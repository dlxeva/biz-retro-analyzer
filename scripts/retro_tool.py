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
# Output vocabulary (shared by scaffold, validate and render)
# ---------------------------------------------------------------------------

STATUS_VALUES = ["Confirmed", "Inferred", "Assumption", "Needs validation"]
STRENGTH_VALUES = ["High", "Medium", "Low"]
BASIS_VALUES = ["Source quote/paraphrase", "Cross-source pattern", "User context", "Later reasoning only"]

# (key, canonical heading, lowercase aliases matched against headings)
SECTIONS = [
    ("fact", "Structured Fact Record", ["fact record", "fact pack", "source record", "事实记录", "事实层"]),
    ("thread", "Project Thread", ["project thread", "project retro", "项目脉络", "项目主线", "项目复盘"]),
    ("chain", "Advancement / Influence Chain", ["influence chain", "advancement chain", "推进链", "影响链"]),
    ("motive", "Stakeholder Motive Readout", ["motive readout", "stakeholder motive", "position readout",
                                              "动机", "立场解读"]),
    ("map", "Participant Understanding Map", ["understanding map", "理解地图", "理解图谱"]),
    ("audit", "Judgment and Reverse Audit", ["reverse audit", "judgment and", "反向审计", "判断与"]),
    ("actions", "Current Actions", ["current actions", "next actions", "当前行动", "行动建议", "下一步行动"]),
    ("method", "Method Notes", ["method notes", "方法笔记", "方法沉淀"]),
]
SECTION_TITLES = {k: t for k, t, _ in SECTIONS}
MODE_REQUIRED = {
    "A": ["fact"],
    "B": ["fact", "thread", "motive", "map", "actions"],
    "C": ["fact", "thread", "motive", "map", "audit", "actions"],
}

# Claim types covered by the High-Risk Claim Gate (SKILL.md). Matched in claim text only.
HIGH_RISK_TERMS = [
    "motive", "intent", "hidden agenda", "bad faith", "misdirection", "manipulat", "kickback",
    "conflict of interest", "controls the", "gatekeeper", "decision path", "decision authority",
    "leverage", "budget", "pricing", "political", "exit rationale", "true priority",
    "动机", "意图", "真实目的", "回扣", "利益冲突", "利益输送", "操纵", "揽权", "控制权", "决策权",
    "拍板权", "把关人", "预算", "定价", "政治", "站队", "恶意", "误导", "退出理由",
]
HIGH_RISK_RE = re.compile("|".join(re.escape(t) for t in HIGH_RISK_TERMS), re.I)
INTERPRETATION_RE = re.compile(
    r"\b(?:wants? to|appears to want|motive|intends?|secretly|clearly wants)\b|想要|动机|意图|显然是想|其实是想", re.I)

FIELD_KEYS = {
    "claim": "claim", "judgment": "claim", "action": "claim", "action or contradiction": "claim",
    "判断": "claim", "论断": "claim",
    "status": "status", "claim status": "status", "current status": "status", "状态": "status",
    "strength": "strength", "evidence strength": "strength", "confidence": "strength",
    "强度": "strength", "证据强度": "strength", "置信度": "strength",
    "basis": "basis", "source basis": "basis", "依据": "basis",
    "source anchor": "anchor", "anchor": "anchor", "evidence anchor": "anchor", "evidence": "anchor",
    "triggered by": "anchor", "锚点": "anchor", "来源锚点": "anchor", "原文锚点": "anchor", "证据": "anchor",
    "what would validate it": "validate", "what still needs validation": "validate", "to validate": "validate",
    "why it matters": "other", "待验证": "validate", "如何验证": "validate",
    "information-change explanation": "explain", "info-change explanation": "explain",
    "pressure explanation": "explain", "pressure or misjudgment explanation": "explain",
    "strategic-misdirection explanation": "explain", "misdirection explanation": "explain",
}
TAG_KEYS = {"claim", "status", "strength", "basis", "anchor", "validate", "explain"}
DO_NOW_RE = re.compile(r"^(?:do now|立即做|立即|马上做|现在就做)$", re.I)

PLACEHOLDER_RES = [
    re.compile(r"Confirmed\s*\|\s*Inferred"),
    re.compile(r"High\s*\|\s*Medium"),
    re.compile(r"Source quote\S*\s*\|\s*Cross-source"),
    re.compile(r"transcript\s*\|\s*notes", re.I),
    re.compile(r"<fill[^>]*>", re.I),
    re.compile(r"\[speaker,\s*timestamp\]", re.I),
    re.compile(r"\{\{[^}]+\}\}"),
]

FIELD_RE = re.compile(
    r"^(?:\*\*(?P<b>[^*]{1,60}?)(?P<bc>[:：])?\*\*|`(?P<c>[^`]{1,60})`|"
    r"(?P<p>[A-Za-z][A-Za-z /'-]{0,47}|[" + CJK + r"][" + CJK + r"/]{0,11}))"
    r"\s*(?P<colon>[:：])?\s*(?P<v>.*)$")
