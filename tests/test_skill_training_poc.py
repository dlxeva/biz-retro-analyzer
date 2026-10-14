"""Standard-library regression tests for reconstruction Skill PoC (no model calls)."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evaluations" / "skill-training-poc" / "run_poc.py"
spec = importlib.util.spec_from_file_location("biz_reconstruction_poc", SCRIPT)
poc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poc)


class ReconstructionPocTest(unittest.TestCase):
    def test_holdout_six_cases_and_gold(self):
        case_ids = {key for key, _ in poc.cases()}
        gold = json.loads(poc.GOLD.read_text(encoding="utf-8"))
        self.assertEqual(len(case_ids), 6)
        self.assertEqual(case_ids, {item["id"] for item in gold["cases"]})
        for item in gold["cases"]:
            self.assertGreaterEqual(len(item["required"]), 4)
            self.assertGreaterEqual(len(item["forbidden"]), 2)
            self.assertEqual(len({c["id"] for c in item["required"]}),
                             len(item["required"]))
            self.assertEqual(len({c["id"] for c in item["forbidden"]}),
                             len(item["forbidden"]))
            self.assertTrue(all(c["severity"] in ("critical", "major")
                                for c in item["forbidden"]))

    def test_frozen_skill_and_no_gold_leak_in_prompts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "prompts"
            manifest = poc.prepare(["A", "S"], out, {})
            self.assertEqual(len(manifest["inputs"]), 12)
            self.assertEqual(manifest["base_commit"], poc.BASE_COMMIT)
            prompt_a = (out / "A" / "h02-rewritten-commitment.md").read_text(
                encoding="utf-8")
            prompt_s = (out / "S" / "h02-rewritten-commitment.md").read_text(
                encoding="utf-8")
            self.assertNotIn("## Expert checks", prompt_a)
            self.assertNotIn("## Expert checks", prompt_s)
            self.assertNotIn("holdout-gold.json", prompt_a)
            self.assertNotIn("holdout-gold.json", prompt_s)
            self.assertIn("[S05]", prompt_a)
            self.assertIn("Frozen Biz Retro runtime protocol", prompt_s)
            self.assertNotIn("Frozen Biz Retro runtime protocol", prompt_a)

    def test_candidate_delta_is_mandatory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises((ValueError, AttributeError)):
                poc.prepare(["B"], Path(tmp), {})
            with self.assertRaises((ValueError, AttributeError)):
                poc.prepare(["C"], Path(tmp), {})
            with self.assertRaises(ValueError):
                poc.model_prompt("B", "source", "base", "")

    def test_training_pack_generates_templated_material(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            poc.train_pack(out)
            self.assertEqual(len(list(out.glob("B-distill-*.md"))), 6)
            self.assertEqual(len(list(out.glob("C-forward-*.md"))), 6)
            self.assertEqual(len(list(out.glob("C-backward-*.md"))), 6)
            self.assertIn("No model inference", (out / "STATUS.txt").read_text(
                encoding="utf-8"))
            self.assertNotIn("## Expert checks", (out / "C-forward-01.md")
                             .read_text(encoding="utf-8"))
            self.assertIn("## Expert checks", (out / "C-backward-01.md")
                          .read_text(encoding="utf-8"))

    def test_scorer_penalizes_critical_false_positives(self):
        gold = json.loads(poc.GOLD.read_text(encoding="utf-8"))["cases"][0]
        row = {"covered": [x["id"] for x in gold["required"]],
               "violations": [], "supported_claims": 4,
               "unsupported_claims": 0, "valid_anchors": 4,
               "invalid_anchors": 0, "unsupported_high_risk_claims": 0}
        self.assertEqual(poc.score_review(row, gold)["score"], 100)
        row["violations"] = ["f2"]
        self.assertEqual(poc.score_review(row, gold)["score"], 82)
        row["unsupported_claims"] = 1
        row["unsupported_high_risk_claims"] = 1
        self.assertLess(poc.score_review(row, gold)["score"], 70)
        row["covered"] = ["invalid-check"]
        with self.assertRaises(ValueError):
            poc.score_review(row, gold)

    def test_blinded_review_and_scoring(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            cases = poc.cases()
            outputs = tmp / "outputs"
            for arm in ("A", "S"):
                path = outputs / arm / (cases[0][0] + ".md")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("审计输出 for " + arm, encoding="utf-8")
            blind = tmp / "blind"
            mapping = tmp / "private" / "mapping.json"
            self.assertEqual(poc.blind_outputs(outputs, blind, mapping), 2)
            entries = json.loads(mapping.read_text(encoding="utf-8"))
            self.assertEqual(len(entries), 2)
            self.assertEqual(len(list(blind.glob("*.md"))), 2)
            reviews = tmp / "reviews.jsonl"
            gold = json.loads(poc.GOLD.read_text(encoding="utf-8"))["cases"][0]
            data = []
            for ident in entries:
                data.append({"blind_id": ident,
                             "covered": [x["id"] for x in gold["required"]],
                             "violations": [], "supported_claims": 4,
                             "unsupported_claims": 0, "valid_anchors": 4,
                             "invalid_anchors": 0,
                             "unsupported_high_risk_claims": 0})
            reviews.write_text("\n".join(json.dumps(r) for r in data) + "\n",
                               encoding="utf-8")
            result = poc.score_file(reviews, mapping, tmp / "report.json")
            self.assertFalse(result["complete"])
            self.assertFalse(result["four_arm_complete"])
            self.assertEqual(result["summary"]["A"]["mapped"], 1)
            self.assertEqual(result["summary"]["A"]["expected"], 6)
            self.assertEqual(result["summary"]["A"]["mean_score"], 100)
            self.assertEqual(result["summary"]["S"]["mean_score"], 100)


    def test_full_24_report_blind_review_is_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gold = json.loads(poc.GOLD.read_text(encoding="utf-8"))
            outputs = root / "outputs"
            for arm in poc.ARMS:
                for case in gold["cases"]:
                    folder = outputs / arm
                    folder.mkdir(parents=True, exist_ok=True)
                    (folder / (case["id"] + ".md")).write_text(
                        "Synthetic review only", encoding="utf-8")
            mapping = root / "private-mapping.json"
            self.assertEqual(
                poc.blind_outputs(outputs, root / "blind", mapping), 24)
            entries = json.loads(mapping.read_text(encoding="utf-8"))
            by_case = {x["id"]: x for x in gold["cases"]}
            rows = []
            for blind_id, item in entries.items():
                g = by_case[item["case_id"]]
                rows.append({
                    "blind_id": blind_id,
                    "covered": [x["id"] for x in g["required"]],
                    "violations": [], "supported_claims": 5,
                    "unsupported_claims": 0, "valid_anchors": 5,
                    "invalid_anchors": 0, "unsupported_high_risk_claims": 0,
                })
            review = root / "review.jsonl"
            review.write_text(
                "\n".join(json.dumps(x) for x in rows) + "\n",
                encoding="utf-8")
            result = poc.score_file(review, mapping, root / "scores.json")
            self.assertTrue(result["complete"])
            self.assertTrue(result["four_arm_complete"])
            self.assertTrue(all(x["reviewed"] == 6 and x["mapped"] == 6
                                for x in result["summary"].values()))
            with self.assertRaises(ValueError):
                poc.blind_outputs(outputs, root / "blind", root / "new-map.json")


if __name__ == "__main__":
    unittest.main()
