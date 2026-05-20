# Input Modes

Use this file to decide how deep the analysis can safely go.

## Mode 1: Source Evidence Only

Use when the user provides only raw materials such as:

- transcripts
- notes
- field observations
- video analysis text

### Safe outputs

- structured fact records
- source-by-source summaries
- factual open questions
- light project thread inference

### Avoid

- strong motive attribution without enough support
- heavy reverse-audit conclusions

### Special case: Speaker-Unknown Mode

If the source material does not reliably label who said what:

- do not force person-level motive attribution
- downgrade to anonymous position analysis
- use labels such as:
  - `one participant`
  - `another speaker`
  - `a pushing view`
  - `a cautious view`
- preserve uncertainty instead of assigning identity

---

## Mode 2: Source Evidence + Project Context

Use when raw materials are accompanied by:

- project background
- current collaboration setup
- user concerns
- product or solution sketches

### Safe outputs

- structured fact records
- cross-material project progression
- stronger stakeholder motive analysis
- current-stage boundary recommendations

### Watch for

- user framing may already bias the reading

---

## Mode 3: Source Evidence + Context + Follow-up Reasoning

Use when the user also provides:

- prior AI analysis
- their own retrospective reasoning
- intermediate conclusions
- back-and-forth debate or correction

### Safe outputs

- full retro pack
- explicit fact/judgment split
- reverse audit
- method notes

### Hard rule

Treat later reasoning as judgment-layer material.  
Do not upgrade it into source evidence.

---

## Decision Rule

When inputs are mixed:

1. tag raw evidence first
2. tag user context second
3. tag follow-up reasoning third

If unsure, preserve uncertainty instead of collapsing layers.

When speaker labels are missing:

1. mark `speaker-unknown mode`
2. keep structure and issue extraction
3. weaken stakeholder-specific outputs
4. recommend speaker relabeling if later precision matters