INLINE_ANCHOR_RE = re.compile(
    r"(?:source anchor|evidence anchor|anchor|evidence|triggered by|锚点|来源锚点|原文锚点|证据)\s*[:：]\s*([^`\n]+)",
    re.I)
INLINE_STATUS_RE = re.compile(r"`(Confirmed|Inferred|Assumption|Needs validation)`")
QUOTE_RES = [
    re.compile(r"\u201c([^\u201d\n]{2,300})\u201d"),
    re.compile(r"\u300c([^\u300d\n]{2,300})\u300d"),
    re.compile(r"\u300e([^\u300f\n]{2,300})\u300f"),
    re.compile(r'(?<![A-Za-z0-9])"([^"\n]{2,300})"'),
    re.compile(r"`([^`\n]{2,300})`"),
]
RANGE_SEP = r"\s*(?:-|\u2013|\u2014|~|\uff5e|to|至|到)\s*"
TS_ITEM_RE = re.compile(
    r"(?P<approx>~|≈|约|approx\.?\s*)?(?<![\d:])(?P<a>" + TS + r")(?:" + RANGE_SEP + r"(?P<b>" + TS + r"))?(?![\d:])")
SEG_SPLIT_RE = re.compile(r"[,，、;；|。]|\s/\s")
ADJACENT_GAP_RE = re.compile(r"^[\s*_`]*(?:['’]s)?[\s,，:：(（\[【]*(?:at|@|于|在|说|称|表示|said|says)?[\s:：(（]*$")
TITLE_WORDS = {"Director", "Dr", "Dr.", "Mr", "Mr.", "Mrs", "Mrs.", "Ms", "Ms.", "Prof", "Prof.",
               "Manager", "Doctor", "Chief", "Head", "Mister", "Lead", "VP", "CEO", "CTO", "CFO"}


def section_key(title):
    t = normalize(title).lower()
    for key, canonical, aliases in SECTIONS:
        if canonical.lower() in t or any(a in t for a in aliases):
            return key
    return None


def has_cjk(text):
    return bool(re.search("[" + CJK + "]", text))


def norm_for_match(text):
    text = normalize(text).lower()
    return "".join(ch for ch in text if ch.isalnum())


def enum_value(raw, values):
    """Return the enum value a field starts with, or None. 'Needs validation - x' -> 'Needs validation'."""
    s = re.sub(r"[`*_]", "", raw or "").strip()
    for v in sorted(values, key=len, reverse=True):
        if s.lower().startswith(v.lower()):
            return v
    return None


# ---------------------------------------------------------------------------
# Markdown model
# ---------------------------------------------------------------------------

BULLET_RE = re.compile(r"^(\s*)(?:[-*+]|\d{1,3}[.)])\s+(.*)$")


def _split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def parse_markdown(text):
    """Parse a Markdown analysis into headings, bullet trees, table rows and paragraphs."""
    nodes, tables, headings = [], [], []
    section, level, stack = None, 0, []
    lines = text.splitlines()
    in_fence = False
    i = 0
    while i < len(lines):
        raw = lines[i]
        line_no = i + 1
        s = raw.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            lvl, title = len(m.group(1)), m.group(2).strip()
            key = section_key(title)
            if key:
                section, level = key, lvl
            elif lvl <= level:
                section, level = None, 0
            headings.append({"line": line_no, "level": lvl, "title": title, "key": key})
            stack = []
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            header = _split_row(s)
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = _split_row(lines[j])
                rows.append({"line": j + 1, "cells": dict(zip(header, cells + [""] * len(header)))})
                j += 1
            tables.append({"line": line_no, "header": header, "rows": rows, "section": section})
            stack = []
            i = j
            continue
        b = BULLET_RE.match(raw)
        if b:
            indent = len(b.group(1).replace("\t", "    "))
            node = {"line": line_no, "indent": indent, "text": b.group(2).strip(), "children": [],
                    "parent": None, "section": section, "kind": "bullet"}
            while stack and stack[-1]["indent"] >= indent:
                stack.pop()
            if stack:
                node["parent"] = stack[-1]
                stack[-1]["children"].append(node)
            nodes.append(node)
            stack.append(node)
        elif s:
            if stack and raw[:1].isspace():
                stack[-1]["text"] += " " + s
            else:
                nodes.append({"line": line_no, "indent": 0, "text": s, "children": [], "parent": None,
                              "section": section, "kind": "para"})
                stack = []
        i += 1
    for n in nodes:
        n["field"], n["key"], n["value"] = _field(n["text"])
    return {"nodes": nodes, "tables": tables, "headings": headings}


def _field(text):
    m = FIELD_RE.match(text)
    if not m or not (m.group("bc") or m.group("colon")):
        return None, None, text
    name = (m.group("b") or m.group("c") or m.group("p") or "").strip().strip(":：").strip()
    if not name:
        return None, None, text
    return name, FIELD_KEYS.get(name.lower(), FIELD_KEYS.get(name)), m.group("v").strip()


