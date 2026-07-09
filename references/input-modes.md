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
- light participant-understanding inference only when evidence is explicit

### Avoid

- strong motive attribution without enough support
- strong competence or literacy claims without enough support
- heavy reverse-audit conclusions

### Special case: Transcription Noise Handling

Real-world transcripts (especially speech-to-text) often contain segments that are **not business-relevant** but will pollute the analysis if left mixed in.

Typical noise types:

- side conversations, visitors entering, family interruptions
- ordering food, smoking breaks, logistics chatter
- greetings, small talk, jokes unrelated to the topic
- ASR misrecognitions, duplicated fragments, filler storms

Hard rule: do not let noise segments contribute to fact layer, motive reading, or understanding assessment.

Handling protocol:

1. **Identify** — flag noise segments by approximate location or time range.
2. **Isolate** — set them aside from the core business analysis.
3. **Annotate** — note briefly what was excluded and why (so the reader knows nothing was hidden).
4. **Do not delete** — some noise carries weak relationship or context signals (who knows whom, informal dynamics), but treat those only as `Low` strength context, never as confirmed evidence.
5. **State the effective analysis window** — e.g. "analysis covers 00:00–57:00; 58:00 onward excluded as non-business noise."

Default: when noise exceeds ~5% of a transcript, always state the analysis window explicitly.

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
- participant understanding map
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
- participant understanding map with strategy implications
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

When participant understanding is thin or ambiguous:

1. keep the map partial rather than forcing a full rating
2. distinguish observed understanding from assumed competence
3. prefer phrases like:
   - `shows strong workflow understanding`
   - `appears politically fluent but delivery depth is unclear`
   - `evidence of domain understanding is thin`

When the transcript contains non-business noise:

1. identify and isolate the noise segments first
2. state the effective analysis window
3. exclude noise from all structured layers (fact, motive, understanding)
4. only mine weak relationship signals from noise if context-relevant, tagged `Low`
