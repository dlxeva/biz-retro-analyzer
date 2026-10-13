# Fictional product review (Mode C)

**Everything here is invented.** The company, people, customers, and numbers do not exist. The material shows a Mode C audit of a meeting where a confident speaker makes claims the room never checks.

| File | What it is |
|---|---|
| `transcript.txt` | Q3 product review meeting, about 15 minutes, speakers A-E. It has noise segments (a room-booking interruption and small talk at the end) and a CEO who joins late. |
| `group-message.txt` | The organizer's post-meeting summary in the project group chat. |
| `context.txt` | Background from the person asking for the analysis. This is context, not independent evidence. |
| `report.json` | The analysis as report JSON (schema `references/output-schema.json`, v2). This file is the single source of truth. |
| `report.html` | Rendered from `report.json`. |
| `report.md` | Rendered from `report.json`. |

Live demo (GitHub Pages): https://dlxeva.github.io/biz-retro-analyzer/demo/

Commands, run from the repository root:

```bash
python3 scripts/retro_tool.py preprocess examples/product-review-fictional/transcript.txt
python3 scripts/retro_tool.py validate examples/product-review-fictional/report.json
python3 scripts/retro_tool.py render examples/product-review-fictional/report.json -o examples/product-review-fictional/report.html
python3 scripts/retro_tool.py render examples/product-review-fictional/report.json --format md -o examples/product-review-fictional/report.md
python3 scripts/retro_tool.py render examples/product-review-fictional/report.json --audience leadership -o /tmp/leadership.html
```

`validate` resolves every anchor in `report.json` against `transcript.txt` and `group-message.txt`. Source paths are resolved relative to the JSON file. A PASS means the report has the protocol's form and its timestamps and quotes exist in the sources. It does not mean the judgments are right.

The analysis was written by hand following SKILL.md. It is a demonstration, not an evaluation result.
