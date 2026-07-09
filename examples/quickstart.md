# Quickstart: From a raw transcript to a full retro

This is a complete end-to-end walkthrough. It shows what to upload, how to trigger the skill, what the skill does with your material, and what a finished output looks like.

If you only read one file in this repository, read this one.

---

## Start here: what to upload

The best input for this skill is a **raw speech-to-text transcript** — the verbatim output from a recording, not a cleaned-up summary.

Why raw transcripts work better than summaries:

- they preserve **tone, hesitation, and interruptions** — these are evidence
- they keep **speaker-by-speaker attribution**, which the skill needs for motive and understanding analysis
- they let the skill anchor every claim back to a specific moment (`Source anchor: Dr. Li, on night-shift latency`)
- summaries quietly flatten away exactly the conflicts and gaps this skill is built to surface

**Ideal input shape:**

- speaker labels present (A / B / C / D, or names, or roles)
- timestamps or at least turn order preserved
- ASR errors left in — the skill does not need perfect text, it needs faithful text
- if you have additional context (project background, your own hypotheses) or follow-up reasoning (prior analysis, debates), provide them **separately**, not mixed into the transcript

If speaker labels are missing, the skill will enter `speaker-unknown mode` and weaken its person-level claims — still useful, but less precise.

---

## The example input

This example uses a fictional scenario. All names, organizations, and details are invented. The transcript is written in a realistic speech-to-text style: oral phrasing, interruptions, repetitions, and a few ASR-style errors.

### Scenario

A clinical decision support system (CDSS) vendor is running a pilot of an AI-assisted electronic medical record (EMR) entry tool at a hospital. This is the second multi-party review meeting.

### Speakers

- **A — Lin Wei** (林伟): vendor project manager
- **B — Chen Hao** (陈昊): vendor technical lead
- **C — Director Zhou** (周主任): hospital IT department director
- **D — Dr. Li** (李医生): physician representative, respiratory department

### Layer 1: Source evidence (the transcript)

> The transcript is in Chinese to stay realistic for this domain. The analysis output below is in English to match the skill's template conventions.

```text
A 林伟 00:00
那我们继续啊，上次会议聊的那个病历辅助录入，这次主要就是看看试点这边大家反馈怎么样。

C 周主任 00:12
我先说啊，信息科这边收到的反馈呢，主要两点。第一呢就是，医生那边反映录入速度反而比以前慢了。第二呢就是这个，你们这个结构化字段，跟我们现有的 HIS 系统对不上，这边导入导出有问题。

D 李医生 00:35
对，我我我补充一下，就是我们科里面用下来的感觉，就是，嗯，白天还行，白天那个，就是提示出来的时候还比较准，但是夜班的时候，夜班那个，经常是我在写病历写到一半，然后那个它才弹出来，那个延迟太厉害了。

A 林伟 01:02
李医生这个延迟的问题，我们我们之前确实，嗯，陈昊你那边查了吗。

B 陈昊 01:10
查了，这个其实是因为，夜班的时候你们那个 HIS 那边，做数据备份，所以那边接口会，会有一个窗口期是关掉的，我们这边的请求就其实是在排队，等他们那边放开。

C 周主任 01:28
等一下，那个备份窗口这个事情，我们信息科是有规定的，那个不能随便动，这个是，属于安全的，安全要求。

B 陈昊 01:38
我理解，我不是说让你们改，我是说这个，这个是一个技术上的一个客观情况，那我们这边能做的呢，就是要么我们做一个本地缓存，但是本地缓存的话，就需要你们那边开一个，开一个接口的权限。

C 周主任 01:55
开接口权限这个事情，得走流程，而且我我也说句实话，就是，开了之后万一出了问题，这个责任，这个到时候算谁的。

A 林伟 02:10
这个这个，周主任您放心，这个责任界定我们可以在合同里面，这一块我们之前也有处理经验。

D 李医生 02:22
那我我打断一下啊，我就是想知道，这个，这个延迟的问题，到底能不能解决，因为如果是夜班一直这样，那我底下医生他们，他们意见会很大，说实话。

A 林伟 02:40
能解决的，李医生，这个技术上是有方案的，就是刚才陈昊说的本地缓存。

C 周主任 02:50
我我插一句，其实我更关心的，不是这个延迟，我更关心的是，这个系统它到底有没有，有没有真正帮到医生。因为你们上次给的数据，说录入效率提升了百分之多少，但是我自己问了一圈，医生那边说感觉没那么明显。这个我觉得，这个才是核心问题。

A 林伟 03:15
这个，周主任，这个数据我们是，是按照操作次数来统计的，这个统计口径是之前咱们，咱们确认过的。

C 周主任 03:25
统计口径确认过，但是，但是医生的实际感受是另一回事。我我我我个人觉得，你们这个，是不是应该，再去就是，跟着医生实际上一两个班，看看真实的情况。

B 陈昊 03:45
这个可以，其实我们一直也想去现场看看，因为就是，很多问题在后台数据上其实看不出来，必须得去现场。

A 林伟 03:58
那这个就这么定，下周我们安排，安排陈昊去跟一两个夜班。然后那个接口权限的事，周主任您看这样行不行，我们，我们先把申请流程走起来，这个不影响，不影响这个现场跟进。

C 周主任 04:15
行，流程先走着，但是我丑话说前面啊，这个现场跟下来如果效果不好，那这个，这个试点的，后续怎么弄，咱们得重新谈。

A 林伟 04:30
理解理解。
```