def subtree_text(node):
    parts = [node["text"]]
    for c in node["children"]:
        parts.append(subtree_text(c))
    return " ".join(parts)


def build_units(model):
    """Group evidence-tag fields into judgment units; also collect inline-tagged bullets."""
    units = []
    siblings = {}
    for n in model["nodes"]:
        if n["kind"] == "bullet":
            siblings.setdefault(id(n["parent"]) if n["parent"] else ("root", n["section"], n["indent"]),
                                []).append(n)
    for group in siblings.values():
        current = None
        prev_line = None
        for n in group:
            is_tag = n["key"] in TAG_KEYS
            contiguous = prev_line is not None and current is not None
            if is_tag:
                if current is None or not contiguous or n["key"] in current["fields"] and n["key"] in (
                        "claim", "status"):
                    current = {"fields": {}, "nodes": [], "parent": n["parent"], "line": n["line"],
                               "section": n["section"], "kind": "group"}
                    units.append(current)
                current["fields"].setdefault(n["key"], " ".join(
                    [n["value"]] + [subtree_text(c) for c in n["children"]]).strip())
                current["nodes"].append(n)
                prev_line = n["line"]
            else:
                current, prev_line = None, None
    for n in model["nodes"]:
        if n["key"] in TAG_KEYS:
            continue
        m = INLINE_STATUS_RE.search(n["text"])
        if m:
            claim = re.sub(r"`[^`]*`", "", n["text"]).strip(" /-—")
            anchors = INLINE_ANCHOR_RE.findall(n["text"])
            units.append({"fields": {"claim": claim, "status": m.group(1), "anchor": "; ".join(anchors)},
                          "nodes": [n], "parent": n["parent"], "line": n["line"], "section": n["section"],
                          "kind": "inline", "text": n["text"]})
    for u in units:
        if u["kind"] == "group":
            u["text"] = " ".join(subtree_text(n) for n in u["nodes"])
            if not u["fields"].get("claim") and u["parent"] is not None:
                u["fields"]["claim"] = u["parent"]["value"] or ""
    units.sort(key=lambda u: u["line"])
    return units


# ---------------------------------------------------------------------------
# Source index: resolve anchors against transcripts
# ---------------------------------------------------------------------------

class SourceIndex:
    def __init__(self, paths):
        self.paths = list(paths)
        self.turns, self.time_points, self.texts = [], set(), []
        for p in self.paths:
            text = read_text(p)
            parsed = parse_transcript(text)
            for t in parsed["turns"]:
                t = dict(t)
                t["source"] = str(p)
                t["norm"] = norm_for_match(t["text"])
                self.turns.append(t)
            self.time_points.update(parsed["time_points"])
            self.texts.append(norm_for_match(text))
        self.labels = sorted({t["speaker"] for t in self.turns})
        letters = re.findall(r"[A-Za-z]{1,8}", "".join(self.texts))
        cjk = re.findall("[" + CJK + "]", "".join(self.texts))
        self.cjk = len(cjk) > len(letters) * 0.3
        self.span = (min(self.time_points), max(self.time_points)) if self.time_points else None
        self.aliases = {}
        for label in self.labels:
            self.aliases[label] = label
            m = re.match(r"^([A-Za-z])\s+(.+)$", label)
            if m:
                self.aliases[m.group(2)] = label
        self.letters = {}
        for label in self.labels:
            m = re.match(r"^([A-Za-z])\s+", label)
            if m:
                self.letters[m.group(1).upper()] = label

    def learn_aliases(self, text):
        """Map document aliases such as 'Director Zhou (C)' onto transcript speaker 'C 周主任'."""
        word_owner = {}
        pattern = re.compile(
            r"([A-Z][A-Za-z.'-]*(?:\s+[A-Z][A-Za-z.'-]*){0,3}|[" + CJK + r"]{2,6})\s*[(（]\s*([A-Za-z])\s*[)）]")
        for alias, letter in pattern.findall(normalize(text)):
            label = self.letters.get(letter.upper())
            if not label:
                continue
            self.aliases.setdefault(alias, label)
            for word in alias.split():
                if word in TITLE_WORDS or len(word) < 2:
                    continue
                word_owner.setdefault(word, set()).add(label)
        for word, owners in word_owner.items():
            if len(owners) == 1:
                self.aliases.setdefault(word, owners.pop())

    def _alias_matches(self, text):
        for alias, label in self.aliases.items():
            if re.match(r"^[A-Za-z0-9 .'-]+$", alias):
                rx = re.compile(r"(?<![A-Za-z])" + re.escape(alias) + r"(?![A-Za-z])")
            else:
                rx = re.compile(re.escape(alias))
            for m in rx.finditer(text):
                yield label, m.start(), m.end()

    def find_speaker(self, text):
        """Return (label, end_pos) of the last speaker alias mentioned in text, or (None, -1)."""
        best = (None, -1, 0)
        for label, start, end in self._alias_matches(text):
            if end > best[1] or (end == best[1] and end - start > best[2]):
                best = (label, end, end - start)
        return best[0], best[1]

    def speaker_before(self, text):
        """Speaker alias that directly precedes the end of text ('Zhou 04:15', '周总：“...”')."""
        label, end = self.find_speaker(text)
        if label and ADJACENT_GAP_RE.match(text[end:]):
            return label
        return None

    def speaker_after(self, text):
        """Speaker alias that directly follows a timestamp ('10:15 高远承认...')."""
        rest = text.lstrip(" ")
        for label, start, _ in self._alias_matches(rest[:16]):
            if start == 0:
                return label
        return None

    def turns_at(self, seconds, approx=False):
        tol = 30 if approx else 0
        return [t for t in self.turns if t["seconds"] is not None and abs(t["seconds"] - seconds) <= tol]

    def known_time(self, seconds, approx=False):
        if approx:
            return bool(self.span) and self.span[0] - 30 <= seconds <= self.span[1] + 30
        return seconds in self.time_points

    def find_quote(self, quote):
        """Return (matched_turns, found_anywhere). Fuzzy match tolerates dropped fillers."""
        q = norm_for_match(quote)
        hits = [t for t in self.turns if q in t["norm"]]
        if hits:
            return hits, True
        if any(q in text for text in self.texts):
            return [], True
        hits = [t for t in self.turns if _coverage(q, t["norm"]) >= 0.8]
        return hits, bool(hits)


