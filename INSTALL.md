# Install

`biz-retro-analyzer` is an Agent Skill: a folder with `SKILL.md` at the root. Copy that folder into the place your agent already looks for skills. The analysis protocol is the documents; the CLI is optional.

Python 3.8 or newer, no pip packages. `python3 scripts/retro_tool.py --help` from the skill folder is the smoke test.

## Claude Code

Project skill (this repo as the project):

```text
.claude/skills/biz-retro-analyzer/SKILL.md
```

User skill:

```text
~/.claude/skills/biz-retro-analyzer/SKILL.md
```

Keep `references/`, `assets/`, `scripts/`, and `examples/` next to `SKILL.md`. Then ask Claude to use the skill, or mention `biz-retro-analyzer` in the prompt.

## Cursor

Same layout, under the project or the user skills directory:

```text
.cursor/skills/biz-retro-analyzer/SKILL.md
```

or, depending on the Cursor build, the Agent Skills folder shown in Settings. Point the agent at `SKILL.md`. CLI commands in the skill are relative to that file.

## Codex / OpenAI Agents

`agents/openai.yaml` is the short description and default prompt for that channel. Zip or clone the whole skill folder so `SKILL.md` stays at the root of what you upload. Do not upload `evaluations/` or `tests/runs/` if you want a smaller package; they are not needed at runtime.

## Zip / web download

1. Download the repository zip from GitHub.
2. Unzip. The skill root is the folder that contains `SKILL.md`.
3. Copy that folder into your agent's skills directory (see above).
4. If you only want the protocol, you can drop `evaluations/` and `tests/`. Keep `references/`, `assets/`, and `scripts/`.

## Windows

- If `python3` is missing, use `py -3 scripts\retro_tool.py --help`.
- Transcripts should be UTF-8. PowerShell: `Get-Content -Encoding utf8`. If a file is GBK, the CLI still reads it.
- Run commands from the skill folder so relative paths in `SKILL.md` resolve.

## After install

```bash
python3 scripts/retro_tool.py preprocess examples/quickstart-transcript.txt
python3 scripts/retro_tool.py validate examples/quickstart-output.md -t examples/quickstart-transcript.txt
python3 scripts/retro_tool.py render examples/quickstart.report.json -o /tmp/quickstart.html
```

`validate` is a lint: form plus whether anchors exist in the transcript. It does not grade the judgments.
