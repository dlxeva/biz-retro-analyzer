"""Tests for scripts/retro_tool.py. Run: python -m unittest discover -s tests -v"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(ROOT / "scripts"))

import retro_tool  # noqa: E402


def run_cli(*argv):
    """Run the CLI in-process; return (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = retro_tool.main([str(a) for a in argv])
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


class TempDirMixin:
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text, encoding="utf-8"):
        path = self.tmp / name
        path.write_bytes(text.encode(encoding))
        return path


class SpeakerLabelTest(unittest.TestCase):
    def test_accepts_names_letters_and_numbered_speakers(self):
        for label in ["A 林伟", "E 周总", "F 欧阳娜娜", "张三", "欧阳娜娜", "主持人", "王总",
                      "发言人1", "说话人 12", "Speaker 3", "John", "Mary Ann", "B"]:
            self.assertTrue(retro_tool.is_speaker_label(label), label)

    def test_rejects_document_labels_and_speech(self):
        for label in ["结论", "备注", "问题", "会议时间", "参会人员", "Summary", "Note",
                      "我觉得是这样", "那这个", "A股这两天跌得厉害"]:
            self.assertFalse(retro_tool.is_speaker_label(label), label)


class ParseTranscriptTest(unittest.TestCase):
    def parse(self, name):
        return retro_tool.parse_transcript(retro_tool.read_text(FIXTURES / name))

    def test_speaker_formats(self):
        parsed = self.parse("speaker-formats.txt")
        speakers = retro_tool.speaker_counts(parsed["turns"])
        self.assertEqual(
            list(speakers),
            ["张三", "李四", "发言人1", "说话人2", "Speaker 3", "John", "主持人", "王建国", "E 周总", "欧阳娜娜"])
        self.assertEqual(speakers["张三"], 2, "full-width and half-width colons are the same speaker")
        for label in ("结论", "备注", "问题", "A股这两天跌得厉害，我们的估值要重谈。", "C 级会员的复购率只有 12%。"):
            self.assertNotIn(label, speakers)

    def test_timestamps_and_continuation_lines(self):
        turns = {t["speaker"]: t for t in self.parse("speaker-formats.txt")["turns"]}
        self.assertEqual(turns["发言人1"]["ts"], "00:01:23")
        self.assertEqual(turns["Speaker 3"]["seconds"], 112)
        self.assertEqual(turns["E 周总"]["ts"], "03:30")
        self.assertIn("最后拍板的人", turns["E 周总"]["text"])
        self.assertIn("飞书妙记格式的内容行", turns["说话人2"]["text"])

    def test_quickstart_transcript(self):
        parsed = retro_tool.parse_transcript(retro_tool.read_text(ROOT / "examples" / "quickstart-transcript.txt"))
        speakers = retro_tool.speaker_counts(parsed["turns"])
        self.assertEqual(sorted(speakers), ["A 林伟", "B 陈昊", "C 周主任", "D 李医生"])
        self.assertEqual(len(parsed["turns"]), 18)
        self.assertEqual(parsed["turns"][0]["ts"], "00:00")
        content = [r for r in parsed["records"] if r["kind"] in ("header", "content")]
        self.assertTrue(all(r["turn"] for r in content))

    def test_noise_is_hint_only(self):
        parsed = self.parse("noise-hints.txt")
        records = parsed["records"]
        key_line = next(r for r in records if "七八个" in r["raw"])
        self.assertEqual(key_line["noise"], "吃饭")
        self.assertEqual(key_line["turn"], "T001", "a noise hint must not detach a line from its speaker")
        self.assertIn("七八个是肯定有的", parsed["turns"][0]["text"])
        self.assertEqual(next(r for r in records if "外卖" in r["raw"])["kind"], "annotation")

    def test_markdown_structure_is_not_speech(self):
        parsed = retro_tool.parse_transcript("# 会议记录\n- 结论：先试点\n| A | B |\n张三：好\n")
        self.assertEqual([t["speaker"] for t in parsed["turns"]], ["张三"])


