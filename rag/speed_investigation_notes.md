# Speed investigation — thinking mode ruled out

**Finding**: `qwen3:4b-instruct` in Ollama resolves to the Qwen3-4B-**Instruct-2507**
checkpoint - a dedicated non-thinking release. Alibaba split their original "hybrid
thinking" models into separate Instruct (no reasoning trace) and Thinking (always-reasoning)
variants in their July 2025 refresh specifically because the hybrid models underperformed.
Confirmed by matching the model's blob hash against Ollama's own library metadata.

**What this means**: adding `"think": false` to the API call had no effect on timing because
there was no thinking pass running in the first place - this model was never capable of it.
The ~2 minute average response time is just raw CPU generation time for a fairly long,
structured answer, not reasoning overhead.

**Next fix applied**: tightened the system prompt to explicitly request shorter, more
conversational answers (~120-180 words guideline) instead of long structured reports with many
headers - this should reduce total tokens generated per answer, which directly reduces time on
CPU-only hardware.

**Still worth testing if this isn't enough**:
- Benchmark the Phi-4-mini-instruct fallback from MODEL_CHOICE.md - independent 2026 sources
  specifically flagged it as the fastest CPU-only performer in its size class
- Run llama-bench (built and verified in Step 4) for a clean tokens/sec number isolated from
  RAG overhead, to separate "model is inherently slow on this hardware" from "our answers are
  just too long"

## Root cause found: raw model speed on this hardware

`ollama run qwen3:4b-instruct --verbose` gave a direct, uncontestable number:
**eval rate: 4.07 tokens/s**. This is genuinely slow for a 4B model - independent benchmarks
for this size class typically report 10-20+ tokens/sec on capable CPUs. This rules out
pipeline overhead, prompt verbosity, and thinking mode as primary causes - the bottleneck is
the laptop's raw CPU throughput for this model size.

The math checks out: at ~4 tok/s, a 150-200 word answer (~200-250 tokens) takes 50-65 seconds
of pure generation time, which lines up with the 77-148s range seen in the last batch test once
prompt processing and RAG context are added on top.

**This is a legitimate, evidence-backed finding for the submission** - not a bug to hide, but
a real data point about how this model size performs on constrained hardware, exactly the kind
of measurement the challenge's performance/efficiency scoring is looking for.

**Next test (zero data cost - already downloaded)**: try `llama3.2:1b`, which was already
pulled during earlier network troubleshooting. A 1B model should generate meaningfully faster
than 4B on the same CPU, since compute scales roughly with parameter count. Worth checking
whether the speed gain is worth any quality tradeoff, using the same
`ollama run llama3.2:1b --verbose` test first, then a full batch_test.py run if the tokens/sec
number looks promising.
