# Baseline test 001 — pre-fine-tuning, pre-RAG

**Date**: 2026-07-11
**Model**: qwen3:4b-instruct, run via `ollama run`, no system prompt, no RAG, no fine-tuning
**Question** (matches qa_dataset qa007): "My maize harvest has small holes in the kernels and
some dust at the bottom of the bag. What is this and what should I do?"

## Raw model answer
Correctly identified maize weevil (Sitophilus zeamais) as the likely cause and frass as the
dust source. Structured the answer with severity assessment, sorting/discarding damaged
kernels, drying, storage in airtight containers, and prevention tips.

## Gaps identified against our knowledge base
1. **Recommended washing the maize before drying.** This is actively counter to
   moisture_and_drying.md - washing reintroduces moisture right before the step where the goal
   is to reach and maintain safe moisture content. A real risk of bad advice, not just a
   missing nicety.
2. **No connection made to aflatoxin risk at all**, despite this being one of the most
   important points in storage_insect_pests.md - that insect damage creates entry wounds for
   mould, compounding the two risks together. The model treated this as a pest-only problem.
3. **Suggested containers (glass jars, vacuum-sealed bags) rather than PICS bags** - not wrong
   in principle, but disconnected from the specific, field-tested, regionally-available
   solution (PICS bags, hermetic storage) that our sourced material centers on.
4. **Invented a specific remedy** ("cinnamon or clove oil soak, 10-15 minutes") with no
   traceable source. This is the clearest example of ungrounded generation - confident,
   specific, and not verifiable against anything we sourced. Also introduces moisture right
   before drying, compounding gap #1.
5. Generic, global tone (uses "vacuum-sealed bags," emoji, no Nigeria-specific reference to
   NSPRI, Aflasafe, or PICS bags by name).

## What this tells us
The base model's actual knowledge of maize weevils is decent - it's not wrong about the pest
identification. What's missing is (a) grounding to a specific, sourced, regionally-relevant set
of solutions, and (b) reasoning about compounded risk (insect damage -> aflatoxin) rather than
treating problems as isolated. This is exactly the gap RAG + fine-tuning on our knowledge base
is meant to close. This baseline is worth re-running with the same question once RAG is wired
up, to directly compare.
