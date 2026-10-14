"""Offline tests of the ACTUAL iterative Biz Retro learning loop (no model/API)."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "evaluations" / "skill-training-poc"
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("biz_train_loop", HERE / "train_loop.py")
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)


class FakeBackend:
    """Deterministic test-double; has no analytical capability."""

    label = "test-double"
    model_id = "fake-smoke-v1"

    def __init__(self):
        self.n_b, self.n_c = 0, 0
        self.prompts = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        if prompt.startswith("# Arm B:"):
            self.n_b += 1
            answer = "## Rule\nB delta step " + str(self.n_b)
        elif prompt.startswith("# Arm C:"):
            self.n_c += 1
            answer = "## Rule\nC delta step " + str(self.n_c)
        else:
            answer = "Synthetic protocol-only response. No professional inference."
        return {"text": answer, "model": self.model_id,
                "input_tokens": 7, "output_tokens": 8}


class IterativeLearningTest(unittest.TestCase):
    def test_new_delta_used_by_following_forward_round(self):
        fake = FakeBackend()
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "train"
            state = loop.train(fake, run, max_cases=2)
            self.assertFalse(state["complete"])
            self.assertEqual(state["calls"], 8)
            names = state["development_cases"]
            first = (run / "cycles" / names[0] / "C-forward.response.md")
            second = (run / "cycles" / names[1] / "C-forward.prompt.md")
            self.assertTrue(first.exists())
            forward_next = second.read_text(encoding="utf-8")
            self.assertIn("C delta step 1", forward_next)
            self.assertNotIn("C delta step 2", forward_next)
            self.assertIn("C delta step 2",
                          (run / "C-delta.md").read_text(encoding="utf-8"))
            self.assertNotIn("Expert checks (revealed AFTER forward)", forward_next)
            self.assertIn("B delta step 2",
                          (run / "cycles" / names[1] / "B-distill.prompt.md")
                          .read_text(encoding="utf-8"))

    def test_complete_training_and_evaluation_isolation(self):
        fake = FakeBackend()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            training = root / "training"
            result = loop.train(fake, training)
            self.assertTrue(result["complete"])
            self.assertEqual(result["calls"], 24)
            self.assertEqual(fake.n_b, 12)
            self.assertEqual(fake.n_c, 6)
            self.assertEqual(result["usage"]["C"]["calls"], 12)
            manifest = json.loads((training / "manifest.json")
                                  .read_text(encoding="utf-8"))
            self.assertEqual(manifest["delta_sha256"]["B"],
                             loop.digest("## Rule\nB delta step 12"))
            out = root / "eval"
            evaluation = loop.evaluate(fake, training, out)
            self.assertTrue(evaluation["complete"])
            self.assertEqual(evaluation["calls"], 24)
            logs = (out / "calls.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(logs), 24)
            self.assertEqual(len(list((out / "outputs").glob("*/*.md"))), 24)
            self.assertEqual(len(list((out / "traces").glob("*/*/*.prompt.md"))), 24)
            sample = (out / "traces" / "C" /
                      "h02-rewritten-commitment" /
                      "eval-C.prompt.md").read_text(encoding="utf-8")
            self.assertIn("C delta step 6", sample)
            self.assertNotIn("Expert checks (revealed AFTER forward)", sample)
            self.assertNotIn("holdout-gold.json", sample)
            self.assertNotIn("## Expert checks", sample)
            self.assertEqual(result["usage"]["B"]["calls"], 12)

    def test_no_change_delta_is_reported_and_evaluated_as_frozen(self):
        class NoChangeBackend(FakeBackend):
            def __call__(self, prompt):
                self.prompts.append(prompt)
                if prompt.startswith("# Arm B:") or prompt.startswith("# Arm C:"):
                    return {"text": "NO_CHANGE", "model": self.model_id}
                return {"text": "No extra rules", "model": self.model_id}
        fake = NoChangeBackend()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            training = root / "training"
            result = loop.train(fake, training)
            self.assertTrue(result["complete"])
            self.assertEqual(result["delta_sha256"]["B"], loop.digest(""))
            evaluation = loop.evaluate(fake, training, root / "eval")
            self.assertEqual(evaluation["no_change_arms"], ["B", "C"])
            p_b = (root / "eval" / "traces" / "B" /
                   "h01-authorized-pilot" / "eval-B.prompt.md").read_text(
                       encoding="utf-8")
            p_s = (root / "eval" / "traces" / "S" /
                   "h01-authorized-pilot" / "eval-S.prompt.md").read_text(
                       encoding="utf-8")
            self.assertEqual(p_b, p_s)

    def test_mismatched_model_or_settings_block_evaluation(self):
        fake = FakeBackend()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            training = root / "training"
            loop.train(fake, training)
            other = FakeBackend()
            other.model_id = "different-model"
            with self.assertRaises(ValueError):
                loop.evaluate(other, training, root / "eval-mismatched")
            other.model_id = fake.model_id
            other.max_output_tokens = 1024
            with self.assertRaises(ValueError):
                loop.evaluate(other, training, root / "eval-settings")
            self.assertFalse((root / "eval-mismatched").exists())
            self.assertFalse((root / "eval-settings").exists())

    def test_external_calls_require_explicit_authorization(self):
        with self.assertRaises(ValueError):
            loop.ChatCompletionsBackend(
                "https://api.example.org/v1/chat/completions",
                "test-model", "OPENAI_API_KEY", False)
        with self.assertRaises(ValueError):
            loop.ChatCompletionsBackend(
                "http://example.org/v1/chat/completions",
                "test-model", "OPENAI_API_KEY", True)

    def test_cap_and_no_change(self):
        self.assertEqual(loop.validate_delta("NO_CHANGE", "prev"), "prev")
        self.assertEqual(loop.validate_delta("updated", "prev"), "updated")
        with self.assertRaises(ValueError):
            loop.validate_delta("x" * 1001, "")
        with self.assertRaises(ValueError):
            loop.validate_delta("secret: holdout-gold.json", "")
        with self.assertRaises(ValueError):
            loop.validate_delta("[PASTE CURRENT DELTA]", "")

    def test_refuse_repository_outputs_and_duplicate_run(self):
        fake = FakeBackend()
        with self.assertRaises(ValueError):
            loop.safe_output_dir(ROOT / "evaluations" / "skill-training-poc" / "temp")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "run"
            p.mkdir()
            (p / "marker.txt").write_text("exists", encoding="utf-8")
            with self.assertRaises(ValueError):
                loop.train(fake, p, max_cases=1)
            self.assertEqual(len(fake.prompts), 0)

    def test_reject_partial_or_tampered_training_deltas(self):
        fake = FakeBackend()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            training = root / "training"
            loop.train(fake, training, max_cases=1)
            with self.assertRaises(ValueError):
                loop.evaluate(fake, training, root / "eval")
        fake = FakeBackend()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            training = root / "training"
            loop.train(fake, training)
            (training / "C-delta.md").write_text("tampered", encoding="utf-8")
            with self.assertRaises(ValueError):
                loop.evaluate(fake, training, root / "eval")


if __name__ == "__main__":
    unittest.main()
