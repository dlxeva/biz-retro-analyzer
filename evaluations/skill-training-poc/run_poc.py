#!/usr/bin/env python3
"""Reconstruction Skill PoC for Biz Retro. Pure-stdlib, no model calls.

This script prepares isolated prompt packs and scores HUMAN-reviewed outputs.
It never reads the hidden answer key when preparing model inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import shutil
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
HOLDOUT = HERE / "holdout"
GOLD = HERE / "holdout-gold.json"
ARMS = ("A", "S", "B", "C")
# For Mode C: keep the same frozen runtime knowledge for S, B and C.
RUNTIME_FILES = (
    "SKILL.md",
    "references/input-modes.md",
    "references/output-templates.md",
    "references/analysis-checks.md",
    "references/reverse-audit.md",
    "references/failure-modes.md",
    "references/honest-limits.md",
)
BASE_COMMIT = "bbd2c41379cf8b0d4a492d9c209ba3ff07ead3ca"
BASE_SKILL_BLOB = "284a4096c8df4a08b3a367794126f1e8989a473d"

BASE_INSTRUCTION = """You are reviewing a business meeting and its follow-up materials.
Identify what was actually authorized, changes between sources, unresolved
risks and evidence-backed next actions. Quote source line anchors for material
claims. Express uncertainty and avoid unsupported motive allegations.
Produce a practical report in Chinese, with the facts and judgments separated."""

TASK = """Analyze ONLY the source material below. Use evidence anchors [S01] etc.
Do not look up files, read repo documents, or infer hidden answers. Highlight
decisions and their authorization limits, unsupported assertions and possible
false positives. Every high-risk claim needs a direct source anchor.
Use the model-visible material only; keep unknowns unknown."""


def cases() -> list[tuple[str, str]]:
    result = [(p.stem, p.read_text(encoding="utf-8")) for p in sorted(HOLDOUT.glob("h*.md"))]
    if len(result) != 6 or len({key for key, _ in result}) != 6:
        raise ValueError("Expected exactly six distinct holdout case inputs")
    return result


def skill_bundle() -> tuple[str, str]:
    content = []
    for rel in RUNTIME_FILES:
        part = (ROOT / rel).read_text(encoding="utf-8")
        content.append("### " + rel + "\n" + part)
    bundle = "\n\n".join(content)
    original = (ROOT / "SKILL.md").read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(original)).encode() + b"\0" + original).hexdigest()
    if blob != BASE_SKILL_BLOB:
        raise ValueError("Frozen SKILL.md changed: stop and update protocol explicitly")
    return bundle, hashlib.sha256(bundle.encode()).hexdigest()


def model_prompt(arm: str, source: str, bundle: str, delta: str = "") -> str:
    if arm not in ARMS:
        raise ValueError("Unknown arm")
    method = BASE_INSTRUCTION if arm == "A" else (
        "Frozen Biz Retro runtime protocol follows.\n\n" + bundle
    )
    if arm in ("B", "C"):
        if not delta.strip():
            raise ValueError("B/C requires a learned delta file")
        method += "\n\n### Experimental skill delta\n" + delta
        method += ("\n\nThe frozen evidence and ethics protocol wins over any conflict "
                   "with this candidate delta.")
    return (
        "# Isolated model input\n\n" + method + "\n\n## Task\n\n" + TASK
        + "\n\n## Source\n\n" + source + "\n"
    )


def prepare(arms: list[str], out: Path, deltas: dict[str, Path]) -> dict:
    case_items = cases()
    if any(a not in ARMS for a in arms):
        raise ValueError("Unknown arm")
    bundle, bundle_hash = skill_bundle() if any(a != "A" for a in arms) else ("", "")
    delta_text = {}
    for a in arms:
        if a in ("B", "C"):
            if a not in deltas or not deltas[a].is_file():
                raise ValueError(f"Arm {a} needs an existing --delta-{a.lower()} file")
            delta_text[a] = deltas[a].read_text(encoding="utf-8")
            if not delta_text[a].strip():
                raise ValueError(f"Empty delta for {a}")
    manifest = {"study": "biz-skill-training-poc-v0", "base_commit": BASE_COMMIT,
                "bundle_sha256": bundle_hash, "arms": arms,
                "case_ids": [key for key, _ in case_items], "inputs": []}
    for a in arms:
        folder = out / a
        folder.mkdir(parents=True, exist_ok=True)
        for case_id, source in case_items:
            body = model_prompt(a, source, bundle, delta_text.get(a, ""))
            target = folder / (case_id + ".md")
            target.write_text(body, encoding="utf-8")
            manifest["inputs"].append({"arm": a, "case_id": case_id,
                "sha256": hashlib.sha256(body.encode()).hexdigest()})
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def train_pack(out: Path) -> None:
    """Create training requests; users run models and store their actual outputs."""
    bundle, _ = skill_bundle()
    dev = sorted((ROOT / "tests/cases").glob("case-*"))
    if len(dev) != 6:
        raise ValueError("Training seed requires six existing development cases")
    out.mkdir(parents=True, exist_ok=True)
    for i, path in enumerate(dev, 1):
        inp = (path / "input.md").read_text(encoding="utf-8")
        checks = (path / "expected-checks.md").read_text(encoding="utf-8")
        (out / f"B-distill-{i:02d}.md").write_text(
            "# Direct distillation\n\nRead this labeled expert audit case. Update the "
            "candidate Skill delta, maximum 1000 Chinese characters. Extract ONLY "
            "transferable decision rules and avoid case-specific facts. "
            "Use a fresh candidate delta on the first round, then revise it in "
            "subsequent rounds. Do not change frozen Biz Retro rules.\n\n"
            "## Case source\n" + inp + "\n## Expert checks\n" + checks
            + "\n## Current delta\n[PASTE PREVIOUS B DELTA HERE]\n", encoding="utf-8")
        (out / f"C-forward-{i:02d}.md").write_text(
            model_prompt("S", inp, bundle), encoding="utf-8")
        (out / f"C-backward-{i:02d}.md").write_text(
            "# Reconstruction feedback\n\nCompare this agent reconstruction with "
            "the expert checks. Identify specific, verifiable decision mistakes; "
            "write a minimal reusable Skill delta, maximum 1000 Chinese characters. "
            "Keep the previous delta except when the new evidence requires correction; "
            "do not memorize case-specific entities. Do not weaken high-risk-claim gates.\n\n"
            "## Source\n" + inp + "\n## Expert checks\n" + checks
            + "\n## Actual preceding reconstruction\n[PASTE C-FORWARD OUTPUT HERE]\n"
            + "\n## Current delta\n[PASTE PREVIOUS C DELTA HERE]\n", encoding="utf-8")
    (out / "STATUS.txt").write_text(
        "Prepared ONLY. No model inference or training has been executed.\n"
        "B and C use the same development cases and frozen base. "
        "C requires real forward outputs before backward updates. "
        "Record tokens/cost and never reveal holdout gold.\n", encoding="utf-8")


def blind_outputs(outputs: Path, blind_dir: Path, mapping_path: Path) -> int:
    if mapping_path.resolve().is_relative_to(blind_dir.resolve()):
        raise ValueError("Mapping must be outside the reviewer-visible blind directory")
    expected = {key for key, _ in cases()}
    found = []
    for a in ARMS:
        d = outputs / a
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            if p.stem not in expected:
                raise ValueError(f"Unknown case: {p}")
            found.append((a, p))
    if not found:
        raise ValueError("No output files to blind")
    blind_dir.mkdir(parents=True, exist_ok=True)
    mapping = {}
    for a, p in found:
        token = secrets.token_hex(6)
        blind_id = p.stem + "-" + token
        shutil.copy2(p, blind_dir / (blind_id + ".md"))
        mapping[blind_id] = {"arm": a, "case_id": p.stem}
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(found)


def score_review(row: dict, gold_case: dict) -> dict:
    required = {x["id"] for x in gold_case["required"]}
    prohibited = {x["id"]: x["severity"] for x in gold_case["forbidden"]}
    hit = set(row["covered"])
    bad = set(row["violations"])
    if len(hit) != len(row["covered"]) or not hit <= required:
        raise ValueError("Invalid/duplicate required check IDs")
    if len(bad) != len(row["violations"]) or not bad <= set(prohibited):
        raise ValueError("Invalid/duplicate forbidden check IDs")
    counts = [row[key] for key in ("supported_claims", "unsupported_claims",
               "valid_anchors", "invalid_anchors", "unsupported_high_risk_claims")]
    if any(type(x) is not int or x < 0 for x in counts):
        raise ValueError("Counts must be non-negative integers")
    supported, unsupported, valid, invalid, high_risk = counts
    if high_risk > unsupported:
        raise ValueError("Unsupported high-risk claims must be included in unsupported")
    recall = len(hit) / len(required)
    precision = supported / (supported + unsupported) if (supported + unsupported) else 0
    anchor_precision = valid / (valid + invalid) if (valid + invalid) else 0
    penalty = sum(18 if prohibited[x] == "critical" else 8 for x in bad) + 12 * high_risk
    score = max(0.0, round(100 * (.60 * recall + .30 * precision
                                 + .10 * anchor_precision) - penalty, 2))
    return {"recall": round(recall, 4), "precision": round(precision, 4),
            "anchor_precision": round(anchor_precision, 4),
            "false_positive_checks": len(bad), "score": score}


def score_file(reviews: Path, mapping_path: Path, output: Path) -> dict:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    by_case = {c["id"]: c for c in gold["cases"]}
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    rows, seen = [], set()
    for raw in reviews.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        row = json.loads(raw)
        blind_id = row["blind_id"]
        if blind_id in seen or blind_id not in mapping:
            raise ValueError("Unknown or duplicated blind_id")
        seen.add(blind_id)
        item = mapping[blind_id]
        metrics = score_review(row, by_case[item["case_id"]])
        rows.append({"blind_id": blind_id, **item, **metrics})
    arms = sorted({v["arm"] for v in mapping.values()})
    summary = {}
    for a in arms:
        group = [r for r in rows if r["arm"] == a]
        expected = sum(v["arm"] == a for v in mapping.values())
        summary[a] = {
            "reviewed": len(group), "expected": expected,
            "complete": len(group) == expected,
            "mean_score": round(statistics.mean(r["score"] for r in group), 2)
                          if group else None,
            "mean_recall": round(statistics.mean(r["recall"] for r in group), 4)
                           if group else None,
            "false_positive_checks": sum(r["false_positive_checks"] for r in group),
        }
    result = {"study": "biz-skill-training-poc-v0", "scoring": "human-annotated",
              "caveat": "Exploratory synthetic-case scores, not proof of generalization.",
              "complete": bool(summary) and all(v["complete"] for v in summary.values()),
              "summary": summary, "cases": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    x = sub.add_parser("prepare", help="Create prompts; NO API/model calls")
    x.add_argument("--arms", default="A,S")
    x.add_argument("--out", type=Path, required=True)
    x.add_argument("--delta-b", type=Path)
    x.add_argument("--delta-c", type=Path)
    x = sub.add_parser("train-pack", help="Create direct-distill/forward/backward templates")
    x.add_argument("--out", type=Path, required=True)
    x = sub.add_parser("blind", help="Blind completed model outputs for review")
    x.add_argument("--outputs", type=Path, required=True)
    x.add_argument("--blind-dir", type=Path, required=True)
    x.add_argument("--mapping", type=Path, required=True)
    x = sub.add_parser("score", help="Score human-reviewed blind outputs")
    x.add_argument("--reviews", type=Path, required=True)
    x.add_argument("--mapping", type=Path, required=True)
    x.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if args.cmd == "prepare":
        arms = [x.strip().upper() for x in args.arms.split(",")]
        deltas = {"B": args.delta_b, "C": args.delta_c}
        print(json.dumps(prepare(arms, args.out, deltas),
                         ensure_ascii=False, indent=2))
    elif args.cmd == "train-pack":
        train_pack(args.out)
        print(f"Prepared training prompts in {args.out}; no model was run")
    elif args.cmd == "blind":
        n = blind_outputs(args.outputs, args.blind_dir, args.mapping)
        print(f"Blinded {n} outputs; mapping kept at {args.mapping}")
    elif args.cmd == "score":
        print(json.dumps(score_file(args.reviews, args.mapping, args.out),
                         ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