class PreprocessCliTest(TempDirMixin, unittest.TestCase):
    def test_annotated_output_keeps_every_line(self):
        src = FIXTURES / "noise-hints.txt"
        code, out, err = run_cli("preprocess", src)
        self.assertEqual(code, 0)
        lines = src.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(out.splitlines()), len(lines))
        self.assertIn("[T001 A 高远 @10:05] [NOISE? 吃饭]", out)
        self.assertIn("nothing was removed", err)

    def test_json_output(self):
        code, out, _ = run_cli("preprocess", FIXTURES / "speaker-formats.txt", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["speakers"][0], {"label": "张三", "turns": 2})
        self.assertEqual(data["turns"][2]["ts"], "00:01:23")

    def test_gbk_and_utf16_input(self):
        text = "张三：我们下周一上线。\r\n李四：好的。\r\n"
        for enc in ("gbk", "utf-16", "utf-8-sig"):
            path = self.write("t-%s.txt" % enc, text, enc)
            code, out, _ = run_cli("preprocess", path)
            self.assertEqual(code, 0, enc)
            self.assertIn("[T002 李四]", out, enc)

    def test_output_file_and_missing_input(self):
        target = self.tmp / "out.txt"
        code, out, err = run_cli("preprocess", FIXTURES / "noise-hints.txt", "-o", target)
        self.assertEqual(code, 0)
        self.assertEqual(out, "")
        self.assertTrue(target.read_text(encoding="utf-8").startswith("[T001"))
        code, _, err = run_cli("preprocess", self.tmp / "missing.txt")
        self.assertEqual(code, 2)
        self.assertIn("file not found", err)


GOLD = ROOT / "examples" / "quickstart-output.md"
QUICK_TRANSCRIPT = ROOT / "examples" / "quickstart-transcript.txt"


def lint(text, mode=None, transcript=QUICK_TRANSCRIPT):
    sources = [transcript] if transcript else []
    _, checks = retro_tool.lint_markdown(text, mode, sources)
    return {c["id"]: c for c in checks}


def failing(checks):
    return sorted(cid for cid, c in checks.items() if c["status"] == "FAIL")


def messages(check, severity="FAIL"):
    return [m for s, _, m in check["items"] if s == severity]


class ValidateGoldSampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gold = GOLD.read_text(encoding="utf-8")

    def test_gold_sample_passes_against_its_transcript(self):
        code, out, _ = run_cli("validate", GOLD, "--transcript", QUICK_TRANSCRIPT)
        self.assertEqual(code, 0, out)
        self.assertIn("Result: PASS", out)
        self.assertIn("does not mean the judgments are correct", out)

    def test_gold_sample_json(self):
        code, out, _ = run_cli("validate", GOLD, "-t", QUICK_TRANSCRIPT, "--json")
        data = json.loads(out)
        self.assertEqual((code, data["result"], data["mode"]), (0, "PASS", "B"))
        anchors = next(c for c in data["checks"] if c["id"] == "anchors")
        self.assertIn("timestamp", anchors["info"])

    def test_without_transcript_anchors_are_unverified(self):
        checks = lint(self.gold, transcript=None)
        self.assertEqual(failing(checks), [])
        self.assertEqual(checks["anchors"]["status"], "WARN")

    def test_original_gold_anchor_errors_are_caught(self):
        before = self.gold.replace("Lin Wei, 03:58 (proposal); Director Zhou, 04:15 (agreement)", "Lin Wei, 04:15")
        before = before.replace("Lin Wei 03:58, Director Zhou 04:15", "Lin Wei 04:15")
        before = "\n".join(l for l in before.splitlines() if "interface permission must go through" not in l)
        checks = lint(before)
        self.assertEqual(failing(checks), ["anchors", "gate-anchors"])
        self.assertEqual(len(messages(checks["anchors"])), 2)
        self.assertIn("04:15 is C 周主任 speaking, not A 林伟", messages(checks["anchors"])[0])
        self.assertIn("gatekeeper", messages(checks["gate-anchors"])[0])

    def test_unknown_timestamp_fails(self):
        checks = lint(self.gold.replace("Dr. Li, 00:35", "Dr. Li, 00:36"))
        self.assertIn("timestamp 00:36 does not appear", messages(checks["anchors"])[0])

    def test_wrong_speaker_fails(self):
        checks = lint(self.gold.replace("Dr. Li, 00:35", "Chen Hao, 00:35"))
        self.assertEqual(messages(checks["anchors"]), ["00:35 is D 李医生 speaking, not B 陈昊"])

    def test_fabricated_quote_in_anchor_fails(self):
        text = self.gold.replace("`Source anchor: Director Zhou, 01:28`",
                                 "`Source anchor: Director Zhou 01:28 \u201c备份窗口下个月就取消\u201d`")
        self.assertIn("quote not found", messages(lint(text)["anchors"])[0])

    def test_quote_with_dropped_fillers_resolves(self):
        text = self.gold.replace("`Source anchor: Director Zhou, 01:28`",
                                 "`Source anchor: Director Zhou 01:28 \u201c备份窗口这个事情，信息科是有规定的\u201d`")
        self.assertEqual(lint(text)["anchors"]["status"], "PASS")

    def test_confirmed_motive_without_quote_fails(self):
        text = self.gold.replace(
            "  - `Claim`: Director Zhou is building an exit rationale\n  - `Status`: Assumption",
            "  - `Claim`: Director Zhou's real motive is to exit the pilot\n  - `Status`: Confirmed")
        checks = lint(text)
        self.assertIn("gate-confirmed", failing(checks))
        self.assertIn("gate-anchors", failing(checks))

    def test_later_reasoning_cannot_be_confirmed(self):
        text = self.gold.replace(
            "  - `Status`: Inferred\n  - `Strength`: Medium\n  - `Basis`: Director Zhou's repeated reframing",
            "  - `Status`: Confirmed\n  - `Strength`: Medium\n  - `Basis`: Later reasoning only; Zhou's reframing")
        self.assertEqual(failing(lint(text)), ["later-reasoning"])

    def test_motive_row_without_evidence_fails(self):
        text = self.gold.replace(
            "| Medium | Interrupted twice to refocus on the latency; explicit about colleague pressure |",
            "| Medium |  |")
        self.assertIn("motive readout row has no evidence", messages(lint(text)["gate-anchors"])[0])

    def test_do_now_without_evidence_fails(self):
        text = self.gold.replace(" `Evidence: Lin Wei 03:58, Chen Hao 03:45`", "")
        self.assertEqual(failing(lint(text)), ["actions"])

    def test_missing_map_fails(self):
        start = self.gold.index("### Participant Understanding Map")
        end = self.gold.index("### Judgment and Reverse Audit")
        self.assertIn("sections", failing(lint(self.gold[:start] + self.gold[end:])))
        omitted = self.gold[:start] + "### Participant Understanding Map\n\nParticipant Understanding Map " \
            "omitted due to insufficient participant-level evidence.\n\n" + self.gold[end:]
        self.assertEqual(failing(lint(omitted)), [])


class ValidateTemplatesTest(TempDirMixin, unittest.TestCase):
    def test_empty_scaffolds_fail(self):
        for mode in ("A", "B", "C"):
            code, text, _ = run_cli("scaffold", "--mode", mode)
            self.assertEqual(code, 0)
            checks = lint(text, transcript=None)
            self.assertIn("placeholders", failing(checks), mode)
            self.assertIn("tagged", failing(checks), mode)
            self.assertNotIn("sections", failing(checks), mode)

    def test_keyword_stuffing_does_not_pass(self):
        stuffed = ("# Mode B Output\n\n## Structured Fact Record\n- anchor anchor 来源 锚点 evidence\n"
                   "- `Status`: Confirmed\n\n## Project Thread\n- motive budget anchor\n\n"
                   "## Stakeholder Motive Readout\n\n## Participant Understanding Map\n\n## Current Actions\n"
                   "- **Do now**: evidence 证据\n")
        self.assertGreaterEqual(len(failing(lint(stuffed))), 3)

    def test_cli_writes_scaffold_and_exits_nonzero_on_fail(self):
        target = self.tmp / "template.md"
        run_cli("scaffold", "--mode", "C", "-o", target)
        self.assertIn("## Judgment and Reverse Audit", target.read_text(encoding="utf-8"))
        code, out, _ = run_cli("validate", target)
        self.assertEqual(code, 1)
        self.assertIn("Result: FAIL", out)


