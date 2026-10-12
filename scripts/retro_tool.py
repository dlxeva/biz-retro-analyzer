#!/usr/bin/env python3
"""biz-retro-analyzer CLI: preprocess transcripts, scaffold outputs, validate anchors, render reports.

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
CHAIN_COLUMNS = ["Actor / Voice", "Claim, frame, or action introduced", "Who adopted or amplified it",
                 "What decision or next step it affected", "Evidence anchor", "Status", "Strength", "Risk if wrong"]
DECISION_COLUMNS = ["#", "Decision", "Decided by", "Owner", "Due", "Status", "Follow-up", "Evidence anchor"]
MINUTES_COLUMNS = ["Written", "Spoken", "Verdict", "Evidence anchor"]
CLAIM_COLUMNS = ["Claim", "Claimant", "Support", "Counter-evidence / correction", "Status", "Evidence anchor"]
MOTIVE_COLUMNS = ["Party", "What they say", "What they appear to want", "Status", "Strength", "Evidence anchor"]
# (schema key, Markdown column, Chinese label)
MAP_DIMENSIONS = [
    ("problem", "Problem itself", "业务问题本身"),
    ("advancementPath", "Advancement path", "实际推进路径"),
    ("deliveryConstraints", "Execution / delivery constraints", "执行与交付约束"),
    ("decisionMechanics", "Decision / organizational mechanics", "决策与组织机制"),
]
MAP_COLUMNS = ["Party / Voice"] + [col for _, col, _ in MAP_DIMENSIONS] + ["Evidence anchor"]
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
        self.raw = ""
        for p in self.paths:
            text = read_text(p)
            self.raw += text
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
            _table(CHAIN_COLUMNS), "",
            "## " + t["motive"], "",
            _table(MOTIVE_COLUMNS), "",
            "## " + t["map"], "",
            "<!-- Levels: strong | mixed | thin | unclear. Or state why the map is omitted. -->", "",
            _table(MAP_COLUMNS), "",
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
    mode = args.mode.upper()
    content = scaffold_json(mode) if args.format == "json" else scaffold_markdown(mode)
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
    sources = list(args.transcript or [])
    if str(args.input).lower().endswith(".json"):
        data, upgraded = load_report(args.input)
        overrides = _parse_source_overrides(args)
        if sources:
            overrides.setdefault(default_source_id(data), Path(sources[0]))
        mode, checks = lint_report(data, args.mode, Path(args.input).resolve().parent, overrides, upgraded)
        sources = sources or [str(p) for p in overrides.values()] or [
            s["path"] for s in data.get("sources", []) if s.get("path")]
    else:
        mode, checks = lint_markdown(read_text(args.input), args.mode, sources)
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
            where = ("L%-4d" % ln) if isinstance(ln, int) else (ln or "     ")
            out.append("        %s%s %s" % (where, "" if sev == c["status"] else " (%s)" % sev.lower(), msg))
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
# Report JSON (schema v2): the single source of truth for render and validate
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "2.0"
SKILL_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = SKILL_DIR / "references" / "output-schema.json"
CSS_PATH = SKILL_DIR / "assets" / "html-report.css"

UNDERSTANDING_LEVELS = ["strong", "mixed", "thin", "unclear"]
SCHEMA_KEYWORDS = {"$schema", "$id", "$defs", "$ref", "title", "description", "type", "enum", "const",
                   "required", "properties", "additionalProperties", "items", "minItems", "minLength",
                   "pattern", "anyOf", "default", "examples"}
JSON_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def schema_errors(value, schema, root=None, path="$"):
    """Minimal JSON Schema validator for the keywords listed in SCHEMA_KEYWORDS."""
    root = root if root is not None else schema
    if "$ref" in schema:
        node = root
        for part in schema["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return schema_errors(value, node, root, path)
    errors = []
    if "anyOf" in schema:
        if all(schema_errors(value, s, root, path) for s in schema["anyOf"]):
            errors.append((path, "does not match any allowed shape"))
    if "const" in schema and value != schema["const"]:
        errors.append((path, "must be %s" % json.dumps(schema["const"])))
    if "enum" in schema and value not in schema["enum"]:
        errors.append((path, "%s is not one of %s" % (json.dumps(value, ensure_ascii=False)[:40],
                                                      ", ".join(map(str, schema["enum"])))))
    t = schema.get("type")
    if t:
        types = t if isinstance(t, list) else [t]
        ok = False
        for name in types:
            if name == "number":
                ok = ok or (isinstance(value, (int, float)) and not isinstance(value, bool))
            elif name == "integer":
                ok = ok or (isinstance(value, int) and not isinstance(value, bool))
            else:
                ok = ok or isinstance(value, JSON_TYPES[name])
        if not ok:
            return errors + [(path, "expected %s" % "/".join(types))]
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append((path, "must not be empty"))
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append((path, "%r does not match %s" % (value[:30], schema["pattern"])))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append((path, "needs at least %d item(s)" % schema["minItems"]))
        if "items" in schema:
            for i, item in enumerate(value):
                errors += schema_errors(item, schema["items"], root, "%s[%d]" % (path, i))
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append((path, "missing required field '%s'" % key))
        props = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in props:
                errors += schema_errors(item, props[key], root, "%s.%s" % (path, key))
            elif extra is False:
                errors.append((path, "unknown field '%s'" % key))
            elif isinstance(extra, dict):
                errors += schema_errors(item, extra, root, "%s.%s" % (path, key))
    return errors


def _status_in(text, default):
    m = re.search(r"\b(Confirmed|Inferred|Assumption|Needs validation)\b", text or "")
    return m.group(1) if m else default


def upgrade_v1(data):
    """Best-effort upgrade of a schema v1 report (no schemaVersion). Unknown statuses become explicit defaults."""
    if data.get("schemaVersion") == SCHEMA_VERSION:
        return data
    d = json.loads(json.dumps(data))
    meta = d.get("meta", {})
    m = re.search(r"\b([ABC])\b", meta.get("outputMode", ""))
    meta["outputMode"] = m.group(1) if m else "B"
    if "contextNote" in meta:
        meta["interactionContext"] = meta.pop("contextNote")
    out = {"schemaVersion": SCHEMA_VERSION, "meta": meta,
           "sources": [{"id": "S1", "label": "Source evidence", "layer": "source"}],
           "summary": d.get("summary", [])}
    for s in out["summary"]:
        s.pop("anchors", None)
    out["evidenceLayer"] = [{
        "title": ev.get("title", ""), "source": "S1", "status": ev.get("status", "Confirmed"),
        "notes": " · ".join(x for x in (ev.get("sourceType"), ev.get("sourceDate"), ev.get("notes")) if x),
        "points": [{"text": p} for p in ev.get("points", [])] or [{"text": ""}],
    } for ev in d.get("evidenceLayer", [])]
    out["projectThread"] = [{"label": t.get("dateLabel", ""), "title": t.get("title", ""), "body": t.get("body", ""),
                             "note": t.get("note", "")} for t in d.get("projectThread", [])]
    out["stakeholders"] = [{
        "party": s.get("party", ""), "role": s.get("role", ""), "statedPosition": s.get("statedPosition", ""),
        "apparentMotive": s.get("apparentMotive", ""), "status": s.get("status", "Inferred"),
        "strength": s.get("confidence", "Low"), "evidenceNote": s.get("evidenceBasis", ""),
    } for s in d.get("stakeholders", [])]
    rows = []
    for r in d.get("understandingMap", []):
        row = {"party": r.get("party", "")}
        for new, old in (("problem", "domainUnderstanding"), ("advancementPath", "workflowUnderstanding"),
                         ("deliveryConstraints", "deliveryUnderstanding"),
                         ("decisionMechanics", "organizationalUnderstanding")):
            raw = r.get(old, "")
            lv = re.split(r"[:：\s—-]", raw.strip(), 1)[0].lower()
            lv = "unclear" if lv.startswith("unclear") else lv
            row[new] = {"level": lv if lv in UNDERSTANDING_LEVELS else "unclear", "note": raw}
        rows.append(row)
    out["understandingMap"] = {"rows": rows, "readout": [r["commentary"] for r in d.get("understandingMap", [])
                                                         if r.get("commentary")]}
    a = d.get("audit", {})
    out["audit"] = {
        "supportedJudgments": [{"claim": x, "status": _status_in(x, "Inferred")} for x in a.get("supportedJudgments", [])],
        "weakJudgments": [{"claim": x, "status": _status_in(x, "Needs validation")} for x in a.get("weakJudgments", [])],
        "explicitAssumptions": [{"claim": x, "status": _status_in(x, "Assumption")}
                                for x in a.get("explicitAssumptions", [])],
        "validationTargets": a.get("validationTargets", []),
    }
    ac = d.get("actions", {})
    out["actions"] = {k: [{"text": x} for x in ac.get(k, [])] for k in ("doNow", "doLater", "validateBeforeCommit")}
    if ac.get("oneLinePositioning"):
        out["actions"]["oneLinePositioning"] = ac["oneLinePositioning"]
    out["references"] = [{"label": r.get("label", ""), "path": r.get("path", ""), "reason": r.get("reason", "")}
                         for r in d.get("references", [])]
    return out


def load_report(path):
    data = json.loads(read_text(path))
    upgraded = data.get("schemaVersion") != SCHEMA_VERSION
    return (upgrade_v1(data) if upgraded else data), upgraded


def iter_judgments(data):
    for i, ev in enumerate(data.get("evidenceLayer", [])):
        for j, u in enumerate(ev.get("evidenceNotes", [])):
            yield "evidenceLayer[%d].evidenceNotes[%d]" % (i, j), u
    for j, u in enumerate(data.get("threadNotes", [])):
        yield "threadNotes[%d]" % j, u
    audit = data.get("audit", {})
    for key in ("supportedJudgments", "weakJudgments", "explicitAssumptions"):
        for j, u in enumerate(audit.get(key, [])):
            yield "audit.%s[%d]" % (key, j), u


def iter_anchors(value, path="$"):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "anchors" and isinstance(item, list):
                for i, a in enumerate(item):
                    if isinstance(a, dict):
                        yield "%s.anchors[%d]" % (path, i), a
            else:
                for x in iter_anchors(item, "%s.%s" % (path, key)):
                    yield x
    elif isinstance(value, list):
        for i, item in enumerate(value):
            for x in iter_anchors(item, "%s[%d]" % (path, i)):
                yield x


def default_source_id(data):
    for s in data.get("sources", []):
        if s.get("layer") == "source":
            return s.get("id")
    return (data.get("sources") or [{}])[0].get("id")


def load_source_indexes(data, base_dir=None, overrides=None):
    """Return ({source_id: SourceIndex}, [(severity, path, message)])."""
    indexes, notes = {}, []
    overrides = dict(overrides or {})
    for i, s in enumerate(data.get("sources", [])):
        sid = s.get("id")
        path = overrides.pop(sid, None)
        if path is None and s.get("path"):
            path = Path(s["path"])
            if not path.is_absolute() and base_dir is not None:
                path = Path(base_dir) / path
        if path is None:
            continue
        if not Path(path).exists():
            notes.append(("WARN", "$.sources[%d].path" % i, "transcript not found: %s" % path))
            continue
        indexes[sid] = SourceIndex([path])
    for sid in overrides:
        notes.append(("FAIL", "--source", "unknown source id '%s'" % sid))
    return indexes, notes


def resolve_anchor(anchor, index):
    """Return a list of (severity, message) problems for one structured anchor."""
    problems = []
    speaker = anchor.get("speaker")
    label = None
    if speaker:
        label = index.aliases.get(speaker) or index.speaker_before(normalize(speaker))
        if not label:
            problems.append(("FAIL", "speaker '%s' does not appear in the transcript" % speaker))
    ts = anchor.get("ts")
    if ts:
        parts = re.split(r"[-~]", normalize(ts))
        secs = [ts_seconds(p) for p in parts]
        if len(secs) == 1:
            if not index.known_time(secs[0]):
                problems.append(("FAIL", "timestamp %s does not appear in the transcript" % ts))
            else:
                present = {t["speaker"] for t in index.turns_at(secs[0])}
                if label and present and label not in present:
                    problems.append(("FAIL", "%s is %s speaking, not %s" % (ts, " / ".join(sorted(present)), label)))
        else:
            lo, hi = min(secs), max(secs)
            if not index.span or lo < index.span[0] or hi > index.span[1]:
                problems.append(("FAIL", "range %s falls outside the transcript" % ts))
            elif label and not any(t["speaker"] == label and t["seconds"] is not None and lo <= t["seconds"] <= hi
                                   for t in index.turns):
                problems.append(("FAIL", "%s has no turn in %s" % (label, ts)))
    quote = anchor.get("quote")
    if quote:
        hits, found = index.find_quote(quote)
        if not found:
            problems.append(("FAIL", "quote not found in the transcript: \u201c%s\u201d" % quote[:40]))
        elif label and hits and label not in {t["speaker"] for t in hits}:
            problems.append(("FAIL", "quote \u201c%s\u201d is from %s, not %s" % (
                quote[:30], " / ".join(sorted({t["speaker"] for t in hits})), label)))
    return problems


def anchor_turn(anchor, index):
    """Best transcript turn for an anchor (for links and tooltips), or None."""
    label = index.aliases.get(anchor.get("speaker") or "")
    candidates = index.turns
    if anchor.get("ts"):
        first = ts_seconds(re.split(r"[-~]", normalize(anchor["ts"]))[0])
        candidates = index.turns_at(first) or [t for t in index.turns if t["seconds"] is not None and
                                                t["seconds"] >= first][:1]
    if anchor.get("quote"):
        hits, _ = index.find_quote(anchor["quote"])
        candidates = [t for t in candidates if t in hits] or hits or candidates
    if label:
        candidates = [t for t in candidates if t["speaker"] == label] or candidates
    return candidates[0] if candidates else None


def _checkable(anchors):
    return any(a.get("ts") or a.get("quote") for a in anchors or [])


def lint_report(data, mode=None, base_dir=None, overrides=None, upgraded=False):
    """Validate a schema v2 report: shape, protocol rules and anchor resolution. Returns (mode, checks)."""
    checks = []

    def add(cid, title, items, info=None):
        sev = {s for s, _, _ in items} - {"INFO"}
        status = "FAIL" if "FAIL" in sev else ("WARN" if sev else "PASS")
        checks.append({"id": cid, "title": title, "status": status, "items": items, "info": info})

    items = [("FAIL", p, m) for p, m in schema_errors(data, load_schema())]
    if upgraded:
        items.insert(0, ("WARN", "$", "schema v1 input was upgraded in memory; statuses without a tag were defaulted"))
    add("schema", "Matches references/output-schema.json (v%s)" % SCHEMA_VERSION, items)
    mode = (mode or data.get("meta", {}).get("outputMode") or "B").upper()
    if mode not in MODE_REQUIRED:
        mode = "B"

    items = []
    for path, value in _iter_strings(data):
        if any(rx.search(value) for rx in PLACEHOLDER_RES):
            items.append(("FAIL", path, "unfilled placeholder: %s" % value[:60]))
    add("placeholders", "No unfilled template placeholders", items)

    items = []
    if mode in ("B", "C"):
        if not data.get("projectThread"):
            items.append(("FAIL", "$.projectThread", "Project Thread is empty"))
        if not data.get("stakeholders"):
            items.append(("FAIL", "$.stakeholders", "Stakeholder Motive Readout is empty"))
        um = data.get("understandingMap") or {}
        if not um.get("rows") and not um.get("omittedReason"):
            items.append(("FAIL", "$.understandingMap", "Participant Understanding Map needs rows or omittedReason"))
    if mode == "C":
        audit = data.get("audit") or {}
        if not any(audit.get(k) for k in ("supportedJudgments", "weakJudgments", "explicitAssumptions")):
            items.append(("FAIL", "$.audit", "Judgment and Reverse Audit has no judgments"))
    add("sections", "Required sections for Mode %s" % mode, items)

    judgments = list(iter_judgments(data))
    need = 1 if mode == "A" else 3
    tagged = len(judgments) + len(data.get("stakeholders", []))
    add("tagged", "At least %d judgment(s) carry Status tags" % need,
        [] if tagged >= need else [("FAIL", "$", "found %d tagged judgment(s)" % tagged)], "%d tagged" % tagged)

    layers = {s.get("id"): s.get("layer") for s in data.get("sources", [])}
    gate, confirmed, later = [], [], []
    for path, u in judgments:
        status, claim = u.get("status"), u.get("claim", "")
        risky = u.get("highRiskType") or (HIGH_RISK_RE.search(claim) and HIGH_RISK_RE.search(claim).group(0))
        anchors = u.get("anchors") or []
        if status == "Confirmed" and (u.get("basis") == "Later reasoning only" or (anchors and all(
                layers.get(a.get("source")) == "later_reasoning" for a in anchors))):
            later.append(("FAIL", path, "Confirmed claim supported only by later reasoning"))
        if status == "Confirmed" and anchors and all(layers.get(a.get("source")) == "context" for a in anchors):
            later.append(("WARN", path, "Confirmed claim anchored only in user context"))
        if not risky:
            continue
        if status in ("Confirmed", "Inferred") and not _checkable(anchors):
            gate.append(("FAIL", path, "high-risk %s claim (%s) needs an anchor with ts or quote" % (status, risky)))
        if status in ("Assumption", "Needs validation") and not u.get("toValidate"):
            gate.append(("WARN", path, "high-risk %s claim (%s) should say what would validate it" % (status, risky)))
        if status == "Confirmed" and not any(a.get("quote") for a in anchors):
            confirmed.append(("FAIL", path, "Confirmed high-risk claim without a verbatim quote anchor"))
    for i, s in enumerate(data.get("stakeholders", [])):
        path = "stakeholders[%d]" % i
        if not _checkable(s.get("anchors")):
            gate.append(("FAIL", path, "motive readout for %s needs an anchor with ts or quote" % s.get("party")))
        if s.get("status") == "Confirmed" and not any(a.get("quote") for a in s.get("anchors") or []):
            confirmed.append(("FAIL", path, "Confirmed motive readout without a verbatim quote anchor"))
    add("gate-anchors", "High-risk claims carry source anchors", gate)
    add("gate-confirmed", "No Confirmed high-risk claim without a verbatim quote", confirmed)
    add("later-reasoning", "Later reasoning is never Confirmed", later)

    if mode in ("B", "C"):
        items = []
        do_now = (data.get("actions") or {}).get("doNow") or []
        if not do_now:
            items.append(("FAIL", "$.actions.doNow", "Do now is empty"))
        for i, a in enumerate(do_now):
            if not _checkable(a.get("anchors")) and not TS_RE.search(normalize(a.get("text", ""))):
                items.append(("FAIL", "actions.doNow[%d]" % i, "Do-now action without evidence: %s" % a.get("text", "")[:50]))
        add("actions", "Do-now actions carry evidence", items)

    indexes, items = load_source_indexes(data, base_dir, overrides)
    default = default_source_id(data)
    total = 0
    for path, a in iter_anchors(data):
        sid = a.get("source") or default
        if sid not in layers:
            items.append(("FAIL", path, "unknown source id '%s'" % sid))
            continue
        index = indexes.get(sid)
        if index is None:
            continue
        total += 1
        for sev, msg in resolve_anchor(a, index):
            items.append((sev, path, msg))
    if indexes:
        add("anchors", "Anchors resolve to the source transcript", items,
            "%d anchor(s) checked against %d source(s)" % (total, len(indexes)))
    else:
        add("anchors", "Anchors resolve to the source transcript",
            items + [("WARN", "$.sources", "not verified: give sources a path or pass --source ID=PATH")])
    return mode, checks


def _iter_strings(value, path="$"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            for x in _iter_strings(v, "%s.%s" % (path, k)):
                yield x
    elif isinstance(value, list):
        for i, v in enumerate(value):
            for x in _iter_strings(v, "%s[%d]" % (path, i)):
                yield x


# ---------------------------------------------------------------------------
# Audience redaction
# ---------------------------------------------------------------------------

SENSITIVE_RISK = {"motive", "intent", "bad_faith", "political"}


def redact(data, audience):
    """Return (copy of data for the audience, list of removal notes)."""
    d = json.loads(json.dumps(data))
    removed = []
    if audience == "internal":
        return d, removed

    def drop_judgments(keep):
        n = 0
        for key in ("supportedJudgments", "weakJudgments", "explicitAssumptions"):
            items = d.get("audit", {}).get(key)
            if items:
                kept = [u for u in items if keep(u)]
                n += len(items) - len(kept)
                d["audit"][key] = kept
        notes = d.get("threadNotes")
        if notes:
            kept = [u for u in notes if keep(u)]
            n += len(notes) - len(kept)
            d["threadNotes"] = kept
        return n

    if d.get("audit", {}).get("suspiciousActions"):
        removed.append(("suspiciousActions", len(d["audit"].pop("suspiciousActions"))))
    n = drop_judgments(lambda u: not (u.get("highRiskType") in SENSITIVE_RISK and u.get("status") != "Confirmed"))
    if n:
        removed.append(("sensitiveJudgments", n))
    n = 0
    for s in d.get("stakeholders", []):
        if s.get("status") != "Confirmed" and s.get("apparentMotive"):
            s["apparentMotive"] = ""
            n += 1
    if n:
        removed.append(("apparentMotive", n))
    if audience == "external":
        for key in ("stakeholders", "understandingMap", "influenceChain", "claimLedger", "minutesCheck", "threadNotes"):
            if d.get(key):
                value = d.pop(key)
                removed.append((key, len(value.get("rows", [])) if isinstance(value, dict) else len(value)))
        audit = d.get("audit")
        if audit:
            n = drop_judgments(lambda u: u.get("status") == "Confirmed")
            for key in ("estimateRisks", "consensusCheck", "userNarrative"):
                audit.pop(key, None)
            if n:
                removed.append(("unconfirmedJudgments", n))
        for s in d.get("sources", []):
            s.pop("path", None)
        d.pop("methodNotes", None)
    return d, removed


# ---------------------------------------------------------------------------
# Render: Markdown
# ---------------------------------------------------------------------------

def md_cell(text):
    return re.sub(r"\s+", " ", str(text or "")).replace("|", "\\|").strip() or "-"


def md_anchor(a):
    bits = [x for x in (a.get("speaker"), a.get("ts")) if x]
    s = " ".join(bits)
    if a.get("quote"):
        s += (" " if s else "") + "\u201c%s\u201d" % a["quote"]
    if a.get("note"):
        s += (" " if s else "") + "(%s)" % a["note"]
    return s


def md_anchors(anchors):
    return "; ".join(md_anchor(a) for a in anchors or [] if md_anchor(a))


def md_judgment(u, indent="  "):
    lines = [indent + "- `Claim`: " + u.get("claim", ""), indent + "- `Status`: " + u.get("status", "")]
    if u.get("strength"):
        lines.append(indent + "- `Strength`: " + u["strength"])
    if u.get("basis"):
        lines.append(indent + "- `Basis`: " + u["basis"] + (" (%s)" % u["note"] if u.get("note") else ""))
    elif u.get("note"):
        lines.append(indent + "- `Basis`: " + u["note"])
    if u.get("anchors"):
        lines.append(indent + "- `Source anchor`: " + md_anchors(u["anchors"]))
    if u.get("toValidate"):
        lines.append(indent + "- `What would validate it`: " + u["toValidate"])
    return lines


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for r in rows:
        out.append("| " + " | ".join(md_cell(c) for c in r) + " |")
    return out


def render_markdown(data):
    m = data["meta"]
    out = ["# " + m.get("reportTitle", ""), ""]
    head = "Mode %s" % m.get("outputMode", "")
    head += "".join(" · " + m[k] for k in ("reportDate", "projectStage") if m.get(k))
    out += ["> " + head]
    if m.get("lead"):
        out += [">", "> " + m["lead"]]
    out.append("")
    if data.get("summary"):
        out += ["## Summary", ""]
        for s in data["summary"]:
            line = "- `%s` **%s**" % (s["status"], s["headline"])
            if s.get("body"):
                line += " - " + s["body"]
            if s.get("anchors"):
                line += " `Source anchor: %s`" % md_anchors(s["anchors"])
            out.append(line)
        out.append("")

    out += ["## " + SECTION_TITLES["fact"], ""]
    out.append("- **Source set**: " + "; ".join(
        "%s %s (%s%s)" % (s["id"], s["label"], s["layer"], ", " + s["type"] if s.get("type") else "")
        for s in data.get("sources", [])))
    for key, label in (("interactionContext", "Interaction context"), ("analysisWindow", "Analysis window"),
                       ("noiseNote", "Noise")):
        if m.get(key):
            out.append("- **%s**: %s" % (label, m[key]))
    out.append("- **What was said**:")
    for ev in data.get("evidenceLayer", []):
        out.append("  - **%s**%s" % (ev["title"], " (%s)" % ev["notes"] if ev.get("notes") else ""))
        for p in ev.get("points", []):
            line = "    - " + p["text"]
            if p.get("anchors"):
                line += " `Source anchor: %s`" % md_anchors(p["anchors"])
            out.append(line)
    if data.get("openQuestions"):
        out.append("- **Open factual gaps**:")
        out += ["  - " + q for q in data["openQuestions"]]
    notes = [u for ev in data.get("evidenceLayer", []) for u in ev.get("evidenceNotes", [])]
    if notes:
        out.append("- **Evidence notes**:")
        for u in notes:
            out += md_judgment(u)
    out.append("")
    if data.get("decisions"):
        out += ["### Decision Ledger", ""]
        out += md_table(DECISION_COLUMNS,
                        [[d.get("id") or "D%d" % (i + 1), d["decision"], d.get("decidedBy"), d.get("owner"),
                          d.get("due"), d["status"], d.get("followUp"), md_anchors(d.get("anchors"))]
                         for i, d in enumerate(data["decisions"])])
        out.append("")
    if data.get("minutesCheck"):
        out += ["### Minutes vs Recording", ""]
        out += md_table(MINUTES_COLUMNS,
                        [[r["written"], r["spoken"], r["verdict"], md_anchors(r.get("anchors"))]
                         for r in data["minutesCheck"]])
        out.append("")
    if data.get("claimLedger"):
        out += ["### Claim Ledger", ""]
        out += md_table(CLAIM_COLUMNS,
                        [[c["claim"], c.get("claimant"), c.get("support"), c.get("counter"), c["status"],
                          md_anchors(c.get("anchors"))] for c in data["claimLedger"]])
        out.append("")

    if data.get("projectThread") or data.get("threadNotes"):
        out += ["## " + SECTION_TITLES["thread"], ""]
        for t in data.get("projectThread", []):
            line = "- **%s%s**: %s" % (t["label"] + " · " if t.get("label") else "", t["title"], t["body"])
            if t.get("note"):
                line += " (%s)" % t["note"]
            if t.get("anchors"):
                line += " `Source anchor: %s`" % md_anchors(t["anchors"])
            out.append(line)
        if data.get("threadNotes"):
            out.append("- **Evidence-risk notes**:")
            for u in data["threadNotes"]:
                out += md_judgment(u)
        out.append("")
    if data.get("influenceChain"):
        out += ["## " + SECTION_TITLES["chain"], ""]
        out += md_table(CHAIN_COLUMNS,
                        [[c["actor"], c["move"], c.get("adoptedBy"), c.get("effect"), md_anchors(c.get("anchors")),
                          c["status"], c.get("strength"), c.get("riskIfWrong")] for c in data["influenceChain"]])
        out.append("")
    if data.get("stakeholders"):
        out += ["## " + SECTION_TITLES["motive"], ""]
        out += md_table(MOTIVE_COLUMNS,
                        [["%s%s" % (s["party"], " (%s)" % s["role"] if s.get("role") else ""), s["statedPosition"],
                          s["apparentMotive"], s["status"], s["strength"],
                          "; ".join(x for x in (md_anchors(s.get("anchors")), s.get("evidenceNote")) if x)]
                         for s in data["stakeholders"]])
        out.append("")
    um = data.get("understandingMap")
    if um:
        out += ["## " + SECTION_TITLES["map"], ""]
        if um.get("rows"):
            out += md_table(MAP_COLUMNS,
                            [[r["party"]] + ["%s%s" % (r[k]["level"], " - " + r[k]["note"] if r[k].get("note") else "")
                                             for k, _, _ in MAP_DIMENSIONS] + [md_anchors(r.get("anchors"))]
                             for r in um["rows"]])
            out.append("")
        if um.get("omittedReason"):
            out += ["Participant Understanding Map omitted due to %s" % um["omittedReason"].rstrip(".") + ".", ""]
        if um.get("readout"):
            out += ["**Readout:**"] + ["- " + x for x in um["readout"]] + [""]

    audit = data.get("audit")
    if audit:
        out += ["## " + SECTION_TITLES["audit"], ""]
        if audit.get("userNarrative"):
            out.append("- **User's current narrative**: " + audit["userNarrative"])
        for key, label in (("supportedJudgments", "Judgments that look supported"),
                           ("weakJudgments", "Judgments that need stronger evidence"),
                           ("explicitAssumptions", "Assumptions to keep explicit")):
            if audit.get(key):
                out.append("- **%s**:" % label)
                for u in audit[key]:
                    out += md_judgment(u)
        if audit.get("estimateRisks"):
            out.append("- **Likely overestimates / underestimates**:")
            out += ["  - " + x for x in audit["estimateRisks"]]
        if audit.get("suspiciousActions"):
            out.append("- **Suspicious actions requiring lower-intent alternatives**:")
            for s in audit["suspiciousActions"]:
                out += ["  - `Action or contradiction`: " + s["action"],
                        "  - `Information-change explanation`: " + s["informationChange"],
                        "  - `Pressure or misjudgment explanation`: " + s["pressureOrMisjudgment"],
                        "  - `Strategic-misdirection explanation`: " + s["strategicMisdirection"],
                        "  - `Current status`: " + s["status"]]
                if s.get("anchors"):
                    out.append("  - `Source anchor`: " + md_anchors(s["anchors"]))
        if audit.get("consensusCheck"):
            out.append("- **Consensus reality check**:")
            out += ["  - " + x for x in audit["consensusCheck"]]
        if audit.get("validationTargets"):
            out.append("- **High-impact claims requiring validation**:")
            out += ["  - " + x for x in audit["validationTargets"]]
        out.append("")

    ac = data.get("actions", {})
    out += ["## " + SECTION_TITLES["actions"], ""]
    for key, label in (("doNow", "Do now"), ("doLater", "Do later"),
                       ("validateBeforeCommit", "Must validate before deeper commitment")):
        items = ac.get(key) or []
        if not items and key != "doNow":
            continue
        out.append("- **%s**:" % label)
        for a in items:
            extra = ", ".join(x for x in ("owner: " + a["owner"] if a.get("owner") else "",
                                          "due: " + a["due"] if a.get("due") else "") if x)
            line = "  - " + a["text"] + (" (%s)" % extra if extra else "")
            if a.get("anchors"):
                line += " `Evidence: %s`" % md_anchors(a["anchors"])
            out.append(line)
    if ac.get("oneLinePositioning"):
        out.append("- **One-line positioning**: " + ac["oneLinePositioning"])
    out.append("")
    if data.get("methodNotes"):
        out += ["## " + SECTION_TITLES["method"], ""] + ["- " + x for x in data["methodNotes"]] + [""]
    if data.get("references"):
        out += ["## References", ""]
        out += ["- %s%s - %s" % (r["label"], " (`%s`)" % r["path"] if r.get("path") else "", r["reason"])
                for r in data["references"]]
        out.append("")
    return "\n".join(out).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Render: HTML
# ---------------------------------------------------------------------------

STATUS_CLASS = {"Confirmed": "t-confirmed", "Inferred": "t-inferred", "Assumption": "t-assumption",
                "Needs validation": "t-needs"}
VERDICT_CLASS = {"consistent": "t-confirmed", "partial": "t-assumption", "inconsistent": "t-needs"}
LABELS = {
    "zh": {
        "evidenceFirst": "证据优先", "date": "日期", "stage": "阶段", "context": "交互语境", "window": "分析窗口",
        "audience": "受众", "summary": "当前总结", "summarySub": "最关键的结论，每条都标注证据状态。",
        "fact": "结构化事实记录", "factSub": "按来源记录“谁说了什么”，不掺判断。说过不等于为真。",
        "sources": "输入材料", "layer": {"source": "原始证据", "context": "背景补充", "later_reasoning": "事后推理"},
        "gaps": "待补的事实缺口", "evidenceNotes": "证据备注", "riskNotes": "证据风险备注",
        "decisions": "决策台账", "decisionsSub": "会上实际做出的决定、谁做的，以及之后是否被改写。",
        "minutes": "书面纪要 vs 录音原话", "minutesSub": "逐条比对会后书面结论与逐字稿。",
        "claims": "主张台账", "claimsSub": "只评价主张的证据状态，不评价人。",
        "thread": "项目脉络", "threadSub": "状态如何走到今天，核心张力是什么。",
        "chain": "推进 / 影响链", "chainSub": "谁引入了框架，谁采纳或放大，它改变了哪个决定。",
        "motive": "相关方动机解读", "motiveSub": "各方说了什么，与看起来想要什么。动机属于高风险判断，必须有锚点。",
        "map": "参与者理解地图", "mapSub": "谁在哪一层真正理解了问题。",
        "audit": "判断与反向审计", "auditSub": "挑战主导叙事：哪些判断站得住，哪些太顺。",
        "narrative": "用户当前叙事", "supported": "支持度较强的判断", "weak": "需要更强证据",
        "assumptions": "必须保持显式的假设", "validate": "承诺前要验证的高影响判断",
        "estimates": "可能高估 / 低估", "suspicious": "可疑行为的三种解释", "consensus": "共识真实性检查",
        "infoChange": "信息变化", "pressure": "压力或误判", "misdirection": "策略性误导",
        "actions": "当前行动", "actionsSub": "立即做 / 稍后做 / 承诺前必须验证。",
        "doNow": "立即做", "doLater": "稍后做", "validateBeforeCommit": "承诺前必须验证",
        "positioning": "一句话定位", "method": "方法笔记", "references": "来源参考",
        "appendix": "附录 · 逐字稿（锚点目标）", "expand": "展开全部发言",
        "filter": "只看", "all": "全部", "print": "打印 / PDF", "exportReport": "导出报告 JSON",
        "exportDecisions": "导出决策台账 JSON", "exportClaims": "导出主张台账 CSV", "exportActions": "导出行动 CSV",
        "owner": "负责人", "due": "截止", "colon": "\uff1a", "layerName": "层级", "details": "说明", "toValidate": "如何验证", "risk": "若判断错",
        "party": "相关方", "says": "说了什么", "wants": "看起来想要", "status": "状态", "strength": "强度",
        "anchor": "锚点", "decision": "决定", "decidedBy": "决定者", "followUp": "后续", "written": "书面结论",
        "spoken": "录音原话", "verdict": "一致性", "claim": "主张", "claimant": "提出者", "support": "会上依据",
        "counter": "反证 / 修正", "actor": "行动者", "move": "引入的说法或动作", "adoptedBy": "采纳 / 放大",
        "effect": "影响的决定", "label": "来源", "path": "路径", "reason": "用途",
        "verdicts": {"consistent": "一致", "partial": "部分一致", "inconsistent": "不一致"},
        "levels": {"strong": "强", "mixed": "部分", "thin": "弱", "unclear": "材料不足"},
        "omitted": "理解地图未输出：", "unresolved": "未在逐字稿中找到", "redacted": "本版本面向 %s，已移除：",
        "redactions": {"suspiciousActions": "可疑行为分析", "sensitiveJudgments": "未确认的动机/意图类判断",
                       "apparentMotive": "未确认的动机推断", "stakeholders": "相关方动机解读",
                       "understandingMap": "参与者理解地图", "influenceChain": "推进/影响链",
                       "claimLedger": "主张台账", "minutesCheck": "纪要比对", "threadNotes": "脉络风险备注",
                       "unconfirmedJudgments": "未确认的判断"},
        "legend": "标签说明：", "footer": "本报告遵循证据优先原则：已确认 = 原始材料直接支持；推断 = 基于材料的合理解读；"
                                       "假设 = 尚未充分支持的工作假设；待验证 = 用于承诺、定价或战略前必须核实。",
        "statusNames": {"Confirmed": "已确认", "Inferred": "推断", "Assumption": "假设", "Needs validation": "待验证"},
    },
    "en": {
        "evidenceFirst": "Evidence first", "date": "Date", "stage": "Stage", "context": "Context", "window": "Window",
        "audience": "Audience", "summary": "Summary", "summarySub": "Top conclusions, each tagged with its evidence status.",
        "fact": "Structured Fact Record", "factSub": "What was said, per source. Said is not the same as true.",
        "sources": "Input stack", "layer": {"source": "source evidence", "context": "context",
                                            "later_reasoning": "later reasoning"},
        "gaps": "Open factual gaps", "evidenceNotes": "Evidence notes", "riskNotes": "Evidence-risk notes",
        "decisions": "Decision Ledger", "decisionsSub": "Decisions actually made, by whom, and whether they were rewritten.",
        "minutes": "Minutes vs Recording", "minutesSub": "Written conclusions compared with the transcript.",
        "claims": "Claim Ledger", "claimsSub": "Scores the evidence behind claims, not the people.",
        "thread": "Project Thread", "threadSub": "How the project got here and where the tension sits.",
        "chain": "Advancement / Influence Chain", "chainSub": "Who introduced a frame, who adopted it, what it changed.",
        "motive": "Stakeholder Motive Readout",
        "motiveSub": "What each party says versus what they appear to want. Motive is a high-risk claim and needs anchors.",
        "map": "Participant Understanding Map", "mapSub": "Who understands which layer of the problem.",
        "audit": "Judgment and Reverse Audit", "auditSub": "Challenges the dominant narrative.",
        "narrative": "User's current narrative", "supported": "Judgments that look supported",
        "weak": "Judgments that need stronger evidence", "assumptions": "Assumptions to keep explicit",
        "validate": "High-impact claims requiring validation", "estimates": "Likely overestimates / underestimates",
        "suspicious": "Suspicious actions: three explanations", "consensus": "Consensus reality check",
        "infoChange": "Information change", "pressure": "Pressure or misjudgment",
        "misdirection": "Strategic misdirection",
        "actions": "Current Actions", "actionsSub": "Do now / do later / validate before committing.",
        "doNow": "Do now", "doLater": "Do later", "validateBeforeCommit": "Validate before commit",
        "positioning": "One-line positioning", "method": "Method Notes", "references": "Sources",
        "appendix": "Appendix · Transcript (anchor targets)", "expand": "Show all turns",
        "filter": "Show", "all": "All", "print": "Print / PDF", "exportReport": "Export report JSON",
        "exportDecisions": "Export decisions JSON", "exportClaims": "Export claims CSV",
        "exportActions": "Export actions CSV",
        "owner": "Owner", "due": "Due", "colon": ": ", "layerName": "Layer", "details": "Details", "toValidate": "To validate", "risk": "Risk if wrong",
        "party": "Party", "says": "What they say", "wants": "Appears to want", "status": "Status",
        "strength": "Strength", "anchor": "Anchor", "decision": "Decision", "decidedBy": "Decided by",
        "followUp": "Follow-up", "written": "Written", "spoken": "Spoken", "verdict": "Verdict", "claim": "Claim",
        "claimant": "Claimant", "support": "Support", "counter": "Counter / correction", "actor": "Actor",
        "move": "Move", "adoptedBy": "Adopted by", "effect": "Effect", "label": "Source", "path": "Path",
        "reason": "Use",
        "verdicts": {"consistent": "consistent", "partial": "partial", "inconsistent": "inconsistent"},
        "levels": {"strong": "strong", "mixed": "mixed", "thin": "thin", "unclear": "unclear"},
        "omitted": "Understanding map omitted: ", "unresolved": "not found in the transcript",
        "redacted": "This version is for %s. Removed:",
        "redactions": {"suspiciousActions": "suspicious-action analysis",
                       "sensitiveJudgments": "unconfirmed motive or intent judgments",
                       "apparentMotive": "unconfirmed motive readings", "stakeholders": "stakeholder motive readout",
                       "understandingMap": "understanding map", "influenceChain": "influence chain",
                       "claimLedger": "claim ledger", "minutesCheck": "minutes check", "threadNotes": "thread risk notes",
                       "unconfirmedJudgments": "unconfirmed judgments"},
        "legend": "Legend:", "footer": "Evidence first. Confirmed = directly supported by the source; Inferred = "
                                       "grounded interpretation; Assumption = working hypothesis; Needs validation = "
                                       "check before using it for commitment, pricing or strategy.",
        "statusNames": {"Confirmed": "Confirmed", "Inferred": "Inferred", "Assumption": "Assumption",
                        "Needs validation": "Needs validation"},
    },
}

HTML_JS = r"""
(function(){
var data=JSON.parse(document.getElementById('report-data').textContent);
document.querySelectorAll('.filter [data-f]').forEach(function(b){b.addEventListener('click',function(){
 var f=b.getAttribute('data-f');
 document.querySelectorAll('.filter [data-f]').forEach(function(x){x.classList.toggle('on',x===b);});
 document.querySelectorAll('[data-s]').forEach(function(n){n.classList.toggle('dim',f!=='all'&&n.getAttribute('data-s')!==f);});
});});
function dl(name,text,type){var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:type}));
 a.download=name;document.body.appendChild(a);a.click();a.remove();}
