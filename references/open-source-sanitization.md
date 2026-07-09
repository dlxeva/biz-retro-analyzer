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

### Composite Fingerprints (the most common leakage)

Changing names and numbers is shallow sanitization. The real risk is **composite fingerprints**: a combination of individually-common details that, taken together, identify the source uniquely. Any insider or industry peer reads them and recognizes the case within seconds.

Test every example for composite fingerprints before publishing.

#### Red-flag detail types

- **Rare or unique events**: "the demo used a chat feature pulled from a game" — this is nearly one-of-a-kind and recognizable instantly.
- **Specific tool + action pairs**: "suggested sending a prompt to [specific consumer AI product]" — the named tool plus the exact action narrows fast.
- **Paired numbers**: "revenue 40M, accuracy 60%→90%" — one number might be common, two together are a fingerprint.
- **Unusual industry x scenario combos**: "adult-education collapse x customer service" — niche intersections are traceable.
- **Team-structure numbers**: "three people, one deep client" — in a small niche this identifies the team.

#### The composite fingerprint test

Ask, for each example:

1. If I showed this to someone in the same industry, could they name the company or team within 30 seconds?
2. Are there three or more specific details (event, tool, figure, niche combo) that appear together?
3. Is any single detail rare enough to be one-of-a-kind?

If the answer to any is yes, shallow sanitization (rename + renumber) is not enough.

#### Sanitization strategies, ranked by safety

1. **Scene substitution (safest for public release)** — keep the conflict structure, noise pattern, or consensus shape that makes the example useful, but move it to a completely different industry and product context. The traceable link is severed entirely. Use this when the example's value is structural, not domain-specific.

2. **Detail dilution** — keep the industry but replace each fingerprint detail with a common alternative from the same domain. Weaker than scene substitution: team-structure numbers and niche combos may still be recognizable to close peers.

3. **Renaming only (weakest, often insufficient for real cases)** — change names and figures but keep the scenario. Only safe for fully generic situations; risky for anything drawn from real work.

Hard rule: for examples derived from real recordings or real projects, prefer scene substitution. Renaming alone almost always leaks to insiders.

### Domain Lock-In

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
- Do any examples contain composite fingerprints (rare events, tool+action pairs, paired numbers, niche combos, team-structure numbers) that survive renaming? If yes, apply scene substitution, not just renaming.
- For examples derived from real recordings: would an industry peer recognize the source within 30 seconds?

If any answer is "yes", sanitize before release.
