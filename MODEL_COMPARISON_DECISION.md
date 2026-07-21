# Model comparison: qwen3:4b-instruct vs llama3.2:1b — decision

**Date**: 2026-07-11

## Speed
| Model | Raw eval rate | Batch test avg | Batch test range |
|---|---|---|---|
| qwen3:4b-instruct | 4.07 tok/s | ~104s | 77-148s |
| llama3.2:1b | 7.94 tok/s | ~53s | 34-76s |

Roughly 2x speed gain with the 1B model - a real, measurable difference on this hardware.

## Quality — read all 16 answers from each model, found real problems with llama3.2:1b
that go beyond "less detailed" and into actively wrong or fabricated:

1. **qa011, qa012 — invented wrong acronym expansions.** Called PICS "Plastic Inner Chambered
   Silo." The correct expansion (Purdue Improved Crop Storage) is stated directly in the
   retrieved context (pics_bags_usage.md). This is the model overriding a fact that was
   literally in front of it with a fabricated one - a more concerning failure mode than simply
   missing information.
2. **qa007 — misidentified the cause of the dust** in the weevil question (arguably our most
   important diagnostic scenario). Said it's "fungi and bacteria" growing; the source material
   is clear it's insect frass/debris. Wrong on the core reasoning task this project centers on.
3. **qa002 — inverted a safety threshold.** Source material states humidity above 65-70% is
   the point where mould risk rises - a ceiling to stay under. The model presented this as a
   target ("aim for air inside storage room to be around 65-70%"), which is backwards and
   would actively encourage worse storage conditions if followed.
4. **qa016 — fabricated a source citation.** Attributed specific claims to "FAO Nigeria,"
   which was never actually a source we had - data_sources_log.md lists FAO Nigeria
   publications under "still to source," not "found." The model invented an authority that
   doesn't exist in our material.
5. Recurring stylistic incoherence - several answers open with an apparent refusal ("I can't
   help with that" / "I can't advise you on that") and then immediately answer anyway. Not
   dangerous, but would look unpolished and confusing in a live demo.

qwen3:4b-instruct's only comparable issue across our tests (the phosphine suggestion in
rag_test_001_vs_baseline.md) was a case of reaching outside the provided context for a
plausible addition - a different, more defensible failure mode than misreading or inventing
facts that contradict what was directly retrieved.

## Decision: keep qwen3:4b-instruct as the primary model
The 2x speed gain doesn't outweigh a real increase in ungrounded and factually inverted
answers, especially for a project centered on food-safety guidance where getting the
moisture/mould threshold or the pest diagnosis wrong has real consequences. Speed is a genuine
constraint worth continuing to optimize (see speed_investigation_notes.md), but not by
swapping to a model that's demonstrably less reliable on the exact reasoning tasks this
project is built around.

This comparison itself - having tested a real alternative, with evidence, rather than assuming
either "smaller is fine" or "bigger is always better" - is worth keeping in the submission
writeup. It shows the model choice was actually validated, not just picked from a
spec sheet.
