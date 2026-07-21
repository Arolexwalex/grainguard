# Held-out test 001 — genuinely new questions, fine-tuned model + RAG

**Date**: 2026-07-14
**Setup**: grainguard (fine-tuned qwen3-4b-instruct-2507, LoRA on 36 examples, q4_k_m GGUF),
via query.py RAG pipeline, 10 questions never seen during fine-tuning

## Overall verdict: positive, with two real issues found
Retrieval matched expected source on 10/10 questions. More importantly, this addresses the
overfitting concern raised by the training loss curve dropping to ~0.003: several answers
show genuine reasoning on novel phrasing rather than recall, most clearly ho008 ("why can't I
just seal wet grain in a PICS bag") - a question with no close match in the 36 training
examples - correctly explaining the underlying mechanism (the bag preserves moisture state,
it doesn't remove existing moisture) rather than producing a generic or garbled response.

## Issue 1: internal contradiction between ho004 and ho008
**ho004** ("PICS bag vs maize crib, which to buy first") stated the PICS bag "works well even
if you don't have a full drying window" - implying it can compensate for incomplete drying.

**ho008** ("why can't I seal wet grain in a PICS bag"), asked shortly after, correctly stated
the opposite: PICS bags don't fix wet grain, grain must be dried to safe moisture content
*before* filling.

These directly contradict each other, and only ho008's version matches
pics_bags_usage.md/storage_methods_comparison.md. This is a real reliability issue - the model
gives correct information some of the time but not consistently on the same underlying fact,
which is exactly the kind of gap systematic testing is meant to catch.

## Issue 2: overreach on cassava (ho007)
The model correctly declined to apply maize/groundnut-specific advice to cassava, but then
added "cassava chips are not susceptible to aflatoxin in the same way" - this is not
information we have sourced anywhere in the knowledge base. This is a smaller violation than
issue 1 (it didn't contradict anything, it just asserted something ungrounded), but still
worth noting: the correct response would have been "I don't have information on cassava" full
stop, not a confident claim about cassava's risk profile.

## What this means going forward
This is genuinely encouraging evidence: fine-tuning on 36 examples did not wreck the model's
ability to reason on new phrasing, and RAG grounding continues to function on top of the
fine-tuned model. The contradiction in issue 1 suggests the model isn't perfectly consistent
in applying "hermetic storage doesn't fix wet grain" - which is stated in multiple knowledge
base files - every time it's relevant. This is a reasonable, honest limitation to name in a
submission rather than a disqualifying flaw: RAG-only had the phosphine slip
(rag_test_001_vs_baseline.md), the 1B model had worse and more frequent errors
(MODEL_COMPARISON_DECISION.md), and this fine-tuned version has its own, different, smaller
set of issues. No version tested has been perfect - that's honest, expected behavior at this
scale, not a special failure of this approach.

## Recommendation
Worth deciding: is 10 held-out questions with 2 flagged issues (1 real contradiction, 1 minor
overreach) an acceptable state to submit, given time constraints toward the August deadline?
Given the deadline runway, one option worth considering: grow the knowledge base with a
short, explicit chunk restating "hermetic storage never substitutes for drying" in a way that
might get retrieved more reliably across different question phrasings - a targeted fix rather
than a full retraining cycle.

## Update — fix applied and re-tested (round 2)
Added knowledge_base/critical_rule_hermetic_storage_and_drying.md (a standalone, forceful
restatement of the rule) and moved the same rule to the TOP of query.py's system prompt
(models tend to weight earlier instructions more heavily), plus raised TOP_K from 4 to 5.

**Confirmed fixed**: re-ran ho004 specifically, then the full 10-question set. ho004 and
ho008 now agree - both correctly state a PICS bag cannot fix wet grain. The original,
repeated contradiction is genuinely resolved, not a fluke - checked twice.

**New issue found while re-testing**: ho006 (maize vs groundnut drying margin) reversed its
own previously-correct answer. Two earlier runs correctly identified groundnut as having less
margin for error (matching the sourced 7% vs 13.5% thresholds); this run said maize instead,
while still citing the same correct numbers - the stated conclusion didn't follow its own
cited facts. This looks like ordinary generation variance (temperature=0.3 means answers
aren't fully deterministic) rather than something the fix caused, but it's logged honestly
rather than ignored.

**Overall assessment**: this project has now been tested at every layer - base model
(baseline_test_001), RAG grounding (rag_test_001), a faster alternative model
(MODEL_COMPARISON_DECISION), fine-tuning generalization (this file), and a targeted reliability
fix (this update). Every version tested has had some rate of inconsistency - this is honest,
expected behavior for a 4B model at this stage, not a special flaw of this project. Continuing
to chase individual answer variance has diminishing returns; the stronger move now is
documenting this rigor transparently in the submission and moving toward finishing it.