### Layer 2: Project context (optional, provided by user)

```text
This is the second review of a 3-month pilot.
The vendor wants to convert the pilot into a full rollout contract.
The hospital IT department controls the technical approvals.
The clinical side was initially supportive but is losing patience with the night-shift issue.
```

### Trigger prompt (copy and adapt)

```md
Use biz-retro-analyzer / Mode B: Retro Pack.

Input stack:
- Source evidence: [the transcript above]
- Context: [the project context above]

Please produce:
1. Structured Fact Record
2. Project Thread
3. Stakeholder Motive Readout
4. Participant Understanding Map
5. Judgment and Reverse Audit
6. Current Actions

Rules:
- Separate facts, participant claims, and model inferences.
- Tag high-impact judgments with Status, Strength, Basis, and Source anchor.
- Do not let later reasoning or my context overwrite the source evidence.
```

---

## What the skill does with it

The skill runs a layered pipeline. Each layer is built before the next, so earlier material is never silently overwritten by later interpretation.

1. **Classify the input** — separates raw transcript from your context. Tags the interaction context (this is a `working_session`).
   See `references/input-modes.md`.

2. **Build the fact layer** — extracts what was actually said, tied to speakers and timestamps. Flags factual gaps.
   See `references/output-templates.md`.

3. **Build the structure layer** — merges across speakers into a project thread, identifies stakeholder motives and who understands what.
   See `references/analysis-checks.md`.

4. **Build the judgment layer** — runs reverse audit, tags high-risk claims, checks for false consensus.
   See `references/reverse-audit.md`.

---

## Full sample output

Below is what a complete Mode B output looks like for this input. Every claim is anchored back to the transcript.

### Structured Fact Record

- **Source set**: single meeting transcript, ~4.5 minutes of dense content
- **Source type**: speech-to-text transcript, reliable speaker labels, minor ASR artifacts
- **Interaction context**: `working_session` (multi-party project review)
- **What is confirmed**:
  - The pilot has two reported problems: slow entry speed and field-mismatch with the existing HIS system. `Source anchor: Director Zhou, 00:12`
  - Night-shift latency is a specific complaint from the clinical side. `Source anchor: Dr. Li, 00:35`
  - The latency cause is identified: HIS backup window closes the interface, requests queue. `Source anchor: Chen Hao, 01:10`
  - The backup window cannot be changed due to security policy. `Source anchor: Director Zhou, 01:28`
  - A technical fix exists (local cache) but requires an interface-permission approval. `Source anchor: Chen Hao, 01:38`
  - The vendor's efficiency metric is disputed: IT's informal polling of doctors does not match the vendor's numbers. `Source anchor: Director Zhou, 02:50`
- **Explicit follow-up actions**:
  - Chen Hao to shadow 1-2 night shifts next week. `Source anchor: Lin Wei, 03:58`
  - Interface-permission application to start in parallel. `Source anchor: Lin Wei, 04:15`
- **Open factual gaps**:
  - Whether the local-cache fix actually resolves night-shift latency under real load is untested.
  - The real magnitude of the efficiency gap between vendor metrics and doctor experience is unknown.