def _coverage(q, text):
    from difflib import SequenceMatcher
    if not q or not text:
        return 0.0
    width = max(len(q) * 2, 8)
    step = max(len(q) // 2, 1)
    best = 0.0
    for start in range(0, max(len(text) - len(q), 0) + 1, step):
        window = text[start:start + width]
        sm = SequenceMatcher(None, q, window, autojunk=False)
        matched = sum(b.size for b in sm.get_matching_blocks() if b.size >= 2)
        best = max(best, matched / float(len(q)))
        if best >= 0.8:
            break
    return best


def extract_quotes(text):
    found, spans = [], []
    for rx in QUOTE_RES:
        for m in rx.finditer(text):
            if any(a <= m.start() < b for a, b in spans):
                continue
            q = m.group(1).strip()
            is_backtick = rx.pattern.startswith("`")
            if is_backtick and (not has_cjk(q) or INLINE_ANCHOR_RE.match(q) or ":" in normalize(q)):
                continue
            n = norm_for_match(q)
            if len(n) < (3 if has_cjk(q) else 12):
                continue
            spans.append((m.start(), m.end()))
            found.append((q, m.start()))
    return found


def normalize_analysis(text):
    """NFKC, but keep '02:38：41 家' from becoming the timestamp 02:38:41."""
    return normalize(re.sub(r"(\d:\d{2})\uff1a", "\\1 \uff1a", text))


def fragments(model):
    """Yield (line, text, is_anchor_context, default_party) for every piece of analysis text."""
    for n in model["nodes"]:
        if n["key"] == "anchor":
            yield n["line"], n["value"], True, ""
            continue
        rest = n["text"]
        for m in list(re.finditer(r"`[^`\n]*`", rest)):
            inner = INLINE_ANCHOR_RE.search(m.group(0)[1:-1])
            if inner:
                yield n["line"], inner.group(1), True, ""
                rest = rest[:m.start()] + " " * (m.end() - m.start()) + rest[m.end():]
        for m in list(INLINE_ANCHOR_RE.finditer(rest)):
            yield n["line"], m.group(1), True, ""
            rest = rest[:m.start()] + " " * (m.end() - m.start()) + rest[m.end():]
        yield n["line"], rest, False, ""
    for table in model["tables"]:
        party_col = table["header"][0] if table["header"] else None
        for row in table["rows"]:
            party = row["cells"].get(party_col, "") if party_col else ""
            for col, val in row["cells"].items():
                if col == party_col or not val:
                    continue
                anchor_col = bool(re.search(r"evidence|anchor|证据|锚点|依据|来源", col, re.I))
                yield row["line"], val, anchor_col, party


def check_anchors(model, index, results):
    """Timestamps, speaker attributions and quotes must resolve to the source transcript.

    A speaker counts as explicit only when the name sits right next to the timestamp or quote
    ('Zhou 04:15', '10:15 高远', '周总：“...”'). Explicit mismatches inside anchors fail;
    looser attributions (row party, earlier mention) are reported as INFO.
    """
    stats = {"timestamps": 0, "quotes": 0, "skipped_quotes": 0}
    for line, text, anchor_ctx, default_party in fragments(model):
        text = normalize_analysis(text)
        default = index.find_speaker(normalize(default_party))[0] if default_party else None
        level = "FAIL" if anchor_ctx else "WARN"
        mismatch = "FAIL" if anchor_ctx else "WARN"
        last, pending = None, None
        for seg in SEG_SPLIT_RE.split(text):
            items = list(TS_ITEM_RE.finditer(seg))
            if not items:
                pending = index.speaker_before(seg.rstrip(" *_`"))
                continue
            for it in items:
                stats["timestamps"] += 1
                explicit = (index.speaker_before(seg[:it.start()]) or index.speaker_after(seg[it.end():])
                            or pending)
                speaker = explicit or last or default or index.find_speaker(seg[:it.start()])[0]
                sev = mismatch if explicit else "INFO"
                approx = bool(it.group("approx"))
                a = ts_seconds(it.group("a"))
                b = ts_seconds(it.group("b")) if it.group("b") else None
                shown = it.group(0).strip()
                pending = None
                if explicit:
                    last = explicit
                if b is None:
                    if not index.known_time(a, approx):
                        results.append((level, line, "timestamp %s does not appear in the transcript" % shown))
                        continue
                    present = {t["speaker"] for t in index.turns_at(a, approx)}
                    if speaker and present and speaker not in present:
                        results.append((sev, line, "%s is %s speaking, not %s" % (
                            shown, " / ".join(sorted(present)), speaker)))
                else:
                    lo, hi = min(a, b), max(a, b)
                    if not index.span or lo < index.span[0] or hi > index.span[1]:
                        results.append((level, line, "range %s falls outside the transcript" % shown))
                        continue
                    if speaker and not any(t["speaker"] == speaker and t["seconds"] is not None and
                                           lo <= t["seconds"] <= hi for t in index.turns):
                        results.append((sev, line, "%s has no turn in %s" % (speaker, shown)))
        for quote, pos in extract_quotes(text):
            if has_cjk(quote) != index.cjk:
                stats["skipped_quotes"] += 1
                continue
            stats["quotes"] += 1
            hits, found = index.find_quote(quote)
            if not found:
                results.append(("FAIL" if anchor_ctx else "INFO", line,
                                "quote not found in the transcript: \u201c%s\u201d" % quote[:40]))
                continue
            explicit = index.speaker_before(text[:pos])
            speaker = explicit or default
            if speaker and hits and speaker not in {t["speaker"] for t in hits}:
                results.append((mismatch if explicit else "INFO", line, "quote \u201c%s\u201d is from %s, not %s" % (
                    quote[:30], " / ".join(sorted({t["speaker"] for t in hits})), speaker)))
    return stats


# ---------------------------------------------------------------------------
# Scaffold
# ---------------------------------------------------------------------------

FILL = "<fill>"


def _tag_fields(indent="  ", validate=True):
    lines = [
        indent + "- `Claim`: " + FILL,
        indent + "- `Status`: " + FILL + "  <!-- " + " | ".join(STATUS_VALUES) + " -->",
        indent + "- `Strength`: " + FILL + "  <!-- " + " | ".join(STRENGTH_VALUES) + " -->",
        indent + "- `Basis`: " + FILL + "  <!-- " + " | ".join(BASIS_VALUES) + " -->",
        indent + "- `Source anchor`: " + FILL + "  <!-- speaker MM:SS \"short verbatim quote\" -->",
    ]
    if validate:
        lines.append(indent + "- `What would validate it`: " + FILL)
    return "\n".join(lines)


def _table(headers):
    return "| " + " | ".join(headers) + " |\n| " + " | ".join("---" for _ in headers) + " |\n| " + \
        " | ".join(FILL for _ in headers) + " |"


def scaffold_markdown(mode):
    t = SECTION_TITLES
    parts = ["# Mode %s Output" % mode, ""]
    parts += [
        "## " + t["fact"], "",
        "- **Source set**: " + FILL,
        "- **Source type**: " + FILL + "  <!-- transcript, notes, chat log, field notes -->",
        "- **Interaction context**: " + FILL,
        "- **Analysis window**: " + FILL + "  <!-- e.g. 00:00-42:10, excluding 05:05-06:40 (room booking) -->",
        "- **What is confirmed**:",
        "  - " + FILL + " `Source anchor: " + FILL + "`",
        "- **Explicit decisions**:",
        "- **Explicit follow-up actions**:",
        "- **Open factual gaps**:",
        "- **Evidence notes**:",
        _tag_fields(validate=False), "",
    ]
    if mode in ("B", "C"):
        parts += [
            "## " + t["thread"], "",
            "- **Current stage**: " + FILL,
            "- **How the goal narrowed or shifted**: " + FILL,
            "- **Trial scenario vs. product body**: " + FILL,
            "- **Current blocking issue**: " + FILL,
            "- **Non-blocking but real gaps**: " + FILL,
            "- **Evidence-risk notes**:",
            _tag_fields(), "",
            "## " + t["chain"], "",
            "<!-- Optional: include when a frame or decision path was passed between actors. -->", "",
            _table(["Actor", "Move (claim, frame or action)", "Adopted or amplified by", "Effect on decision",
                    "Evidence anchor", "Status", "Strength", "Risk if wrong"]), "",
            "## " + t["motive"], "",
            _table(["Party", "What they say", "What they appear to want", "Status", "Strength",
                    "Evidence anchor"]), "",
            "## " + t["map"], "",
            "<!-- Levels: strong | mixed | thin | unclear. Or state why the map is omitted. -->", "",
            _table(["Party", "Problem itself", "Advancement path", "Execution / delivery constraints",
                    "Decision / organizational mechanics", "Evidence anchor"]), "",
        ]
    if mode in ("B", "C"):
        parts += [
            "## " + t["audit"], "",
            "- **User's current narrative**: " + FILL,
            "- **Judgments that look supported**:",
            _tag_fields(),
            "- **Judgments that need stronger evidence**:",
            _tag_fields(),
        ]
        if mode == "C":
            parts += [
                "- **Suspicious actions requiring lower-intent alternatives**:",
                "  - `Action or contradiction`: " + FILL,
                "  - `Information-change explanation`: " + FILL,
                "  - `Pressure or misjudgment explanation`: " + FILL,
                "  - `Strategic-misdirection explanation`: " + FILL,
                "  - `Current status`: " + FILL,
                "- **Consensus reality check**: " + FILL,
            ]
        parts += [
            "- **High-impact claims requiring validation**: " + FILL, "",
            "## " + t["actions"], "",
            "- **Do now**:",
            "  - " + FILL + " `Evidence: " + FILL + "`",
            "- **Do later**:",
            "  - " + FILL,
            "- **Must validate before deeper commitment**:",
            "  - " + FILL, "",
        ]
    return "\n".join(parts).rstrip() + "\n"


def cmd_scaffold(args):
    """生成结构化输出模板（所有待填位置都是 <fill>，未填写时 validate 会失败）。"""
    content = scaffold_markdown(args.mode.upper())
    _write_output(content, args.output)
    if args.output:
        print("Template (Mode %s) -> %s" % (args.mode.upper(), args.output), file=sys.stderr)


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------

def infer_mode(text, model):
    head = "\n".join(text.splitlines()[:5])
    m = re.search(r"Mode\s*([ABC])\b", head)
    if m:
        return m.group(1)
    keys = {h["key"] for h in model["headings"] if h["key"]}
    if "audit" in keys and re.search(r"Audit Pack|审计包", head, re.I):
        return "C"
    if keys & {"thread", "motive", "map", "actions"}:
        return "B"
    return "A"


def _has_anchor(unit):
    if unit["fields"].get("anchor", "").strip(" `-"):
        return True
    return bool(TS_RE.search(normalize(unit["text"])) or extract_quotes(unit["text"]))


def lint_markdown(text, mode=None, sources=()):
    """Return (mode, checks). checks: list of {id, title, status, items:[(severity, line, msg)]}."""
    model = parse_markdown(text)
    units = build_units(model)
    mode = (mode or infer_mode(text, model)).upper()
    checks = []

    def add(cid, title, items, info=None, warn_only=False):
        sev = {s for s, _, _ in items} - {"INFO"}
        status = "PASS"
        if "FAIL" in sev and not warn_only:
            status = "FAIL"
        elif sev:
            status = "WARN"
        if warn_only:
            items = [(s if s == "INFO" else "WARN", ln, msg) for s, ln, msg in items]
        checks.append({"id": cid, "title": title, "status": status, "items": items, "info": info})

    present = {h["key"] for h in model["headings"] if h["key"]}
    missing = [k for k in MODE_REQUIRED[mode] if k not in present]
    add("sections", "Required sections for Mode %s" % mode,
        [("FAIL", None, "missing section: %s" % SECTION_TITLES[k]) for k in missing],
        "%d/%d present" % (len(MODE_REQUIRED[mode]) - len(missing), len(MODE_REQUIRED[mode])))

    items = []
    for no, line in enumerate(text.splitlines(), 1):
        clean = re.sub(r"<!--.*?-->", "", line)
        for rx in PLACEHOLDER_RES:
            if rx.search(clean):
                items.append(("FAIL", no, "unfilled placeholder: %s" % clean.strip()[:70]))
                break
    for u in units:
        for key in ("claim", "status"):
            if key in u["fields"] and not u["fields"][key].strip(" `*"):
                items.append(("FAIL", u["line"], "empty `%s` field" % key.capitalize()))
    add("placeholders", "No unfilled template placeholders or empty tag fields", items)

    tagged = [u for u in units if enum_value(u["fields"].get("status"), STATUS_VALUES)]
    need = 1 if mode == "A" else 3
    add("tagged", "At least %d judgment(s) carry Status tags" % need,
        [] if len(tagged) >= need else [("FAIL", None, "found %d tagged judgment(s)" % len(tagged))],
        "%d tagged" % len(tagged))

    items = []
    for u in units:
        st = u["fields"].get("status")
        if st and st.strip(" `*") and not enum_value(st, STATUS_VALUES):
            items.append(("WARN", u["line"], "Status '%s' is not one of %s" % (st[:30], ", ".join(STATUS_VALUES))))
        sg = u["fields"].get("strength")
        if sg and sg.strip(" `*") and not enum_value(sg, STRENGTH_VALUES):
            items.append(("WARN", u["line"], "Strength '%s' is not one of High, Medium, Low" % sg[:30]))
    for table in model["tables"]:
        for col in table["header"]:
            if re.search(r"^(confidence|strength|置信度|强度)$", col.strip(), re.I):
                for row in table["rows"]:
                    v = row["cells"].get(col, "")
                    if v and not enum_value(v, STRENGTH_VALUES) and not re.match(r"^\d{1,3}$", v.strip()):
                        items.append(("WARN", row["line"], "%s '%s' is not High, Medium, Low or 0-100" % (col, v)))
                    elif v and enum_value(v, STRENGTH_VALUES) and re.search(r"[-/~]", v.strip(" `*")):
                        items.append(("WARN", row["line"], "%s '%s' mixes two levels" % (col, v)))
    add("vocabulary", "Status / strength values use the protocol vocabulary", items, warn_only=True)

    gate_items, confirmed_items, later_items = [], [], []
    for u in units:
        status = enum_value(u["fields"].get("status"), STATUS_VALUES)
        claim = u["fields"].get("claim", "")
        risky = HIGH_RISK_RE.search(claim)
        basis = u["fields"].get("basis", "")
        if status == "Confirmed" and re.search(r"later reasoning|后续推理|事后推理", basis, re.I):
            later_items.append(("FAIL", u["line"], "Confirmed claim whose basis is later reasoning only"))
        if not risky or not status:
            continue
        label = "%s claim (%s)" % (status, risky.group(0))
        if status in ("Confirmed", "Inferred") and not _has_anchor(u):
            gate_items.append(("FAIL", u["line"], "high-risk %s has no source anchor: %s" % (label, claim[:60])))
        if status in ("Assumption", "Needs validation") and "validate" not in u["fields"] and \
                not re.search(r"validat|验证", u["text"], re.I):
            gate_items.append(("WARN", u["line"], "high-risk %s does not say what would validate it" % label))
        if status == "Confirmed" and not extract_quotes(u["text"]):
            confirmed_items.append(("FAIL", u["line"], "Confirmed high-risk claim without a verbatim quote: %s"
                                    % claim[:60]))
    for table in model["tables"]:
        header = table["header"]
        ev_cols = [c for c in header if re.search(r"evidence|anchor|证据|锚点|依据", c, re.I)]
        motive_table = table["section"] == "motive" or any(re.search(r"want|motive|想要|动机", c, re.I)
                                                           for c in header)
        for row in table["rows"]:
            cells = row["cells"]
            if all(not v or v == FILL for v in cells.values()):
                continue
            has_ev = any(cells.get(c, "").strip(" -—") for c in ev_cols)
            joined = " ".join(cells.values())
            if motive_table and not has_ev:
                gate_items.append(("FAIL", row["line"], "motive readout row has no evidence: %s" % joined[:50]))
            elif HIGH_RISK_RE.search(joined) and not has_ev and not TS_RE.search(normalize(joined)):
                gate_items.append(("WARN", row["line"], "high-risk wording without evidence: %s" % joined[:50]))
    tagged_lines = {n["line"] for u in units for n in u["nodes"]}
    for n in model["nodes"]:
        if n["line"] in tagged_lines or n["section"] not in ("thread", "motive", "audit", "chain"):
            continue
        own = n["value"] if n["field"] else n["text"]
        if HIGH_RISK_RE.search(own) and not TS_RE.search(normalize(n["text"])) and not extract_quotes(n["text"]) \
                and not INLINE_ANCHOR_RE.search(n["text"]) and not n["children"]:
            gate_items.append(("WARN", n["line"], "untagged high-risk wording: %s" % own[:60]))
    add("gate-anchors", "High-risk claims carry source anchors", gate_items)
    add("gate-confirmed", "No Confirmed high-risk claim without a verbatim quote", confirmed_items)
    add("later-reasoning", "Later reasoning is never Confirmed", later_items)

    if mode in ("B", "C"):
        map_rows = sum(len(t["rows"]) for t in model["tables"] if t["section"] == "map")
        map_text = " ".join(n["text"] for n in model["nodes"] if n["section"] == "map")
        omitted = re.search(r"map omitted|omitted due to|理解地图.{0,10}(?:省略|不输出)", map_text + " " + text, re.I)
        add("map", "Participant Understanding Map has rows or an omission statement",
            [] if map_rows or omitted else [("FAIL", None, "no map rows and no omission statement")],
            "%d row(s)" % map_rows)

        items, found = [], False
        for n in model["nodes"]:
            if not (n["field"] and DO_NOW_RE.match(n["field"].strip())):
                continue
            found = True
            entries = n["children"] or ([n] if n["value"] else [])
            if not entries:
                items.append(("FAIL", n["line"], "Do now is empty"))
            for e in entries:
                body = subtree_text(e) if e is not n else n["value"]
                if FILL in body:
                    continue
                if not (TS_RE.search(normalize(body)) or extract_quotes(body) or INLINE_ANCHOR_RE.search(body)):
                    items.append(("FAIL", e["line"], "Do-now action without evidence: %s" % body[:60]))
        if not found:
            items.append(("FAIL", None, "no `Do now` entry in Current Actions"))
        add("actions", "Do-now actions carry evidence", items)

    if sources:
        index = SourceIndex(sources)
        index.learn_aliases(text)
        items = []
        stats = check_anchors(model, index, items)
        info = "%d timestamp(s), %d quote(s) checked against %d turn(s)" % (
            stats["timestamps"], stats["quotes"], len(index.turns))
        if stats["skipped_quotes"]:
            info += "; %d quote(s) in another language skipped" % stats["skipped_quotes"]
        add("anchors", "Anchors resolve to the source transcript", items, info)
    else:
        add("anchors", "Anchors resolve to the source transcript",
            [("WARN", None, "not verified: pass --transcript to check timestamps, speakers and quotes")])

    items = []
    for n in model["nodes"]:
        if n["section"] == "fact" and not n["line"] in tagged_lines:
            m = INTERPRETATION_RE.search(n["text"])
            if m:
                items.append(("WARN", n["line"], "interpretation word '%s' in the fact layer" % m.group(0)))
    add("fact-layer", "Fact layer avoids interpretation language", items, warn_only=True)
    return mode, checks


def cmd_validate(args):
    """检查分析输出的协议形式，并把证据锚点（时间戳/发言人/引文）对照原始转写稿核对。"""
    text = read_text(args.input)
    sources = list(args.transcript or [])
    mode, checks = lint_markdown(text, args.mode, sources)
    failed = [c for c in checks if c["status"] == "FAIL"]
    if args.json:
        payload = {"tool": "biz-retro-analyzer validate", "version": VERSION, "input": str(args.input),
                   "mode": mode, "transcripts": [str(s) for s in sources],
                   "result": "FAIL" if failed else "PASS",
                   "checks": [{"id": c["id"], "title": c["title"], "status": c["status"], "info": c["info"],
                               "items": [{"severity": s, "line": ln, "message": m} for s, ln, m in c["items"]]}
                              for c in checks]}
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return 1 if failed else 0
    out = ["=" * 60, "  biz-retro-analyzer · protocol lint (Mode %s)" % mode]
    if sources:
        out.append("  transcript: %s" % ", ".join(str(s) for s in sources))
    out.append("=" * 60)
    for c in checks:
        title = c["title"] + (" [%s]" % c["info"] if c["info"] and args.verbose else "")
        out.append("  %-4s  %s" % (c["status"], title))
        visible = [i for i in c["items"] if args.verbose or i[0] != "INFO"]
        shown = visible if args.verbose or c["status"] == "FAIL" else visible[:5]
        for sev, ln, msg in shown:
            out.append("        %s%s %s" % ("L%-4d" % ln if ln else "     ", "" if sev == c["status"] else
                                           " (%s)" % sev.lower(), msg))
        hidden = len(visible) - len(shown)
        if hidden:
            out.append("        ... %d more (use -v)" % hidden)
        infos = len(c["items"]) - len(visible)
        if infos:
            out.append("        %d info note(s) on loose attributions or quoted terms (use -v)" % infos)
    warns = sum(1 for c in checks if c["status"] == "WARN")
    out.append("")
    out.append("  Result: %s (%d failing, %d with warnings, %d checks)" % (
        "FAIL" if failed else "PASS", len(failed), warns, len(checks)))
    if sources:
        out.append("  PASS means the output follows the protocol's form and its anchors resolve.")
    else:
        out.append("  Anchors were not checked against a source; pass --transcript for that.")
    out.append("  It does not mean the judgments are correct; a reviewer still has to read them.")
    out.append("=" * 60)
    print("\n".join(out))
    return 1 if failed else 0


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

    p = sub.add_parser("scaffold", help="Generate an output template with <fill> placeholders")
    p.add_argument("--mode", choices=["A", "B", "C"], default="B")
    p.add_argument("-o", "--output")

    p = sub.add_parser("validate", help="Lint an analysis and resolve its anchors against the transcript")
    p.add_argument("input")
    p.add_argument("-t", "--transcript", action="append",
                   help="source transcript to resolve timestamps, speakers and quotes against (repeatable)")
    p.add_argument("--mode", type=str.upper, choices=["A", "B", "C"], help="override the inferred output mode")
    p.add_argument("--json", action="store_true", help="machine-readable result")
    p.add_argument("-v", "--verbose", action="store_true", help="show every finding and check details")
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