class ValidateChineseTest(unittest.TestCase):
    TRANSCRIPT = FIXTURES / "noise-hints.txt"
    DOC = """# Mode A 输出

## 结构化事实记录

- **已确认**：
  - 高远收回了客户数量的说法：“二十几个可能说多了，七八个是肯定有的”。`来源锚点：A 高远 10:05`
  - 苏晴指出 B 端客户周末活跃度下降。`来源锚点：苏晴 10:20`
- **证据备注**：
  - `判断`：高远会前引用的“二十多个客户”缺少记录支撑
  - `状态`：Inferred
  - `强度`：Medium
  - `依据`：Source quote/paraphrase
  - `锚点`：高远 10:05“没有正式记录”
"""

    def test_chinese_fields_and_anchors_pass(self):
        checks = lint(self.DOC, transcript=self.TRANSCRIPT)
        self.assertEqual(failing(checks), [])
        self.assertEqual(checks["tagged"]["status"], "PASS")
        self.assertEqual(checks["anchors"]["status"], "PASS")

    def test_chinese_speaker_mismatch_fails(self):
        checks = lint(self.DOC.replace("苏晴 10:20", "马骏 10:20"), transcript=self.TRANSCRIPT)
        self.assertEqual(messages(checks["anchors"]), ["10:20 is B 苏晴 speaking, not C 马骏"])

    def test_full_width_colon_after_time_is_not_a_timestamp(self):
        doc = self.DOC.replace("`来源锚点：苏晴 10:20`", "`来源锚点：苏晴 10:20：41 家里只有 3 家`")
        self.assertEqual(lint(doc, transcript=self.TRANSCRIPT)["anchors"]["status"], "PASS")


