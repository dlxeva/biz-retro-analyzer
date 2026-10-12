"""Tests for scripts/retro_tool.py. Run: python -m unittest discover -s tests -v"""

import contextlib
import io
import json
import os
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


class ExampleSyncTest(unittest.TestCase):
    def test_quickstart_transcript_matches_markdown(self):
        md = (ROOT / "examples" / "quickstart.md").read_text(encoding="utf-8")
        block = md.split("```text\n", 1)[1].split("\n```", 1)[0]
        transcript = (ROOT / "examples" / "quickstart-transcript.txt").read_text(encoding="utf-8")
        self.assertEqual(block.strip(), transcript.strip())


if __name__ == "__main__":
    unittest.main()