function anchors(list){return (list||[]).map(function(a){return [a.speaker,a.ts,a.quote?'\u201c'+a.quote+'\u201d':''].filter(Boolean).join(' ');}).join('; ');}
function csv(rows,keys){var q=function(s){return '"'+String(s==null?'':s).replace(/"/g,'""')+'"';};
 return '\ufeff'+[keys.join(',')].concat(rows.map(function(r){return keys.map(function(k){return q(k==='anchors'?anchors(r.anchors):r[k]);}).join(',');})).join('\n');}
var on=function(id,fn){var el=document.getElementById(id);if(el)el.addEventListener('click',fn);};
on('exp-report',function(){dl('report.json',JSON.stringify(data,null,2),'application/json');});
on('exp-decisions',function(){dl('decision-ledger.json',JSON.stringify(data.decisions||[],null,2),'application/json');});
on('exp-claims',function(){dl('claim-ledger.csv',csv(data.claimLedger||[],['claim','claimant','support','counter','status','strength','anchors']),'text/csv');});
on('exp-actions',function(){var a=data.actions||{},rows=[];['doNow','doLater','validateBeforeCommit'].forEach(function(k){(a[k]||[]).forEach(function(x){rows.push(Object.assign({lane:k},x));});});
 dl('actions.csv',csv(rows,['lane','text','owner','due','status','anchors']),'text/csv');});
document.querySelectorAll('a.anc[href^="#t-"]').forEach(function(a){a.addEventListener('click',function(){
 var d=document.querySelector('details.tx-wrap');if(d)d.open=true;});});
})();
"""


def _esc(text):
    import html
    return html.escape(str(text if text is not None else ""), quote=True)


class HtmlRenderer:
    def __init__(self, data, indexes, lang, removed, audience):
        self.d = data
        self.idx = indexes
        self.L = LABELS["zh" if lang.lower().startswith("zh") else "en"]
        self.removed = removed
        self.audience = audience
        self.default = default_source_id(data)
        self.anchored = {}

    def tag(self, status):
        if not status:
            return ""
        return '<span class="tag %s" title="%s">%s</span>' % (
            STATUS_CLASS.get(status, "t-context"), _esc(self.L["statusNames"].get(status, status)), _esc(status))

    def strength(self, value):
        return '<span class="tag s-%s">%s</span>' % (_esc(value.lower()), _esc(value)) if value else ""

    def turn_id(self, sid, turn):
        return "t-%s-%s" % (sid, turn["seconds"] if turn["seconds"] is not None else turn["id"])

    def anchor(self, a):
        sid = a.get("source") or self.default
        text = " ".join(x for x in (re.sub(r"^[A-Za-z]\s+", "", a.get("speaker") or ""), a.get("ts")) if x)
        if a.get("quote"):
            q = a["quote"] if len(a["quote"]) <= 18 else a["quote"][:17] + "\u2026"
            text += (" " if text else "") + "\u201c%s\u201d" % q
        if not text:
            text = a.get("note", "")
        index = self.idx.get(sid)
        if index is None:
            return '<span class="anc">%s</span>' % _esc(text)
        problems = resolve_anchor(a, index)
        turn = anchor_turn(a, index)
        if problems:
            reason = "; ".join(m for _, m in problems)
            return '<span class="anc bad" title="%s">%s</span>' % (_esc(reason), _esc(text))
        if not turn:
            return '<a class="anc" href="#src-%s" title="%s">%s</a>' % (_esc(sid), _esc(a.get("quote") or ""), _esc(text))
        tip = "%s %s\uff1a%s" % (turn["speaker"], turn["ts"] or "", turn["text"][:160])
        return '<a class="anc" href="#%s" title="%s">%s</a>' % (self.turn_id(sid, turn), _esc(tip), _esc(text))

    def anchors(self, anchors):
        if not anchors:
            return ""
        return '<span class="ancs">%s</span>' % " ".join(self.anchor(a) for a in anchors)

    def text(self, value):
        """Escape and link bare timestamps to transcript turns of the default source."""
        s = _esc(value)
        index = self.idx.get(self.default)
        if not index:
            return s

        def link(m):
            turns = index.turns_at(ts_seconds(m.group(1)))
            if not turns:
                return m.group(0)
            t = turns[0]
            tip = "%s\uff1a%s" % (t["speaker"], t["text"][:160])
            return '<a class="anc ts" href="#%s" title="%s">%s</a>' % (self.turn_id(self.default, t), _esc(tip),
                                                                      m.group(1))
        return TS_RE.sub(link, s)

    def judgment(self, u):
        parts = ['<li data-s="%s">' % _esc(u.get("status")), self.text(u.get("claim")), " ", self.tag(u.get("status")),
                 " ", self.strength(u.get("strength"))]
        if u.get("basis"):
            parts.append(' <span class="tag t-context">%s</span>' % _esc(u["basis"]))
        if u.get("anchors"):
            parts.append(" " + self.anchors(u["anchors"]))
        if u.get("note"):
            parts.append('<div class="note">%s</div>' % self.text(u["note"]))
        if u.get("toValidate"):
            parts.append('<div class="note"><strong>%s%s</strong>%s</div>' % (
                _esc(self.L["toValidate"]), self.L["colon"], self.text(u["toValidate"])))
        parts.append("</li>")
        return "".join(parts)

    def section(self, key, sub, body, sid=None):
        return '<section class="section" id="%s"><h2>%s</h2><p class="sub">%s</p>%s</section>' % (
            sid or key, _esc(self.L[key]), _esc(sub) if sub else "", body)

    def table(self, headers, rows, statuses=None):
        out = ['<div class="tbl-wrap"><table><thead><tr>', "".join("<th>%s</th>" % _esc(h) for h in headers),
               "</tr></thead><tbody>"]
        for i, r in enumerate(rows):
            attr = ' data-s="%s"' % _esc(statuses[i]) if statuses and statuses[i] else ""
            out.append("<tr%s>%s</tr>" % (attr, "".join("<td>%s</td>" % c for c in r)))
        out.append("</tbody></table></div>")
        return "".join(out)

    def render(self, css):
        d, L, m = self.d, self.L, self.d["meta"]
        lang = "zh-CN" if L is LABELS["zh"] else (m.get("language") or "en")
        o = ['<!DOCTYPE html><html lang="%s"><head><meta charset="UTF-8">' % _esc(lang),
             '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
             '<meta name="generator" content="biz-retro-analyzer %s">' % VERSION,
             "<title>%s</title><style>%s</style></head><body><main class=\"page\">" % (_esc(m["reportTitle"]), css)]
        mode_names = {"A": "Mode A · Fact Pack", "B": "Mode B · Retro Pack", "C": "Mode C · Audit Pack"}
        o.append('<header class="hero"><p class="eyebrow">%s · %s</p><h1>%s</h1>' % (
            _esc(mode_names.get(m.get("outputMode"), m.get("outputMode"))), _esc(L["evidenceFirst"]),
            _esc(m["reportTitle"])))
        if m.get("lead"):
            o.append('<p class="lead">%s</p>' % self.text(m["lead"]))
        chips = [(L["date"], m.get("reportDate")), (L["stage"], m.get("projectStage")),
                 (L["context"], m.get("interactionContext")), (L["window"], m.get("analysisWindow")),
                 (L["audience"], self.audience)]
        o.append('<div class="hero-meta">%s</div>' % "".join(
            '<span class="chip"><strong>%s</strong> %s</span>' % (_esc(k), _esc(v)) for k, v in chips if v))
        for key in ("subtitle", "noiseNote"):
            if m.get(key):
                o.append('<div class="hero-note">%s</div>' % self.text(m[key]))
        o.append("</header>")
        if self.removed:
            names = ", ".join("%s (%d)" % (L["redactions"].get(k, k), n) for k, n in self.removed)
            o.append('<div class="callout warn audience-note"><strong>%s</strong> %s</div>' % (
                _esc(L["redacted"] % self.audience), _esc(names)))

        o.append('<nav class="filter" aria-label="filter"><span>%s</span>' % _esc(L["filter"]))
        for st, cls in STATUS_CLASS.items():
            o.append('<button type="button" data-f="%s" class="tag %s">%s</button>' % (_esc(st), cls, _esc(st)))
        o.append('<button type="button" data-f="all" class="tag t-context on">%s</button><span class="sp"></span>' %
                 _esc(L["all"]))
        o.append('<button type="button" id="exp-report" class="tag t-context">%s</button>' % _esc(L["exportReport"]))
        if d.get("decisions"):
            o.append('<button type="button" id="exp-decisions" class="tag t-context">%s</button>' %
                     _esc(L["exportDecisions"]))
        if d.get("claimLedger"):
            o.append('<button type="button" id="exp-claims" class="tag t-context">%s</button>' % _esc(L["exportClaims"]))
        o.append('<button type="button" id="exp-actions" class="tag t-context">%s</button>' % _esc(L["exportActions"]))
        o.append('<button type="button" onclick="window.print()" class="tag t-context">%s</button></nav>' %
                 _esc(L["print"]))

        if d.get("summary"):
            cards = "".join(
                '<div class="card sum-card" data-s="%s">%s %s <span class="anchor">%s</span><div class="headline">%s'
                '</div><p>%s</p>%s</div>' % (_esc(s["status"]), self.tag(s["status"]), self.strength(s.get("strength")),
                                             _esc(s.get("label")), _esc(s["headline"]), self.text(s.get("body")),
                                             self.anchors(s.get("anchors"))) for s in d["summary"])
            o.append(self.section("summary", L["summarySub"], '<div class="card-grid">%s</div>' % cards))

        body = [self.table([L["label"], L["layerName"], L["details"]], [
            ["<strong>%s</strong> %s" % (_esc(s["id"]), _esc(s["label"])),
             '<span class="tag layer-%s">%s</span>' % (_esc(s["layer"]), _esc(L["layer"].get(s["layer"], s["layer"]))),
             _esc(" · ".join(x for x in (s.get("type"), s.get("date"), s.get("speakerAttribution"), s.get("note")) if x))]
            for s in d.get("sources", [])])]
        for ev in d.get("evidenceLayer", []):
            pts = "".join("<li>%s %s</li>" % (self.text(p["text"]), self.anchors(p.get("anchors"))) for p in ev["points"])
            notes = "".join(self.judgment(u) for u in ev.get("evidenceNotes", []))
            body.append('<div class="card"%s><h3>%s %s</h3>%s<ul>%s</ul>%s</div>' % (
                ' data-s="%s"' % _esc(ev["status"]) if ev.get("status") else "", _esc(ev["title"]),
                self.tag(ev.get("status")), '<p class="anchor">%s</p>' % self.text(ev["notes"]) if ev.get("notes") else "",
                pts, '<h4>%s</h4><ul class="judgments">%s</ul>' % (_esc(L["evidenceNotes"]), notes) if notes else ""))
        if d.get("openQuestions"):
            body.append('<div class="callout"><strong>%s</strong><ul>%s</ul></div>' % (
                _esc(L["gaps"]), "".join("<li>%s</li>" % self.text(q) for q in d["openQuestions"])))
        o.append(self.section("fact", L["factSub"], "".join(body)))

        if d.get("decisions"):
            rows = [[_esc(x.get("id") or "D%d" % (i + 1)), self.text(x["decision"]), _esc(x.get("decidedBy")),
                     _esc(x.get("owner")), _esc(x.get("due")), self.tag(x["status"]),
                     self.text(x.get("followUp")), self.anchors(x.get("anchors"))] for i, x in enumerate(d["decisions"])]
            o.append(self.section("decisions", L["decisionsSub"], self.table(
                ["#", L["decision"], L["decidedBy"], L["owner"], L["due"], L["status"], L["followUp"], L["anchor"]],
                rows, [x["status"] for x in d["decisions"]])))
        if d.get("minutesCheck"):
            rows = [[self.text(r["written"]), self.text(r["spoken"]) + " " + self.anchors(r.get("anchors")),
                     '<span class="tag %s">%s</span>%s' % (VERDICT_CLASS[r["verdict"]],
                                                          _esc(L["verdicts"][r["verdict"]]),
                                                          '<div class="note">%s</div>' % self.text(r["note"])
                                                          if r.get("note") else "")] for r in d["minutesCheck"]]
            o.append(self.section("minutes", L["minutesSub"], self.table([L["written"], L["spoken"], L["verdict"]], rows)))
        if d.get("claimLedger"):
            rows = [[self.text(c["claim"]), _esc(c.get("claimant")), self.text(c.get("support")),
                     self.text(c.get("counter")), self.tag(c["status"]) + " " + self.strength(c.get("strength")),
                     self.anchors(c.get("anchors"))] for c in d["claimLedger"]]
            o.append(self.section("claims", L["claimsSub"], self.table(
                [L["claim"], L["claimant"], L["support"], L["counter"], L["status"], L["anchor"]], rows,
                [c["status"] for c in d["claimLedger"]])))

        if d.get("projectThread") or d.get("threadNotes"):
            items = "".join(
                '<div class="tl-item"%s><div class="tl-title">%s %s</div><div class="tl-meta">%s%s</div><div>%s</div>%s</div>'
                % (' data-s="%s"' % _esc(t["status"]) if t.get("status") else "", _esc(t["title"]),
                   self.tag(t.get("status")), self.text(t.get("label")),
                   " · " + self.text(t["note"]) if t.get("note") else "", self.text(t["body"]),
                   self.anchors(t.get("anchors"))) for t in d.get("projectThread", []))
            notes = "".join(self.judgment(u) for u in d.get("threadNotes", []))
            o.append(self.section("thread", L["threadSub"], '<div class="timeline">%s</div>%s' % (
                items, '<h4>%s</h4><ul class="judgments">%s</ul>' % (_esc(L["riskNotes"]), notes) if notes else "")))
        if d.get("influenceChain"):
            nodes = []
            for c in d["influenceChain"]:
                nodes.append(
                    '<div class="node" data-s="%s"><div class="who">%s %s %s</div><div>%s</div>'
                    '<div class="anchor">%s%s</div>%s%s</div>' % (
                        _esc(c["status"]), _esc(c["actor"]), self.tag(c["status"]), self.strength(c.get("strength")),
                        self.text(c["move"]),
                        "%s%s%s \u00b7 " % (_esc(L["adoptedBy"]), L["colon"], _esc(c["adoptedBy"])) if c.get("adoptedBy") else "",
                        "\u2192 " + self.text(c.get("effect")) if c.get("effect") else "",
                        self.anchors(c.get("anchors")),
                        '<div class="note">%s%s%s</div>' % (_esc(L["risk"]), L["colon"], self.text(c["riskIfWrong"]))
                        if c.get("riskIfWrong") else ""))
            o.append(self.section("chain", L["chainSub"], '<div class="chain">%s</div>' % '<div class="arrow">\u2193</div>'.join(nodes)))
        if d.get("stakeholders"):
            rows = [["<strong>%s</strong>%s" % (_esc(s["party"]), '<br><span class="anchor">%s</span>' % _esc(s["role"])
                                                if s.get("role") else ""),
                     self.text(s["statedPosition"]), self.text(s["apparentMotive"]) or "\u2014",
                     self.tag(s["status"]) + " " + self.strength(s["strength"]),
                     self.anchors(s.get("anchors")) + (' <span class="note">%s</span>' % self.text(s["evidenceNote"])
                                                        if s.get("evidenceNote") else "")]
                    for s in d["stakeholders"]]
            o.append(self.section("motive", L["motiveSub"], self.table(
                [L["party"], L["says"], L["wants"], L["status"], L["anchor"]], rows,
                [s["status"] for s in d["stakeholders"]])))
        um = d.get("understandingMap")
        if um and (um.get("rows") or um.get("omittedReason")):
            body = ""
            if um.get("rows"):
                heads = [L["party"]] + [(lab if L is LABELS["zh"] else col) for _, col, lab in MAP_DIMENSIONS]
                rows = []
                for r in um["rows"]:
                    cells = ["<strong>%s</strong>%s %s" % (_esc(r["party"]), '<br><span class="anchor">%s</span>' %
                                                           _esc(r["role"]) if r.get("role") else "",
                                                           self.anchors(r.get("anchors")))]
                    for k, _, _ in MAP_DIMENSIONS:
                        lv = r[k]["level"]
                        cells.append('<span class="lv lv-%s">%s</span> %s' % (_esc(lv), _esc(L["levels"].get(lv, lv)),
                                                                             self.text(r[k].get("note"))))
                    rows.append(cells)
                body += '<div class="um">%s</div>' % self.table(heads, rows)
            if um.get("omittedReason"):
                body += '<div class="callout">%s%s</div>' % (_esc(L["omitted"]), self.text(um["omittedReason"]))
            if um.get("readout"):
                body += '<div class="callout"><ul>%s</ul></div>' % "".join("<li>%s</li>" % self.text(x) for x in um["readout"])
            o.append(self.section("map", L["mapSub"], body))

        a = d.get("audit")
        if a:
            body = []
            if a.get("userNarrative"):
                body.append('<div class="callout"><strong>%s%s</strong>%s</div>' % (
                    _esc(L["narrative"]), L["colon"], self.text(a["userNarrative"])))
            boxes = []
            for cls, key, lab in (("box-supported", "supportedJudgments", "supported"),
                                  ("box-weak", "weakJudgments", "weak"),
                                  ("box-assume", "explicitAssumptions", "assumptions")):
                if a.get(key):
                    boxes.append('<div class="audit-box %s"><h4>%s</h4><ul class="judgments">%s</ul></div>' % (
                        cls, _esc(L[lab]), "".join(self.judgment(u) for u in a[key])))
            if a.get("validationTargets"):
                boxes.append('<div class="audit-box box-validate"><h4>%s</h4><ul>%s</ul></div>' % (
                    _esc(L["validate"]), "".join("<li>%s</li>" % self.text(x) for x in a["validationTargets"])))
            if boxes:
                body.append('<div class="audit-grid">%s</div>' % "".join(boxes))
            if a.get("estimateRisks"):
                body.append('<div class="card"><h3>%s</h3><ul>%s</ul></div>' % (
                    _esc(L["estimates"]), "".join("<li>%s</li>" % self.text(x) for x in a["estimateRisks"])))
            for s in a.get("suspiciousActions", []):
                body.append(
                    '<div class="card suspicious" data-s="%s"><h3>%s %s</h3>%s<div class="three">'
                    '<div><h4>%s</h4><p>%s</p></div><div><h4>%s</h4><p>%s</p></div><div><h4>%s</h4><p>%s</p></div>'
                    '</div></div>' % (_esc(s["status"]), _esc(L["suspicious"]), self.tag(s["status"]),
                                      "<p>%s %s</p>" % (self.text(s["action"]), self.anchors(s.get("anchors"))),
                                      _esc(L["infoChange"]), self.text(s["informationChange"]), _esc(L["pressure"]),
                                      self.text(s["pressureOrMisjudgment"]), _esc(L["misdirection"]),
                                      self.text(s["strategicMisdirection"])))
            if a.get("consensusCheck"):
                body.append('<div class="callout warn"><strong>%s</strong><ul>%s</ul></div>' % (
                    _esc(L["consensus"]), "".join("<li>%s</li>" % self.text(x) for x in a["consensusCheck"])))
            if body:
                o.append(self.section("audit", L["auditSub"], "".join(body)))

        ac = d.get("actions", {})
        lanes = []
        for cls, key in (("act-now", "doNow"), ("act-later", "doLater"), ("act-validate", "validateBeforeCommit")):
            items = ac.get(key) or []
            if not items:
                continue
            lis = []
            for x in items:
                meta = "".join('<span class="owner">%s %s</span>' % (_esc(L[f]), _esc(x[f])) for f in ("owner", "due")
                               if x.get(f))
                lis.append('<li%s>%s %s %s %s</li>' % (' data-s="%s"' % _esc(x["status"]) if x.get("status") else "",
                                                       self.text(x["text"]), self.tag(x.get("status")), meta,
                                                       self.anchors(x.get("anchors"))))
            lanes.append('<div class="act-box %s"><h4>%s</h4><ul>%s</ul></div>' % (cls, _esc(L[key]), "".join(lis)))
        body = '<div class="act-grid">%s</div>' % "".join(lanes)
        if ac.get("oneLinePositioning"):
            body += '<div class="callout"><strong>%s%s</strong>%s</div>' % (
                _esc(L["positioning"]), L["colon"], self.text(ac["oneLinePositioning"]))
        o.append(self.section("actions", L["actionsSub"], body))
        if d.get("methodNotes"):
            o.append(self.section("method", "", "<ul>%s</ul>" % "".join("<li>%s</li>" % self.text(x)
                                                                      for x in d["methodNotes"])))
        if d.get("references"):
            o.append(self.section("references", "", self.table(
                [L["label"], L["path"], L["reason"]],
                [[_esc(r["label"]), "<code>%s</code>" % _esc(r.get("path")) if r.get("path") else "", _esc(r["reason"])]
                 for r in d["references"]])))
        if self.idx and self.audience != "external":
            blocks = []
            for s in d.get("sources", []):
                index = self.idx.get(s["id"])
                if not index:
                    continue
                turns = "".join('<p id="%s"><b>%s %s</b> %s</p>' % (self.turn_id(s["id"], t), _esc(t["ts"] or ""),
                                                                   _esc(t["speaker"]), _esc(t["text"]))
                                for t in index.turns)
                if not turns:
                    turns = "<pre>%s</pre>" % _esc(index.raw)
                blocks.append('<h3 id="src-%s">%s %s</h3><div class="tx">%s</div>' % (
                    _esc(s["id"]), _esc(s["id"]), _esc(s["label"]), turns))
            if blocks:
                o.append('<section class="section" id="appendix"><h2>%s</h2><details class="tx-wrap"><summary>%s'
                         '</summary>%s</details></section>' % (_esc(L["appendix"]), _esc(L["expand"]), "".join(blocks)))
        legend = " ".join(self.tag(s) for s in STATUS_CLASS)
        o.append('<footer class="footer"><p><strong>%s</strong> %s</p><p>%s</p><p class="anchor">biz-retro-analyzer %s'
                 ' \u00b7 schema %s%s \u00b7 audience: %s</p></footer>' % (
                     _esc(L["legend"]), legend, _esc(L["footer"]), VERSION, _esc(d.get("schemaVersion")),
                     " \u00b7 " + _esc(m["generatedBy"]) if m.get("generatedBy") else "", _esc(self.audience)))
        payload = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
        o.append('<script type="application/json" id="report-data">%s</script><script>%s</script>' % (payload, HTML_JS))
        o.append("</main></body></html>")
        return "\n".join(o) + "\n"


def render_html(data, indexes=None, audience=None, css=None):
    audience = audience or data.get("meta", {}).get("audience") or "internal"
    shown, removed = redact(data, audience)
    css = css if css is not None else CSS_PATH.read_text(encoding="utf-8")
    lang = data.get("meta", {}).get("language") or ("zh-CN" if has_cjk(data["meta"].get("reportTitle", "")) else "en")
    return HtmlRenderer(shown, indexes or {}, lang, removed, audience).render(css)


def _parse_source_overrides(args):
    overrides = {}
    for item in getattr(args, "source", None) or []:
        if "=" not in item:
            raise SystemExit("error: --source expects ID=PATH, got %r" % item)
        sid, path = item.split("=", 1)
        overrides[sid.strip()] = Path(path.strip())
    return overrides


def cmd_render(args):
    """把报告 JSON 渲染成 HTML（单文件、内联 CSS）或 Markdown。"""
    data, upgraded = load_report(args.input)
    overrides = _parse_source_overrides(args)
    if args.transcript:
        sid = default_source_id(data)
        overrides.setdefault(sid, Path(args.transcript))
    mode, checks = lint_report(data, None, Path(args.input).resolve().parent, overrides, upgraded)
    schema = next(c for c in checks if c["id"] == "schema")
    if schema["status"] == "FAIL":
        for _, path, msg in schema["items"][:15]:
            print("schema: %s %s" % (path, msg), file=sys.stderr)
        print("error: report does not match the schema; fix it or run validate for details", file=sys.stderr)
        return 1
    failed = [c for c in checks if c["status"] == "FAIL"]
    if args.format == "md":
        audience = args.audience or data.get("meta", {}).get("audience") or "internal"
        out = render_markdown(redact(data, audience)[0])
    else:
        indexes, _ = load_source_indexes(data, Path(args.input).resolve().parent, overrides)
        out = render_html(data, indexes, args.audience)
    _write_output(out, args.output)
    if failed:
        print("warning: %d protocol check(s) fail: %s (run validate for details)" % (
            len(failed), ", ".join(c["id"] for c in failed)), file=sys.stderr)
    if args.output:
        print("Rendered %s -> %s" % (args.format, args.output), file=sys.stderr)
    return 0


def scaffold_json(mode):
    j = {"claim": FILL, "status": FILL, "strength": FILL, "basis": FILL,
         "anchors": [{"source": "S1", "speaker": FILL, "ts": "00:00", "quote": FILL}], "toValidate": FILL}
    data = {
        "schemaVersion": SCHEMA_VERSION,
        "meta": {"reportTitle": FILL, "reportDate": FILL, "outputMode": mode, "projectStage": FILL, "lead": FILL,
                 "language": "zh-CN", "audience": "internal", "interactionContext": FILL, "analysisWindow": FILL},
        "sources": [{"id": "S1", "label": FILL, "layer": "source", "type": "transcript", "path": FILL,
                     "speakerAttribution": "reliable"}],
        "summary": [{"label": FILL, "headline": FILL, "body": FILL, "status": FILL}],
        "evidenceLayer": [{"title": FILL, "source": "S1", "status": "Confirmed",
                           "points": [{"text": FILL, "anchors": [{"speaker": FILL, "ts": "00:00"}]}],
                           "evidenceNotes": [dict(j)]}],
        "openQuestions": [FILL],
        "decisions": [{"decision": FILL, "decidedBy": FILL, "owner": FILL, "due": FILL, "status": FILL,
                       "anchors": [{"speaker": FILL, "ts": "00:00"}]}],
        "actions": {"doNow": [{"text": FILL, "owner": FILL, "anchors": [{"speaker": FILL, "ts": "00:00"}]}],
                    "doLater": [{"text": FILL}], "validateBeforeCommit": [{"text": FILL}]},
    }
    if mode in ("B", "C"):
        data["projectThread"] = [{"label": FILL, "title": FILL, "body": FILL}]
        data["threadNotes"] = [dict(j)]
        data["influenceChain"] = [{"actor": FILL, "move": FILL, "adoptedBy": FILL, "effect": FILL, "status": FILL,
                                   "anchors": [{"speaker": FILL, "ts": "00:00"}]}]
        data["stakeholders"] = [{"party": FILL, "statedPosition": FILL, "apparentMotive": FILL, "status": FILL,
                                 "strength": FILL, "anchors": [{"speaker": FILL, "ts": "00:00", "quote": FILL}]}]
        data["understandingMap"] = {"rows": [dict([("party", FILL)] + [(k, {"level": FILL, "note": FILL})
                                                                       for k, _, _ in MAP_DIMENSIONS])],
                                    "readout": [FILL]}
        data["audit"] = {"userNarrative": FILL, "supportedJudgments": [dict(j)], "weakJudgments": [dict(j)],
                         "validationTargets": [FILL]}
    if mode == "C":
        data["audit"]["suspiciousActions"] = [{"action": FILL, "informationChange": FILL,
                                               "pressureOrMisjudgment": FILL, "strategicMisdirection": FILL,
                                               "status": FILL}]
        data["audit"]["consensusCheck"] = [FILL]
        data["claimLedger"] = [{"claim": FILL, "claimant": FILL, "support": FILL, "counter": FILL, "status": FILL}]
        data["minutesCheck"] = [{"written": FILL, "spoken": FILL, "verdict": FILL}]
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


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
    p.add_argument("--mode", type=str.upper, choices=["A", "B", "C"], default="B")
    p.add_argument("--format", choices=["md", "json"], default="md")
    p.add_argument("-o", "--output")

    p = sub.add_parser("validate", help="Lint an analysis and resolve its anchors against the transcript")
    p.add_argument("input")
    p.add_argument("-t", "--transcript", action="append",
                   help="source transcript to resolve timestamps, speakers and quotes against (repeatable)")
    p.add_argument("--mode", type=str.upper, choices=["A", "B", "C"], help="override the inferred output mode")
    p.add_argument("--json", action="store_true", help="machine-readable result")
    p.add_argument("-s", "--source", action="append", metavar="ID=PATH",
                   help="JSON input: transcript for a source id, overriding sources[].path (repeatable)")
    p.add_argument("-v", "--verbose", action="store_true", help="show every finding and check details")

    p = sub.add_parser("render", help="Render report JSON (schema v2) to single-file HTML or Markdown")
    p.add_argument("input")
    p.add_argument("--format", choices=["html", "md"], default="html")
    p.add_argument("-o", "--output")
    p.add_argument("--audience", choices=["internal", "leadership", "external"],
                   help="redact for the audience (default: meta.audience or internal)")
    p.add_argument("-t", "--transcript", help="transcript for the first source-layer source")
    p.add_argument("-s", "--source", action="append", metavar="ID=PATH", help="transcript for a source id")
    return parser


def main(argv=None):
    _setup_console()
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {"preprocess": cmd_preprocess, "scaffold": cmd_scaffold, "validate": cmd_validate,
                "render": cmd_render}
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