class ExampleSyncTest(unittest.TestCase):
    def test_quickstart_transcript_matches_markdown(self):
        md = (ROOT / "examples" / "quickstart.md").read_text(encoding="utf-8")
        block = md.split("```text\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(block.strip(), QUICK_TRANSCRIPT.read_text(encoding="utf-8").strip())

    def test_gold_output_matches_markdown(self):
        md = (ROOT / "examples" / "quickstart.md").read_text(encoding="utf-8")
        start = md.index("### Structured Fact Record")
        end = md.index("---\n\n## How to verify")
        self.assertEqual(md[start:end].strip(), GOLD.read_text(encoding="utf-8").strip())


QUICK_REPORT = ROOT / "examples" / "quickstart.report.json"
FICTIONAL = ROOT / "examples" / "product-review-fictional"
REPORTS = [QUICK_REPORT, FICTIONAL / "report.json"]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def lint_json(data, base_dir=None, mode=None):
    _, checks = retro_tool.lint_report(data, mode, base_dir)
    return {c["id"]: c for c in checks}


def schema_keywords(node):
    if isinstance(node, dict):
        props = node.get("properties", {})
        defs = node.get("$defs", {})
        for key, value in node.items():
            if value is props or value is defs:
                for sub in value.values():
                    for k in schema_keywords(sub):
                        yield k
                yield key
                continue
            yield key
            for k in schema_keywords(value):
                yield k
    elif isinstance(node, list):
        for item in node:
            for k in schema_keywords(item):
                yield k


class SchemaTest(unittest.TestCase):
    def test_validator_supports_every_keyword_the_schema_uses(self):
        used = set(schema_keywords(retro_tool.load_schema()))
        self.assertEqual(used - retro_tool.SCHEMA_KEYWORDS, set())

    def test_schema_matches_tool_vocabulary(self):
        defs = retro_tool.load_schema()["$defs"]
        self.assertEqual(defs["status"]["enum"], retro_tool.STATUS_VALUES)
        self.assertEqual(defs["strength"]["enum"], retro_tool.STRENGTH_VALUES)
        self.assertEqual(defs["basis"]["enum"], retro_tool.BASIS_VALUES)
        self.assertEqual(defs["understanding"]["properties"]["level"]["enum"], retro_tool.UNDERSTANDING_LEVELS)
        self.assertEqual(retro_tool.load_schema()["properties"]["schemaVersion"]["const"], retro_tool.SCHEMA_VERSION)

    def test_schema_errors_report_paths(self):
        errors = retro_tool.schema_errors({"schemaVersion": "2.0", "meta": {}}, retro_tool.load_schema())
        self.assertIn(("$", "missing required field 'sources'"), errors)
        self.assertTrue(any(p == "$.meta" for p, _ in errors))

    def test_v1_report_is_upgraded_schema_clean(self):
        v1 = {"meta": {"reportTitle": "T", "reportDate": "2026-01-01", "outputMode": "Mode B: Retro Pack",
                       "projectStage": "pilot", "contextNote": "formal meeting"},
              "summary": [{"label": "1", "headline": "h", "body": "b", "status": "Inferred"}],
              "evidenceLayer": [{"title": "Meeting", "status": "Confirmed", "points": ["p1"]}],
              "stakeholders": [{"party": "A", "statedPosition": "s", "apparentMotive": "m", "confidence": "Low"}],
              "understandingMap": [{"party": "A", "domainUnderstanding": "strong: knows it",
                                    "workflowUnderstanding": "mixed", "deliveryUnderstanding": "thin",
                                    "organizationalUnderstanding": "unclear from material"}],
              "audit": {"weakJudgments": ["x is Assumption"]},
              "actions": {"doNow": ["call A"]}}
        data = retro_tool.upgrade_v1(v1)
        self.assertEqual(retro_tool.schema_errors(data, retro_tool.load_schema()), [])
        self.assertEqual(data["meta"]["outputMode"], "B")
        self.assertEqual(data["understandingMap"]["rows"][0]["problem"]["level"], "strong")
        self.assertEqual(data["understandingMap"]["rows"][0]["decisionMechanics"]["level"], "unclear")
        self.assertEqual(data["audit"]["weakJudgments"][0]["status"], "Assumption")


class ValidateReportJsonTest(TempDirMixin, unittest.TestCase):
    def test_examples_pass(self):
        for path in REPORTS:
            code, out, _ = run_cli("validate", path)
            self.assertEqual(code, 0, out)
            self.assertIn("Result: PASS", out)
            self.assertIn("anchor(s) checked against", run_cli("validate", path, "-v")[1])

    def test_json_scaffolds_fail(self):
        for mode in ("A", "B", "C"):
            code, text, _ = run_cli("scaffold", "--mode", mode, "--format", "json")
            self.assertEqual(code, 0)
            checks = lint_json(json.loads(text))
            self.assertIn("placeholders", failing(checks), mode)
            self.assertIn("schema", failing(checks), mode)

    def test_wrong_speaker_and_fabricated_quote_fail(self):
        data = load_json(QUICK_REPORT)
        data["stakeholders"][0]["anchors"] = [{"speaker": "B 陈昊", "ts": "02:10"}]
        data["evidenceLayer"][0]["points"][0]["anchors"] = [{"speaker": "A 林伟", "ts": "02:10",
                                                             "quote": "我们下个月就签合同"}]
        msgs = messages(lint_json(data, QUICK_REPORT.parent)["anchors"])
        self.assertTrue(any("02:10 is A 林伟 speaking, not B 陈昊" in m for m in msgs), msgs)
        self.assertTrue(any("quote not found" in m for m in msgs), msgs)

    def test_unknown_source_and_missing_anchor(self):
        data = load_json(QUICK_REPORT)
        data["actions"]["doNow"][0]["anchors"] = [{"source": "S9", "ts": "02:10"}]
        data["stakeholders"][1]["anchors"] = []
        checks = lint_json(data, QUICK_REPORT.parent)
        self.assertIn("unknown source id 'S9'", messages(checks["anchors"])[0])
        self.assertTrue(any("motive readout" in m for m in messages(checks["gate-anchors"])))

    def test_confirmed_claim_needs_source_layer_and_quote(self):
        data = load_json(FICTIONAL / "report.json")
        u = data["audit"]["weakJudgments"][0]
        u.update(status="Confirmed", highRiskType="motive", basis="Later reasoning only",
                 anchors=[{"source": "C1", "note": "user says so"}])
        checks = lint_json(data, FICTIONAL)
        self.assertIn("later-reasoning", failing(checks))
        self.assertIn("gate-confirmed", failing(checks))
        self.assertIn("gate-anchors", failing(checks))

    def test_source_override_and_missing_path(self):
        data = load_json(QUICK_REPORT)
        target = self.write("report.json", json.dumps(data, ensure_ascii=False))
        code, out, _ = run_cli("validate", target)
        self.assertIn("transcript not found", out, "the transcript path is relative to the JSON file")
        self.assertIn("Result: PASS (0 failing, 1 with warnings", out)
        code, out, _ = run_cli("validate", target, "-s", "S1=%s" % QUICK_TRANSCRIPT)
        self.assertEqual(code, 0, out)


class RenderTest(TempDirMixin, unittest.TestCase):
    @staticmethod
    def html(path, audience=None):
        data = load_json(path)
        indexes, _ = retro_tool.load_source_indexes(data, path.parent)
        return retro_tool.render_html(data, indexes, audience)

    def test_html_has_sections_and_linked_anchors(self):
        page = self.html(FICTIONAL / "report.json")
        for title in ("结构化事实记录", "决策台账", "主张台账", "项目脉络", "推进 / 影响链", "相关方动机解读",
                      "参与者理解地图", "判断与反向审计", "当前行动", "附录"):
            self.assertIn(title, page)
        self.assertIn('href="#t-S1-', page)
        self.assertNotIn("anc bad", page, "every anchor in the example resolves")
        self.assertIn('id="report-data"', page)
        self.assertNotIn("<link", page, "CSS is inlined")

    def test_unresolved_anchor_is_marked(self):
        data = load_json(QUICK_REPORT)
        data["evidenceLayer"][0]["points"][0]["anchors"] = [{"speaker": "A 林伟", "ts": "09:59"}]
        indexes, _ = retro_tool.load_source_indexes(data, QUICK_REPORT.parent)
        self.assertIn("anc bad", retro_tool.render_html(data, indexes))

    def test_markdown_render_passes_markdown_validate(self):
        cases = [(QUICK_REPORT, [QUICK_TRANSCRIPT]),
                 (FICTIONAL / "report.json", [FICTIONAL / "transcript.txt", FICTIONAL / "group-message.txt"])]
        for path, sources in cases:
            data = load_json(path)
            md = retro_tool.render_markdown(data)
            _, checks = retro_tool.lint_markdown(md, data["meta"]["outputMode"], sources)
            self.assertEqual([c["id"] for c in checks if c["status"] == "FAIL"], [], path.name)

    def test_checked_in_renders_are_current(self):
        for path, html in ((QUICK_REPORT, ROOT / "examples" / "quickstart.report.html"),
                           (FICTIONAL / "report.json", FICTIONAL / "report.html")):
            self.assertEqual(html.read_text(encoding="utf-8"), self.html(path),
                             "re-run: python3 scripts/retro_tool.py render %s -o %s" % (path, html))
        self.assertEqual((FICTIONAL / "report.md").read_text(encoding="utf-8"),
                         retro_tool.render_markdown(load_json(FICTIONAL / "report.json")))

    def test_leadership_redaction(self):
        data = load_json(FICTIONAL / "report.json")
        shown, removed = retro_tool.redact(data, "leadership")
        self.assertNotIn("suspiciousActions", shown["audit"])
        self.assertFalse(any(u.get("highRiskType") == "bad_faith"
                             for k in ("supportedJudgments", "weakJudgments", "explicitAssumptions")
                             for u in shown["audit"].get(k, [])))
        self.assertTrue(all(s["apparentMotive"] == "" for s in shown["stakeholders"] if s["status"] != "Confirmed"))
        self.assertIn("suspiciousActions", dict(removed))
        self.assertIn("suspiciousActions", data["audit"], "redaction works on a copy")
        page = self.html(FICTIONAL / "report.json", "leadership")
        self.assertIn("可疑行为分析", page)
        self.assertNotIn("策略性误导", page)

    def test_external_redaction(self):
        shown, removed = retro_tool.redact(load_json(FICTIONAL / "report.json"), "external")
        for key in ("stakeholders", "understandingMap", "influenceChain", "claimLedger", "minutesCheck",
                    "methodNotes"):
            self.assertNotIn(key, shown)
        self.assertTrue(all("path" not in s for s in shown["sources"]))
        for key in ("supportedJudgments", "weakJudgments", "explicitAssumptions"):
            self.assertTrue(all(u["status"] == "Confirmed" for u in shown["audit"].get(key, [])))
        page = self.html(FICTIONAL / "report.json", "external")
        self.assertNotIn('id="appendix"', page)

    def test_cli_render(self):
        target = self.tmp / "out.html"
        code, _, err = run_cli("render", QUICK_REPORT, "-o", target)
        self.assertEqual(code, 0, err)
        self.assertIn("Lin Wei", target.read_text(encoding="utf-8"))
        code, out, _ = run_cli("render", QUICK_REPORT, "--format", "md")
        self.assertEqual(code, 0)
        self.assertIn("## Participant Understanding Map", out)
        broken = self.write("broken.json", json.dumps({"schemaVersion": "2.0", "meta": {}}))
        code, _, err = run_cli("render", broken)
        self.assertEqual(code, 1)
        self.assertIn("does not match the schema", err)


class NamingTest(unittest.TestCase):
    """Section names and table columns are the same in SKILL.md, templates, scaffold and render."""

    def test_section_titles_everywhere(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        templates = (ROOT / "references" / "output-templates.md").read_text(encoding="utf-8")
        scaffold = run_cli("scaffold", "--mode", "C")[1]
        rendered = retro_tool.render_markdown(load_json(FICTIONAL / "report.json"))
        for key, title in retro_tool.SECTION_TITLES.items():
            for name, text in (("SKILL.md", skill), ("output-templates.md", templates)):
                self.assertIn("## " + title, text, "%s missing in %s" % (title, name))
            if key != "method":
                self.assertIn("## " + title, scaffold, title)
            self.assertIn("## " + title, rendered, title)
        self.assertNotIn("## Project Retro", skill)

    def test_table_columns_everywhere(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        templates = (ROOT / "references" / "output-templates.md").read_text(encoding="utf-8")
        scaffold = run_cli("scaffold", "--mode", "C")[1]
        rendered = retro_tool.render_markdown(load_json(FICTIONAL / "report.json"))
        for columns in (retro_tool.CHAIN_COLUMNS, retro_tool.MOTIVE_COLUMNS, retro_tool.MAP_COLUMNS):
            row = " | ".join(columns)
            for name, text in (("SKILL.md", skill), ("output-templates.md", templates), ("scaffold", scaffold)):
                self.assertIn(row, text, name)
        for columns in (retro_tool.DECISION_COLUMNS, retro_tool.MINUTES_COLUMNS, retro_tool.CLAIM_COLUMNS):
            self.assertIn(" | ".join(columns), templates)
            self.assertIn(" | ".join(columns), rendered)
        self.assertIn(" | ".join(["Party / Voice"] + [c for _, c, _ in retro_tool.MAP_DIMENSIONS]), rendered)

    def test_html_template_uses_canonical_map_columns(self):
        template = (ROOT / "assets" / "html-report-template.html").read_text(encoding="utf-8")
        for _, _, label in retro_tool.MAP_DIMENSIONS:
            self.assertIn("<th>%s</th>" % label, template)
        self.assertIn("scripts/retro_tool.py render", template)


if __name__ == "__main__":
    unittest.main()