- **Evidence notes**:
  - `Claim`: the pilot's core value is now in question
  - `Status`: Inferred
  - `Strength`: Medium
  - `Basis`: Director Zhou's repeated reframing toward "is this actually helping doctors"

### Project Thread

- **Current stage**: mid-pilot, second review. Vendor wants conversion to full contract; hospital is signaling conditionality.
- **How the goal shifted**: the meeting opened on a technical problem (entry speed, field mismatch) but Director Zhou reframed it to a value question ("is this actually helping doctors"). The conversation's center of gravity moved from "fix the bug" to "prove the worth."
- **Trial scenario vs. product body**: this is still a pilot. Director Zhou's closing remark ("if the on-site result is bad, we need to renegotiate") makes clear the pilot does not guarantee rollout.
- **Current blocking issue**: night-shift latency has a proposed fix but the fix depends on an interface-permission approval that Director Zhou is cautious about.
- **Non-blocking but real gap**: the efficiency-metric dispute is not blocking any immediate action, but it is the larger strategic risk.
- **Evidence-risk notes**:
  - `Claim`: Director Zhou is the gatekeeper for rollout, not Dr. Li
  - `Status`: Inferred
  - `Strength`: Medium
  - `Basis`: Zhou controls the approval flow and introduced the renegotiation condition; Dr. Li's complaints were routed through technical fixes, not decision authority

### Stakeholder Motive Readout

| Party | What they say | What they appear to want | Confidence | Evidence basis |
| --- | --- | --- | --- | --- |
| **Lin Wei (A)** | Everything is solvable; let's move forward in parallel | Keep the pilot alive and moving toward contract conversion; avoid any single issue becoming a dealbreaker | Medium | Repeatedly deflects to "we can solve this," sequences actions to maintain momentum |
| **Chen Hao (B)** | Technical framing of every problem | Wants the technical path to be clean; genuinely interested in seeing real conditions | Medium | Consistently routes problems to causes and fixes; volunteered for on-site |
| **Director Zhou (C)** | Process, security, responsibility concerns | Wants proof of value before committing; is hedging against rollout risk; may be building an exit rationale | Low-Medium | Introduced renegotiation condition; reframed from bug to value; "丑话说前面" |
| **Dr. Li (D)** | Night-shift latency is unacceptable | Wants the night-shift pain resolved fast, or his colleagues will push back | Medium | Interrupted twice to refocus on the latency; explicit about colleague pressure |

### Participant Understanding Map

| Party | Domain understanding | Workflow understanding | Delivery understanding | Organizational understanding | Main evidence |
| --- | --- | --- | --- | --- | --- |
| **Lin Wei (A)** | Medium — knows the product pitch, less visible on clinical reality | Strong — drives sequencing, keeps actions moving | Medium — defers technical depth to Chen Hao | Strong — reads the room, manages Zhou and Li separately | Routes each complaint to an owner and an action |
| **Chen Hao (B)** | Medium-Strong — correctly diagnosed the HIS backup root cause | Strong — maps problems to causes and to concrete fixes | Strong — proposes local cache, identifies the permission dependency | Medium — understands the interface issue but under-weights the approval friction | 01:10, 01:38 |
| **Director Zhou (C)** | Strong on institutional reality — reframes to "is it actually helping" | Strong — knows the approval flow, security constraints, responsibility boundaries | Medium — defers technical assessment | Strong — controls the gate; introduces renegotiation leverage | 01:28, 02:50, 04:15 |
| **Dr. Li (D)** | Strong on the clinical pain point (night-shift latency) | Weak — does not engage with the HIS/permission chain at all | Weak — no engagement with delivery constraints | Weak — does not reference internal hospital politics | 00:35, 02:22 |

**Readout:**
- The two strongest understandings sit on opposite sides of the table: Zhou understands the organizational and institutional mechanics; Chen understands the delivery and technical mechanics.
- Dr. Li understands the clinical problem deeply but almost nothing about why it happens or how it gets fixed. This is normal for a clinical representative, but it means Dr. Li's urgency will keep surfacing unless the fix path is visible to him.
- The strategic risk: if Zhou and Chen cannot align (organizational gate vs. technical fix), the pilot stalls regardless of Dr. Li's satisfaction.

