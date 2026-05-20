# Open-Source Sanitization

Use this file when preparing public-facing examples, documentation, or sample outputs for this skill.

## Goal

Keep the repository:

- reusable
- non-sensitive
- non-identifying
- not dependent on one real client, project, or organization

## What to Remove or Generalize

### Names

- real customer names
- real partner names
- specific team members
- internal code names

Replace them with:

- `Client A`
- `Partner B`
- `Team Lead`
- `Project X`

### Identifiers

- phone numbers
- email addresses
- meeting links
- internal ticket ids
- contract ids
- financial figures tied to a real company

Either delete them or replace them with obviously fake placeholders.

### Domain Lock-In

Do not let one project's industry dominate the reusable skill text.

Examples:

- avoid writing core rules as if they only apply to government projects
- avoid naming one sector in the skill description unless the skill is intentionally vertical
- move industry-specific logic into optional examples or future extension files

### Private Reasoning Traces

Do not include:

- internal frustrations tied to real people
- trust judgments about named parties
- deal-stage assumptions that reveal private negotiation posture

Keep reusable patterns, not private politics.

## What to Keep

It is fine to keep:

- analysis structure
- generic examples
- method steps
- reusable prompts
- quality checks
- reverse-audit rules

## Repository Review Checklist

Before publishing, check:

- Does README mention a real customer or project?
- Does SKILL.md expose one internal workflow as universal truth?
- Do examples contain traceable names or details?
- Do references contain private shorthand only your team understands?
- Would an outside user understand this repo without knowing your original project?

If any answer is "yes", sanitize before release.
