# Honest Limits

This file records explicit capability boundaries for `biz-retro-analyzer`.

The point is not to make the skill look weaker. The point is to prevent it from producing confident but useless analysis in situations where its assumptions do not hold.

---

## Performative Meetings

There is one kind of meeting this skill cannot analyze well, and probably never will.

Some meetings are **performative**. Everyone speaks smoothly. Everyone agrees. The minutes are clean. And none of it is meant to be examined — because the real decision was made before the meeting, in a smaller room, by fewer people. The meeting exists so the decision can be seen being made.

In these meetings, smoothness is not a signal to investigate. It is the product. The alignment is not fragile or false — it is deliberately manufactured, and it is working exactly as intended.

This skill is built to do the opposite of that. Its toolkit — evidence layering, motive analysis, consensus reality checks, reverse audit — exists to resist smoothness and find the crack under the surface. But when the surface is the point, there is no crack to find. The most sophisticated analysis will only produce sophisticated false positives: flagging correct performance as false consensus, or hunting for hidden motives where the motive is simply to let the meeting end.

This is not a bug to fix. It is the shape of a real organizational pattern.

The deeper irony: in a performative meeting, not everyone is performing. A few people wrote the script. Some are reading from it knowingly. And one or two may believe the meeting is real. Their sincerity is genuine, and their genuine input may be the only honest signal in the room. A perfectly executed performance often contains exactly one person who does not know it is a performance. This skill cannot reliably tell you which one.

So: if your meeting was smooth because the work was done, this skill can help you see what was left unsaid. But if your meeting was smooth because the smoothness was the work, there is nothing here for you — and that itself may be the most honest finding available.

---

## Practical Rule

Before applying this skill to a very smooth meeting, ask:

- Was the meeting meant to decide something, or to display a decision already made?
- Did participants have room to change the outcome?
- Did disagreement have a legitimate path to affect the next step?
- Did the meeting produce new information, or only ratify prior alignment?

If the answer is mostly the latter, use this skill cautiously. Treat most deep motive or false-consensus readings as `Needs validation`.

---

## Output Guidance

If the input appears performative, the output should say so plainly.

Recommended wording:

```md
This material may be a performative or ratification meeting. The transcript is too smooth to support a deep motive or conflict analysis. The likely finding is not hidden disagreement, but that the real decision path happened outside this source material.
```

Do not force a full motive map or influence-chain analysis when the source is only a staged surface.