### Judgment and Reverse Audit

- **User's current narrative** (from context): vendor wants conversion; hospital IT controls approvals; clinical side is losing patience.
- **Judgments that look supported**:
  - The night-shift latency has a real technical cause and a plausible fix. `Confirmed` / `High` / `Source anchor: Chen Hao 01:10-01:38`
  - Director Zhou is signaling that the pilot is now conditional on proving value, not just fixing bugs. `Inferred` / `Medium` / `Source anchor: Zhou 02:50, 04:15`
- **Judgments that need stronger evidence**:
  - `Claim`: Director Zhou is building an exit rationale
  - `Status`: Assumption
  - `Strength`: Low
  - `Basis`: single meeting; Zhou's reframing could also be genuine quality concern, not exit preparation
  - `What would validate it`: does Zhou raise this framing in the next meeting too? Does he escalate to higher leadership?
- **Likely overestimates**:
  - The vendor (Lin Wei) may be overestimating how much the technical fixes will satisfy Zhou. Zhou's core concern shifted to value, not latency.
- **Suspicious action requiring lower-intent alternatives**:
  - `Action`: Director Zhou disputed the efficiency metric that was previously agreed (`统计口径是之前确认过的`).
  - `Information-change explanation`: Zhou may have heard new feedback from doctors between meetings.
  - `Pressure explanation`: Zhou may be under internal pressure to justify the pilot.
  - `Strategic-misdirection explanation`: Zhou may be manufacturing leverage for renegotiation.
  - `Current status`: `Needs validation` — all three are plausible from one meeting.
- **High-impact claims requiring validation**:
  - Whether the local-cache fix resolves latency under real night-shift load — must be confirmed during the on-site shadow.

### Current Actions

- **Do now**:
  - Chen Hao shadows 1-2 night shifts to observe real conditions and validate the latency fix. `Evidence: Lin Wei 03:58, Chen Hao 03:45`
  - Start the interface-permission application in parallel. `Evidence: Lin Wei 04:15`
- **Do later**:
  - After the on-site, reassess whether the efficiency-metric dispute needs a new measurement approach, not just new data.
- **Must validate before deeper commitment**:
  - Before any rollout conversation, confirm whether Director Zhou's reframing is a quality concern or an exit signal. The vendor's entire strategy assumes Zhou wants this to succeed.
  - `Action`: schedule a separate 1:1 with Zhou
  - `Triggered by`: Zhou's renegotiation framing at 04:15
  - `Evidence strength`: Medium

---

## How to verify it ran correctly

Check the output against these five points:

1. **Facts are anchored.** Important claims cite a speaker and a moment in the transcript. If a claim has no anchor and affects a decision, it should be tagged `Needs validation`.
2. **Speakers are not flattened.** Director Zhou and Dr. Li are not merged into one "hospital" voice. Their motives and understanding levels differ.
3. **No single spicy line became a stable conclusion.** Zhou's renegotiation remark did not become "Zhou wants to cancel the pilot" without a `Needs validation` flag.
4. **The context did not overwrite the transcript.** Your Layer 2 input ("vendor wants conversion") informed the thread but did not become a confirmed fact.
5. **The Participant Understanding Map distinguishes dimensions.** Zhou is not uniformly "high" — he is high on organizational, medium on delivery.

---

## Quick FAQ

**My transcript has no speaker labels. What happens?**

The skill enters `speaker-unknown mode`. It will still extract structure, issues, and actions, but it will weaken person-level motive and understanding claims, using labels like `one participant` or `a pushing view` instead of names. If you need precise stakeholder analysis, relabel the transcript with speaker identities first.

**My transcript quality is poor (heavy ASR errors, missing words). Is it still usable?**

Yes, mostly. The skill does not require perfect text. However, if ASR errors are severe enough to change meaning (e.g., misrecognizing a key term), flag those segments to the skill or provide a corrected version of the critical passages. Non-critical noise (filler words, minor errors) does not need cleanup.

**I want an HTML report instead of Markdown.**

Run the analysis in Markdown first. If the output is stable and report-shaped, the skill can recommend upgrading to HTML mode near the end of the analysis. See `references/html-output-mode.md`. Do not start with HTML — the analysis must be built before it is rendered.
