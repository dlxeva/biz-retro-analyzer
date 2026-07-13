#!/usr/bin/env python3
"""biz-retro-analyzer CLI: transcript preprocessing, output scaffolding, protocol validation."""

import argparse, re, sys
from pathlib import Path

VERSION = "1.0.0"

VALID_STATUS = {"Confirmed", "Inferred", "Assumption", "Needs validation"}
VALID_STRENGTH = {"High", "Medium", "Low"}

# 高风险声明关键词——validate 检查这些词附近是否有 Source anchor
HIGH_RISK_KEYWORDS = [
    "motive", "intent", "budget", "pricing", "leverage", "political",
    "controls the", "bad faith", "hidden agenda",
    "动机", "真实意图", "预算", "定价", "控制", "恶意",
]

# 噪声关键词——preprocess 用这些词标记非业务行
NOISE_PATTERNS = re.compile(
    r"(外卖|快递|吃饭|孩子|ipad|iPad|空调|天气|周末|放假|"
    r"抽烟|阳台|喝茶|去哪|怎么来|开车|地铁|"
    r"hello|Hello|喂|诶|哈哈|呵呵|嘿嘿)", re.IGNORECASE
)

# 发言人检测正则——匹配行首的说话人标注
SPEAKER_PATTERN = re.compile(
    r"^\s*(?:\[SPEAKER:\s*[^\]]+\]\s*)?"  # 跳过已标记行
    r"([A-D](?:\s|$)|说话人\s*[1-9]|[一二三四五六](?:\s|：|:)|"
    r"[\u4e00-\u9fff]{1,4}\s*(?:[:：]\s*|\d{1,2}[:：]\d{2}))"
)

def cmd_preprocess(args):
    """预处理：逐行扫描，标注发言人，标记噪声行。"""
    text = Path(args.input).read_text(encoding="utf-8")
    lines = text.strip().split("\n")
    output = []
    stats = {"total": 0, "speakers": set(), "noise": 0}

    for line in lines:
        stripped = line.strip()
        if not stripped:
            output.append(""); continue
        stats["total"] += 1
        m = SPEAKER_PATTERN.match(stripped)
        if m:
            stats["speakers"].add(m.group(1).strip())
            output.append(f"[SPEAKER: {m.group(1).strip()}] {stripped}")
        elif NOISE_PATTERNS.search(stripped):
            stats["noise"] += 1
            output.append(f"[NOISE?] {stripped}")
        else:
            output.append(stripped)

    spk_count = len(stats["speakers"])
    print("=" * 60)
    print("  biz-retro-analyzer · transcript preprocessing")
    print("=" * 60)
    print(f"  Content lines : {stats['total']}")
    print(f"  Speakers      : {spk_count} ({', '.join(sorted(stats['speakers']))})")
    print(f"  Noise lines   : {stats['noise']}")
    if spk_count == 0:
        print("  ⚠ No speaker labels → speaker-unknown mode")
    if stats["noise"] > 5:
        print(f"  ⚠ {stats['noise']} noise lines → isolate before analysis")
    print("=" * 60)
    print()
    result = "\n".join(output)
    if args.output:
        Path(args.output).write_text(result + "\n", encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(result)

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

def cmd_validate(args):
    """验证分析输出是否符合协议规则。"""
    text = Path(args.input).read_text(encoding="utf-8")
    checks = []

    # Check 1: 证据标注存在
    has_tags = bool(re.search(r"`Status`\s*:", text, re.I))
    checks.append(("Evidence tags present", has_tags))

    # Check 2: 高风险声明有锚点
    # 逻辑：搜索 HIGH_RISK_KEYWORDS，检查附近 200 字符内是否有 anchor
    anchor_failures = []
    for kw in HIGH_RISK_KEYWORDS:
        for m in re.finditer(re.escape(kw), text, re.I):
            window = text[max(0, m.start()-200):m.end()+200]
            if not re.search(r"anchor|来源|锚点", window, re.I):
                anchor_failures.append(m.group())
    checks.append(("High-risk claims have anchors", len(anchor_failures) == 0))

    # Check 3: 事实层存在
    checks.append(("Fact layer present",
        bool(re.search(r"Fact Record|事实记录|What is confirmed", text, re.I))))

    # Check 4: 理解地图存在（Mode B/C 必填）
    has_map = bool(re.search(r"Understanding Map|理解地图", text, re.I))
    checks.append(("Understanding map present", has_map))

    # Check 5: 没有未验证的动机判断被标为 Confirmed
    # 逻辑：搜索同时包含 Confirmed 和 motive/intent 的行
    bad_confirmed = re.findall(r"(?i)Confirmed.*(?:motive|intent|动机|意图)", text)
    checks.append(("No Confirmed motive claims", len(bad_confirmed) == 0))

    # Check 6: 动作项有证据基础
    action_lines = re.findall(r"(?i)(?:Do now|立即)[^\n]*", text)
    has_action_ev = any(re.search(r"evidence|证据", a, re.I) for a in action_lines) if action_lines else False
    checks.append(("Actions have evidence", has_action_ev or not action_lines))

    # 报告输出
    print("=" * 60)
    print("  biz-retro-analyzer · protocol validation")
    print("=" * 60)
    for name, passed in checks:
        print(f"  {'✓' if passed else '✗'} {'PASS' if passed else 'FAIL'}  {name}")
    errors = [n for n, p in checks if not p]
    passed_count = sum(1 for _, p in checks if p)
    print(f"\n  Result: {passed_count}/{len(checks)} passed")
    if errors:
        print(f"  Status: FAIL"); sys.exit(1)
    else:
        print(f"  Status: PASS")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(
        prog="retro_tool.py",
        description="biz-retro-analyzer CLI")
    parser.add_argument("--version", action="version", version=f"biz-retro-analyzer {VERSION}")
    sub = parser.add_subparsers(dest="command")

    p1 = sub.add_parser("preprocess", help="Detect speakers, flag noise in transcript")
    p1.add_argument("input"); p1.add_argument("-o", "--output")

    p2 = sub.add_parser("scaffold", help="Generate output template")
    p2.add_argument("--mode", choices=["A","B","C"], default="B")
    p2.add_argument("-o", "--output")

    p3 = sub.add_parser("validate", help="Check analysis against protocol")
    p3.add_argument("input"); p3.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
    if args.command == "preprocess": cmd_preprocess(args)
    elif args.command == "scaffold": cmd_scaffold(args)
    elif args.command == "validate": cmd_validate(args)
    else: parser.print_help(); sys.exit(1)

if __name__ == "__main__":
    main()
