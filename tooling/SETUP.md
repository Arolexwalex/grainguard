# Step 4: tooling setup

## What I actually verified (in this sandbox, right now)
I cloned `llama.cpp` from source and built it CPU-only — no GPU, no Metal — matching the
challenge's hardware constraint exactly. This confirms the toolchain is real and works, not
just theoretical instructions. Built and tested successfully:
- `llama-quantize` — compresses a full-precision model into GGUF at a chosen bit-width
- `llama-bench` — measures tokens/sec, load time, memory — this is our profiling tool for the
  "test on target hardware" step later
- `llama-simple-chat` / `llama-simple` — minimal CLI for running a GGUF model directly
- `llama-tokenize` — inspects how text gets split into tokens

The exact commands that worked, for the record:
```bash
git clone --depth 1 https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
cmake -B build -DGGML_NATIVE=OFF -DGGML_CUDA=OFF -DGGML_METAL=OFF -DLLAMA_CURL=OFF
cmake --build build --config Release -j $(nproc) --target llama-quantize llama-bench llama-simple-chat llama-simple llama-tokenize
```

## What I could NOT do here, and why
This sandbox can only reach a fixed allowlist of domains (GitHub, PyPI, npm, a few others) —
it cannot reach Hugging Face or Ollama's servers, so I can't actually download the multi-gigabyte
Qwen3-4B model weights from inside this environment. That download has to happen on your own
machine. This is a real constraint of where I'm running, not a step being skipped.

I also hit one build quirk worth knowing: building the full `llama-server` binary pulls in a
web UI that gets compiled with npm/vite, which stalled in this sandbox's restricted network. On
your own laptop with normal internet access this will very likely build fine, but if it's slow,
building without the server target (as I did) is a safe workaround — you don't lose any of the
tools you actually need for quantization and benchmarking.

## What you should do on your own laptop

**Easiest path — skip building entirely.** llama.cpp publishes ready-made binaries:
1. Go to `https://github.com/ggml-org/llama.cpp/releases`, download the zip matching your OS
   (Linux, macOS, or Windows; CPU-only build if you don't have a dedicated GPU).
2. Unzip it. You now have `llama-server`, `llama-cli`, `llama-bench`, `llama-quantize` ready to
   run, no compiler needed.
3. Run the model directly from Hugging Face without a separate download step:
   ```bash
   ./llama-server -hf Qwen/Qwen3-4B-GGUF -c 4096
   ```
   This pulls the GGUF automatically and starts an OpenAI-compatible local API server at
   `http://localhost:8080` — which is what our RAG pipeline (next major step) will talk to.

**Alternative — Ollama**, if you prefer a simpler day-to-day interface:
```bash
ollama pull qwen3:4b-instruct
ollama run qwen3:4b-instruct
```
Ollama runs its own local API at `http://localhost:11434` by default.

**If you want to build from source** (e.g. to match our verified CPU-only config exactly, or
if you'll need custom flags later): use the same cmake commands shown above. Expect the full
build including the server to take longer the first time due to the web UI compile step.

## Immediate next actions once you have this running
1. Confirm the server responds: `curl http://localhost:8080/health` (llama.cpp) or
   `curl http://localhost:11434/api/tags` (Ollama)
2. Run `llama-bench -m <path-to-qwen3-4b.gguf>` to get a real number for tokens/sec, load time,
   and memory on your actual hardware — this becomes our first real hardware profiling result
3. Ask the model 3-4 questions from `qa_dataset/farmer_scenarios_v1.jsonl` **before any
   fine-tuning**, and save the raw answers. This is our baseline — the only way to later prove
   that fine-tuning and RAG actually improved anything is to have a "before" to compare against.
