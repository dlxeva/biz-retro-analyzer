#!/usr/bin/env python3
"""biz-retro-analyzer CLI: transcript preprocessing, output scaffolding, protocol validation.

Zero dependencies, Python 3.8+.
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

VERSION = "1.1.0"

VALID_STATUS = {"Confirmed", "Inferred", "Assumption", "Needs validation"}
VALID_STRENGTH = {"High", "Medium", "Low"}

# 高风险声明关键词——validate 检查这些词附近是否有 Source anchor
HIGH_RISK_KEYWORDS = [
    "motive", "intent", "budget", "pricing", "leverage", "political",
    "controls the", "bad faith", "hidden agenda",
    "动机", "真实意图", "预算", "定价", "控制", "恶意",
]


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def read_text(path):
    """Read a text file as UTF-8 (with or without BOM), UTF-16 (BOM) or GB18030."""
    data = Path(path).read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise SystemExit(f"error: cannot decode {path} as UTF-8, UTF-16 or GB18030")


def _setup_console():
    # Windows consoles default to a legacy code page; never crash on output.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def _write_output(text, output):
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


# ---------------------------------------------------------------------------
# Transcript parsing
# ---------------------------------------------------------------------------

TS = r"\d{1,2}:\d{2}(?::\d{2})?"
TS_RE = re.compile(r"(?<![\d:])(" + TS + r")(?![\d:])")
CJK = "\u4e00-\u9fff"

# Line prefixes that look like "label：" but are document structure, not speakers.
NON_SPEAKER_LABELS = {
    "结论", "备注", "问题", "说明", "注", "注意", "注释", "附注", "提示", "议题", "主题", "标题",
    "时间", "日期", "地点", "会议时间", "会议地点", "会议主题", "会议记录注", "记录注", "记录人",
    "参会人员", "参会人", "与会人员", "出席", "列席", "原因", "总结", "小结", "背景", "目标", "结果",
    "决定", "决议", "待办", "行动项", "下一步", "风险", "例如", "比如", "例", "补充", "答案", "回答",
    "提问", "要点", "重点", "摘要", "纪要", "来源", "链接", "地址", "电话", "邮箱", "价格", "报价",
    "预算", "状态", "优先级", "负责人", "截止", "原文", "引用", "首先", "其次", "最后", "另外",
    "第一", "第二", "第三", "第四", "第五", "上午", "下午", "晚上", "今天", "明天", "昨天",
    "note", "notes", "summary", "agenda", "action", "actions", "action items", "decision",
    "decisions", "conclusion", "question", "topic", "date", "time", "location", "attendees",
    "participants", "owner", "status", "next steps", "todo", "risk", "risks", "example",
    "source", "link", "re", "subject", "update", "background", "goal", "result", "warning",
}
# Characters that almost never appear in a name or role label but are common in speech.
FUNCTION_CHARS = set("的是了呢吗吧就这那说讲么啊嗯哦也都还在有和与但而我你他她它们")

SPEAKER_NUM_RE = re.compile(r"(?:说话人|发言人|讲者|发言者|speaker|spk|participant)\s*\d{1,3}", re.I)
LETTER_NAME_RE = re.compile(r"[A-Za-z]\s+[" + CJK + r"·]{1,6}")
CJK_LABEL_RE = re.compile(r"[" + CJK + r"·]{1,8}(?:[A-Za-z]{1,4}\d{0,2}|\d{1,2})?")
EN_LABEL_RE = re.compile(r"(?:[A-Z][A-Za-z0-9.'-]*|\d+)(?:\s(?:[A-Z][A-Za-z0-9.'-]*|\d+)){0,3}")

LABEL = r"[^:\s(\[][^:]{0,23}?"
HEADER_PATTERNS = [
    # [00:01:23] 发言人1：内容
    ("ts_label", re.compile(r"^[\[(]?(" + TS + r")[\])]?\s*(" + LABEL + r")\s*:\s*(.*)$")),
    # [00:01:23] 发言人1
    ("ts_label_line", re.compile(r"^[\[(]?(" + TS + r")[\])]?\s+(" + LABEL + r")\s*$")),
    # Speaker 1 (00:12): content
    ("label_paren_ts", re.compile(r"^(" + LABEL + r")\s*[\[(]\s*(" + TS + r")\s*[\])]\s*:?\s*(.*)$")),
    # A 林伟 00:00   /   张三 00:12：内容
    ("label_ts", re.compile(r"^(" + LABEL + r")\s+[\[(]?(" + TS + r")[\])]?\s*(?::\s*(.*))?$")),
    # 张三：内容   /   John: content
    ("label", re.compile(r"^(" + LABEL + r")\s*:\s*(.*)$")),
]

NOISE_KEYWORDS = [
    "外卖", "快递", "吃饭", "午饭", "晚饭", "孩子", "空调", "天气", "周末", "放假", "抽烟", "阳台",
    "喝茶", "投屏", "听得到", "听不到", "掉线", "卡了", "去哪", "怎么来", "开车", "地铁", "团建",
    "洗手间", "厕所", "会议室预订",
    "lunch", "coffee", "bathroom", "can you hear me", "you're on mute", "on mute", "wifi",
    "traffic", "weekend",
]
NOISE_RE = re.compile("|".join(re.escape(k) for k in NOISE_KEYWORDS), re.I)


def normalize(text):
    """NFKC folds full-width colons, brackets, digits and the ideographic space."""
    return unicodedata.normalize("NFKC", text)


def ts_seconds(ts):
    parts = [int(p) for p in normalize(ts).split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def clean_label(raw):
    label = raw.strip().strip("*_").strip()
    label = label.strip("【】[]").strip()
    label = re.sub(r"\s*\([^()]*\)$", "", label)  # 王总（运营副总） -> 王总
    return re.sub(r"\s+", " ", label).strip()


def is_speaker_label(label):
    if not label or len(label) > 24:
        return False
    if label.lower() in NON_SPEAKER_LABELS:
        return False
    if re.fullmatch(r"[A-Za-z]", label) or SPEAKER_NUM_RE.fullmatch(label):
        return True
    if LETTER_NAME_RE.fullmatch(label) or CJK_LABEL_RE.fullmatch(label):
        return not (set(label) & FUNCTION_CHARS)
    return bool(EN_LABEL_RE.fullmatch(label))


def noise_hint(text):
    m = NOISE_RE.search(text)
    return m.group(0) if m else None


def classify_line(raw):
    """Return (kind, header) where kind is blank|markup|header|annotation|content."""
    s = raw.strip()
    if not s:
        return "blank", None
    if s.startswith(("```", "#", ">", "|", "- ", "* ", "+ ")) or re.match(r"^\d+\.\s", s):
        return "markup", None
    n = normalize(s).replace("**", "").replace("__", "").strip()
    for kind, rx in HEADER_PATTERNS:
        m = rx.match(n)
        if not m:
            continue
        g = m.groups()
        if kind in ("ts_label", "ts_label_line"):
            ts, label, text = g[0], g[1], (g[2] if len(g) > 2 else "")
        elif kind == "label":
            label, ts, text = g[0], None, g[1]
        else:
            label, ts, text = g[0], g[1], g[2]
        label = clean_label(label)
        if is_speaker_label(label):
            return "header", {"speaker": label, "ts": ts, "text": (text or "").strip(), "style": kind}
    if n[0] in "([" and n[-1] in ")]":
        return "annotation", None
    return "content", None


def parse_transcript(text):
    """Split a transcript into speaker turns.

    Lines without a speaker label are attached to the preceding turn. Markdown headings
    and code fences end the current turn. Noise is only hinted, never removed.
    """
    records, turns, current = [], [], None
    for line_no, raw in enumerate(text.splitlines(), 1):
        kind, header = classify_line(raw)
        rec = {"line": line_no, "raw": raw, "kind": kind, "turn": None, "noise": None}
        if kind == "header":
            ts = normalize(header["ts"]) if header["ts"] else None
            current = {
                "id": "T%03d" % (len(turns) + 1),
                "speaker": header["speaker"],
                "ts": ts,
                "seconds": ts_seconds(ts) if ts else None,
                "line": line_no,
                "text": header["text"],
            }
            turns.append(current)
            rec["turn"] = current["id"]
            rec["noise"] = noise_hint(header["text"])
        elif kind == "content":
            if current is not None:
                current["text"] = (current["text"] + " " + raw.strip()).strip()
                rec["turn"] = current["id"]
            rec["noise"] = noise_hint(raw)
        elif kind == "annotation":
            rec["noise"] = noise_hint(raw)
        elif kind == "markup" and raw.strip().startswith(("#", "```")):
            current = None
        records.append(rec)
    time_points = sorted({ts_seconds(t) for t in TS_RE.findall(normalize(text))})
    return {"records": records, "turns": turns, "time_points": time_points}


def speaker_counts(turns):
    counts = {}
    for t in turns:
        counts[t["speaker"]] = counts.get(t["speaker"], 0) + 1
    return counts


def cmd_preprocess(args):
    """预处理：切分发言轮次，归一化发言人标签，把疑似噪声行标为建议（从不删除）。"""
    text = read_text(args.input)
    parsed = parse_transcript(text)
    records, turns = parsed["records"], parsed["turns"]
    by_id = {t["id"]: t for t in turns}
    counts = speaker_counts(turns)

    if args.json:
        payload = {
            "tool": "biz-retro-analyzer preprocess",
            "version": VERSION,
            "source": str(args.input),
            "speakers": [{"label": k, "turns": v} for k, v in counts.items()],
            "turns": turns,
            "noiseHints": [{"line": r["line"], "keyword": r["noise"], "text": r["raw"].strip()}
                           for r in records if r["noise"]],
            "unattributedLines": [r["line"] for r in records if r["kind"] == "content" and not r["turn"]],
        }
        out = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    else:
        lines = []
        for r in records:
            if r["kind"] in ("blank", "markup"):
                lines.append(r["raw"])
                continue
            if r["kind"] == "annotation":
                prefix = "[NOTE]"
            elif r["turn"]:
                t = by_id[r["turn"]]
                prefix = "[%s %s%s]" % (t["id"], t["speaker"], " @" + t["ts"] if t["ts"] else "")
            else:
                prefix = "[?]"
            hint = " [NOISE? %s]" % r["noise"] if r["noise"] else ""
            lines.append("%s%s %s" % (prefix, hint, r["raw"].strip()))
        out = "\n".join(lines) + "\n"
    _write_output(out, args.output)
    _preprocess_report(args, parsed, counts)


def _preprocess_report(args, parsed, counts):
    records, turns = parsed["records"], parsed["turns"]
    content = [r for r in records if r["kind"] in ("header", "content")]
    attributed = [r for r in content if r["turn"]]
    noise = [r for r in records if r["noise"]]
    times = [t["ts"] for t in turns if t["ts"]]
    err = sys.stderr
    print("=" * 60, file=err)
    print("  biz-retro-analyzer · transcript preprocessing", file=err)
    print("=" * 60, file=err)
    print("  Content lines : %d" % len(content), file=err)
    print("  Turns         : %d" % len(turns), file=err)
    print("  Speakers      : %d" % len(counts), file=err)
    for label, n in counts.items():
        print("      %-20s %d turn(s)" % (label, n), file=err)
    if content:
        print("  Attributed    : %d%% (%d/%d lines)" % (
            round(100 * len(attributed) / len(content)), len(attributed), len(content)), file=err)
    print("  Timestamps    : %s" % ("%s - %s" % (times[0], times[-1]) if times else "none"), file=err)
    annotations = sum(1 for r in records if r["kind"] == "annotation")
    if annotations:
        print("  Annotations   : %d non-speech note line(s), tagged [NOTE]" % annotations, file=err)
    if not counts:
        print("  WARN  No speaker labels -> use speaker-unknown mode", file=err)
    singletons = [k for k, v in counts.items() if v == 1]
    if len(turns) >= 6 and singletons:
        print("  WARN  Label(s) seen only once, check they are real speakers: %s" % ", ".join(singletons),
              file=err)
    if noise:
        print("  Possible noise: %d line(s). Suggestions only - nothing was removed." % len(noise), file=err)
        print("      Read each one before excluding it from the analysis window:", file=err)
        for r in noise[:20]:
            print("      L%-4d [%s] %s" % (r["line"], r["noise"], r["raw"].strip()[:60]), file=err)
    print("=" * 60, file=err)
    if args.output:
        print("Written to %s" % args.output, file=err)


# ---------------------------------------------------------------------------
# Scaffold
# ---------------------------------------------------------------------------

def cmd_scaffold(args):
    """生成结构化输出模板。"""
    mode = args.mode.upper()
    tag_block = (
        "  - `Status`: Confirmed | Inferred | Assumption | Needs validation\n"
        "  - `Strength`: High | Medium | Low\n"
        "  - `Basis`: Source quote | Cross-source pattern | User context\n"
        "  - `Source anchor`: [speaker, timestamp]"
    )
    sections = [
        "## Structured Fact Record",
        "- **Source type**: transcript | notes | chat-log",
        "- **What is confirmed**:",
        "- **Evidence notes**:\n" + tag_block,
    ]
    if mode in ("B", "C"):
        sections += [
            "## Project Thread\n- **Current stage**:\n- **Direction shifts**:",
            "## Stakeholder Motive Readout",
            "| Party | Says | Appears to want | Confidence | Evidence |",
            "|-------|------|-----------------|------------|----------|",
            "## Participant Understanding Map",
            "| Party | Domain | Workflow | Delivery | Org | Evidence |",
            "|-------|--------|----------|----------|-----|----------|",
            "## Current Actions\n- **Do now**:\n- **Validate before commit**:",
        ]
    if mode == "C":
        sections += [
            "## Judgment and Reverse Audit",
            "- **Supported judgments**:\n" + tag_block,
            "- **Weak judgments**:\n" + tag_block,
            "- **Suspicious actions**:\n  - `Action`:\n  - `Info-change explanation`:\n"
            "  - `Pressure explanation`:\n  - `Misdirection explanation`:",
        ]
    content = f"# Mode {mode} Output\n\n" + "\n\n".join(sections) + "\n"
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Template (Mode {mode}) → {args.output}")
    else:
        print(content)


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------

def cmd_validate(args):
    """验证分析输出是否符合协议规则。"""
    text = read_text(args.input)
    checks = []

    has_tags = bool(re.search(r"`Status`\s*:", text, re.I))
    checks.append(("Evidence tags present", has_tags))

    anchor_failures = []
    for kw in HIGH_RISK_KEYWORDS:
        for m in re.finditer(re.escape(kw), text, re.I):
            window = text[max(0, m.start()-200):m.end()+200]
            if not re.search(r"anchor|来源|锚点", window, re.I):
                anchor_failures.append(m.group())
    checks.append(("High-risk claims have anchors", len(anchor_failures) == 0))

    checks.append(("Fact layer present",
        bool(re.search(r"Fact Record|事实记录|What is confirmed", text, re.I))))

    has_map = bool(re.search(r"Understanding Map|理解地图", text, re.I))
    checks.append(("Understanding map present", has_map))

    bad_confirmed = re.findall(r"(?i)Confirmed.*(?:motive|intent|动机|意图)", text)
    checks.append(("No Confirmed motive claims", len(bad_confirmed) == 0))

    action_lines = re.findall(r"(?i)(?:Do now|立即)[^\n]*", text)
    has_action_ev = any(re.search(r"evidence|证据", a, re.I) for a in action_lines) if action_lines else False
    checks.append(("Actions have evidence", has_action_ev or not action_lines))

    print("=" * 60)
    print("  biz-retro-analyzer · protocol validation")
    print("=" * 60)
    for name, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
    errors = [n for n, p in checks if not p]
    passed_count = sum(1 for _, p in checks if p)
    print(f"\n  Result: {passed_count}/{len(checks)} passed")
    if errors:
        print("  Status: FAIL"); sys.exit(1)
    else:
        print("  Status: PASS")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(prog="retro_tool.py", description="biz-retro-analyzer CLI")
    parser.add_argument("--version", action="version", version="biz-retro-analyzer %s" % VERSION)
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("preprocess", help="Split a transcript into speaker turns; hint possible noise")
    p.add_argument("input")
    p.add_argument("-o", "--output", help="write the annotated transcript (or JSON) here instead of stdout")
    p.add_argument("--json", action="store_true", help="emit turns as JSON instead of annotated text")

    p = sub.add_parser("scaffold", help="Generate output template")
    p.add_argument("--mode", choices=["A", "B", "C"], default="B")
    p.add_argument("-o", "--output")

    p = sub.add_parser("validate", help="Check analysis against protocol")
    p.add_argument("input")
    return parser


def main(argv=None):
    _setup_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {"preprocess": cmd_preprocess, "scaffold": cmd_scaffold, "validate": cmd_validate}
    if args.command not in handlers:
        parser.print_help()
        return 1
    try:
        return handlers[args.command](args) or 0
    except FileNotFoundError as exc:
        print("error: file not found: %s" % exc.filename, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
