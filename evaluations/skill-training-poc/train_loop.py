#!/usr/bin/env python3
"""Explicit, isolated Biz Retro skill-learning experiment.

Only --provider command or --provider chat-completions performs inference.
No default API calls, no Codex integration. Python 3.8+ / standard library.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import shlex
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

import run_poc as poc

ROOT = poc.ROOT
STUDY = "biz-reconstruction-learning-v1"
MAX_DELTA_CHARS = 1000


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def safe_output_dir(path: Path) -> Path:
    if within(path, ROOT):
        raise ValueError("Experiment outputs must stay outside the git repository")
    if path.exists() and any(path.iterdir()):
        raise ValueError("Output directory already contains files; start a new run")
    path.mkdir(parents=True, exist_ok=True)
    return path


def developer_cases() -> list[tuple[str, str, str]]:
    items = []
    for folder in sorted((ROOT / "tests" / "cases").glob("case-*")):
        source = (folder / "input.md").read_text(encoding="utf-8")
        checks = (folder / "expected-checks.md").read_text(encoding="utf-8")
        items.append((folder.name, source, checks))
    if len(items) != 6:
        raise ValueError("Expected exactly six development cases")
    return items


def validate_delta(answer: str, previous: str, cap: int = MAX_DELTA_CHARS) -> str:
    answer = answer.strip()
    if answer == "NO_CHANGE":
        return previous
    fence = chr(96) * 3
    if answer.startswith(fence):
        lines = answer.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == fence:
            answer = "\n".join(lines[1:-1]).strip()
    if not answer or len(answer) > cap:
        raise ValueError("Delta empty or exceeds character cap")
    if "[PASTE " in answer or "holdout-gold" in answer:
        raise ValueError("Delta contains placeholder or test-answer reference")
    return answer


def distill_prompt(source: str, checks: str, bundle: str, previous: str) -> str:
    return (
        "# Arm B: direct expert-rule distillation\n"
        "Extract transferable rules from this labeled development case. "
        "Do not repeat existing rules or memorize names. Preserve all frozen "
        "evidence and ethics safeguards. Return ONLY the COMPLETE updated "
        "Skill delta in plain Markdown (maximum 1000 characters), or NO_CHANGE.\n\n"
        "## Frozen Skill\n" + bundle
        + "\n\n## Previous B delta\n" + (previous or "(empty)")
        + "\n\n## Development source\n" + source
        + "\n\n## Expert checks\n" + checks
    )


def refine_distill_prompt(source: str, checks: str, bundle: str,
                          previous: str, draft: str) -> str:
    """Budget-matched second pass for B, without any reconstruction."""
    return (
        "# Arm B: direct-rule refinement (second call)\n"
        "Review the proposed delta solely against the labeled expert example "
        "and frozen Skill. Remove redundancy and over-specific rules. "
        "This is still direct knowledge distillation; you have no agent "
        "reconstruction to inspect. Return ONLY the COMPLETE updated Skill "
        "delta (maximum 1000 characters) or NO_CHANGE.\n\n"
        "## Frozen Skill\n" + bundle
        + "\n\n## Previous accepted B delta\n" + (previous or "(empty)")
        + "\n\n## First-pass draft delta\n" + (draft or "(empty)")
        + "\n\n## Development source\n" + source
        + "\n\n## Expert checks\n" + checks
    )


def reconstruct_forward_prompt(source: str, bundle: str, previous: str) -> str:
    # CRITICAL: later rounds use the previous C delta, not just frozen S.
    arm = "C" if previous.strip() else "S"
    return poc.model_prompt(arm, source, bundle, previous)


def reconstruct_backward_prompt(source: str, checks: str, forward: str,
                                bundle: str, previous: str) -> str:
    return (
        "# Arm C: reconstruction-driven skill revision\n"
        "Compare the ACTUAL agent reconstruction with the expert checklist. "
        "Identify missed or overclaimed judgments; generalize minimal, "
        "transferable improvements. Preserve all frozen evidence and "
        "ethics safeguards. Return ONLY the COMPLETE updated Skill delta "
        "in plain Markdown (maximum 1000 characters), or NO_CHANGE. "
        "Never memorize case-specific names or facts.\n\n"
        "## Frozen Skill\n" + bundle
        + "\n\n## Previous C delta\n" + (previous or "(empty)")
        + "\n\n## Development source\n" + source
        + "\n\n## Actual forward reconstruction\n" + forward
        + "\n\n## Expert checks (revealed AFTER forward)\n" + checks
    )


class CommandBackend:
    """User-selected model executable: stdin prompt, stdout response."""

    label = "command"

    def __init__(self, command: str, model_id: str, timeout: int = 180):
        self.argv = shlex.split(command)
        if not self.argv:
            raise ValueError("Empty model command")
        self.model_id, self.timeout = model_id, timeout

    def __call__(self, prompt: str) -> dict:
        # shell=False, fresh empty cwd; command must be user-trusted.
        with tempfile.TemporaryDirectory(prefix="biz-model-") as cwd:
            result = subprocess.run(self.argv, input=prompt, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    cwd=cwd, timeout=self.timeout, check=False)
        if result.returncode:
            # Do not echo stderr; clients sometimes include API credentials there.
            raise RuntimeError("Model command failed with nonzero exit status")
        return {"text": result.stdout.strip(), "model": self.model_id,
                "input_tokens": None, "output_tokens": None}


class ChatCompletionsBackend:
    """One independent HTTP chat-completion per call, explicit spend opt-in."""

    label = "chat-completions"

    def __init__(self, endpoint: str, model_id: str, key_env: str,
                 authorized: bool, timeout: int = 180,
                 max_output_tokens: int = 3000):
        if not authorized:
            raise ValueError("API inference requires --authorize-api-spend")
        parsed = urllib.parse.urlparse(endpoint)
        localhost = parsed.hostname in ("127.0.0.1", "localhost", "::1")
        if parsed.scheme != "https" and not (parsed.scheme == "http" and localhost):
            raise ValueError("Endpoint must be HTTPS except localhost")
        if not parsed.hostname or not parsed.path.endswith("/chat/completions"):
            raise ValueError("Use the full /chat/completions endpoint")
        token = os.environ.get(key_env, "")
        if not token and not localhost:
            raise ValueError("API key environment variable unavailable: " + key_env)
        self.endpoint, self.model_id, self.token = endpoint, model_id, token
        self.timeout = timeout
        if max_output_tokens < 1:
            raise ValueError("max_output_tokens must be positive")
        self.max_output_tokens = max_output_tokens

    def __call__(self, prompt: str) -> dict:
        payload = json.dumps({
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0, "stream": False,
            "max_tokens": self.max_output_tokens,
        }).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        req = urllib.request.Request(self.endpoint, data=payload,
                                     headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as f:
                response = json.loads(f.read(5_000_000).decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError("Model API failed with HTTP " + str(e.code)) from None
        message = response["choices"][0]["message"]["content"]
        if not isinstance(message, str):
            raise ValueError("Expected a text completion")
        usage = response.get("usage") or {}
        return {"text": message.strip(),
                "model": response.get("model", self.model_id),
                "input_tokens": usage.get("prompt_tokens"),
                "output_tokens": usage.get("completion_tokens")}


def record_call(backend: Callable[[str], dict], prompt: str, stage: str,
                case_id: str, folder: Path, log: Path) -> str:
    if not prompt.strip():
        raise ValueError("Empty prompt")
    artifact = folder / case_id
    artifact.mkdir(parents=True, exist_ok=True)
    prefix = stage.replace(".", "-")
    (artifact / (prefix + ".prompt.md")).write_text(prompt, encoding="utf-8")
    reply = backend(prompt)
    if not isinstance(reply, dict) or not isinstance(reply.get("text"), str):
        raise ValueError("Backend must return a dict containing text")
    answer = reply["text"].strip()
    if not answer:
        raise ValueError("Empty model response")
    (artifact / (prefix + ".response.md")).write_text(answer + "\n",
                                                      encoding="utf-8")
    event = {
        "stage": stage, "case_id": case_id,
        "prompt_sha256": digest(prompt), "response_sha256": digest(answer),
        "model": reply.get("model"),
        "backend": getattr(backend, "label", "test-double"),
        "input_tokens": reply.get("input_tokens"),
        "output_tokens": reply.get("output_tokens"),
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    with log.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(event, ensure_ascii=False) + "\n")
    return answer


def summarize_usage(log: Path) -> dict:
    """Never substitute zero for missing usage data (local command provider)."""
    summary = {}
    for line in log.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        arm = event["stage"].split(".")[0]
        stats = summary.setdefault(arm, {
            "calls": 0, "calls_with_token_usage": 0,
            "input_tokens_reported": 0, "output_tokens_reported": 0,
        })
        stats["calls"] += 1
        i, o = event.get("input_tokens"), event.get("output_tokens")
        if isinstance(i, int) and isinstance(o, int):
            stats["calls_with_token_usage"] += 1
            stats["input_tokens_reported"] += i
            stats["output_tokens_reported"] += o
    return summary


def train(backend: Callable[[str], dict], out: Path, max_cases: int = 6) -> dict:
    if max_cases < 1 or max_cases > 6:
        raise ValueError("max_cases must be in 1..6")
    bundle, bundle_hash = poc.skill_bundle()  # immutable baseline first
    dev = developer_cases()[:max_cases]
    out = safe_output_dir(out)
    (out / "cycles").mkdir()
    log = out / "calls.jsonl"
    state = {
        "study": STUDY, "mode": "training", "base_commit": poc.BASE_COMMIT,
        "bundle_sha256": bundle_hash,
        "development_cases": [x[0] for x in dev], "complete": False,
        "backend": getattr(backend, "label", "test-double"),
        "model": getattr(backend, "model_id", "test-double"),
        "warning": "Old development cases previously influenced the frozen Skill.",
    }
    (out / "manifest.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    b_delta, c_delta = "", ""
    for case_id, source, checks in dev:
        b_reply = record_call(
            backend, distill_prompt(source, checks, bundle, b_delta),
            "B.distill", case_id, out / "cycles", log)
        b_draft = validate_delta(b_reply, b_delta)
        b_review = record_call(
            backend, refine_distill_prompt(source, checks, bundle,
                                           b_delta, b_draft),
            "B.refine", case_id, out / "cycles", log)
        b_delta = validate_delta(b_review, b_draft)
        forward = record_call(
            backend, reconstruct_forward_prompt(source, bundle, c_delta),
            "C.forward", case_id, out / "cycles", log)
        c_reply = record_call(
            backend, reconstruct_backward_prompt(
                source, checks, forward, bundle, c_delta),
            "C.backward", case_id, out / "cycles", log)
        c_delta = validate_delta(c_reply, c_delta)
        for arm, delta in (("B", b_delta), ("C", c_delta)):
            (out / "cycles" / case_id / (arm + "-delta.md")).write_text(
                delta + "\n", encoding="utf-8")
    (out / "B-delta.md").write_text(b_delta + "\n", encoding="utf-8")
    (out / "C-delta.md").write_text(c_delta + "\n", encoding="utf-8")
    state["complete"] = max_cases == 6
    state["calls"] = max_cases * 4
    state["usage"] = summarize_usage(log)
    state["delta_sha256"] = {"B": digest(b_delta), "C": digest(c_delta)}
    (out / "manifest.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def evaluate(backend: Callable[[str], dict], training_dir: Path,
             out: Path, arms: tuple[str, ...] = poc.ARMS) -> dict:
    bundle, bundle_hash = poc.skill_bundle()
    prior = json.loads((training_dir / "manifest.json").read_text(encoding="utf-8"))
    if prior.get("study") != STUDY or not prior.get("complete"):
        raise ValueError("Evaluation requires a completed six-case training run")
    if prior.get("base_commit") != poc.BASE_COMMIT or prior.get("bundle_sha256") != bundle_hash:
        raise ValueError("Frozen baseline changed between training and evaluation")
    if not arms or not set(arms) <= set(poc.ARMS) or len(set(arms)) != len(arms):
        raise ValueError("Invalid / duplicate experiment arms")
    deltas = {}
    for arm in ("B", "C"):
        data = (training_dir / (arm + "-delta.md")).read_text(encoding="utf-8").strip()
        if digest(data) != prior["delta_sha256"][arm]:
            raise ValueError("Learned delta changed after training")
        deltas[arm] = data
    out = safe_output_dir(out)
    (out / "outputs").mkdir()
    log = out / "calls.jsonl"
    holdout = poc.cases()
    state = {
        "study": STUDY, "mode": "evaluation", "base_commit": poc.BASE_COMMIT,
        "bundle_sha256": bundle_hash, "delta_sha256": prior["delta_sha256"],
        "arms": list(arms), "case_ids": [x[0] for x in holdout],
        "backend": getattr(backend, "label", "test-double"),
        "model": getattr(backend, "model_id", "test-double"),
        "no_change_arms": [a for a in ("B", "C") if not deltas[a]],
        "complete": False,
        "warning": "Blinded human review required; no performance conclusion yet.",
    }
    (out / "manifest.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for arm in arms:
        for case_id, source in holdout:
            # A genuinely empty delta is a no-change result: run S unmodified,
            # but keep the arm labeled B/C for honest paired evaluation.
            effective_arm = "S" if arm in ("B", "C") and not deltas[arm] else arm
            prompt = poc.model_prompt(effective_arm, source, bundle,
                                      deltas.get(arm, ""))
            answer = record_call(backend, prompt, "eval." + arm, case_id,
                                 out / "traces" / arm, log)
            folder = out / "outputs" / arm
            folder.mkdir(parents=True, exist_ok=True)
            (folder / (case_id + ".md")).write_text(answer + "\n",
                                                    encoding="utf-8")
    state["complete"], state["calls"] = True, len(arms) * len(holdout)
    state["usage"] = summarize_usage(log)
    (out / "manifest.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def cli() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("train", "eval"))
    p.add_argument("--provider", choices=("command", "chat-completions"),
                   required=True)
    p.add_argument("--model", required=True, help="Model name and pinned version")
    p.add_argument("--command", help="Trusted local process: stdin prompt, stdout text")
    p.add_argument("--endpoint", help="Full https://.../chat/completions URL")
    p.add_argument("--api-key-env", default="OPENAI_API_KEY")
    p.add_argument("--max-api-calls", type=int, default=0,
                   help="Required API call budget: >=24 full training, >=24 full evaluation")
    p.add_argument("--max-output-tokens", type=int, default=3000,
                   help="Per-call max_tokens for Chat Completions")
    p.add_argument("--authorize-api-spend", action="store_true",
                   help="Explicit permission for potentially billed API calls")
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-cases", type=int, default=6)
    p.add_argument("--training-dir", type=Path)
    p.add_argument("--arms", default="A,S,B,C")
    args = p.parse_args()
    if args.timeout < 1 or args.max_output_tokens < 1:
        p.error("Timeout and token limit must be positive")
    requested_arms = tuple(x.strip().upper() for x in args.arms.split(","))
    planned_calls = (args.max_cases * 4 if args.action == "train"
                     else len(requested_arms) * len(poc.cases()))
    if args.provider == "chat-completions" and args.max_api_calls < planned_calls:
        p.error("Set --max-api-calls to at least " + str(planned_calls)
                + " for this explicitly authorized run")
    if args.provider == "command":
        if not args.command:
            p.error("--command required for local-command provider")
        backend = CommandBackend(args.command, args.model, args.timeout)
    else:
        if not args.endpoint:
            p.error("--endpoint required for chat-completions")
        backend = ChatCompletionsBackend(
            args.endpoint, args.model, args.api_key_env,
            args.authorize_api_spend, args.timeout, args.max_output_tokens)
    if args.action == "train":
        result = train(backend, args.out, max_cases=args.max_cases)
    else:
        if not args.training_dir:
            p.error("--training-dir required for evaluation")
        result = evaluate(backend, args.training_dir, args.out,
                          arms=requested_arms)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    cli()
