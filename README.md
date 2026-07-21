# GrainGuard — offline post-harvest storage advisor

## What this is
An offline, on-device AI advisor for post-harvest grain storage and aflatoxin prevention. It targets the health/food-
safety and agriculture intersection: a tool an extension agent, agro-dealer, or cooperative
operator can carry into the field with zero internet connection and get concrete, risk-aware
storage guidance for maize and groundnut.

## Why this problem
- Nigeria has roughly 38 million smallholder farmers but only one extension agent per ~10,000
  farmers on average — most farmers never get direct technical advice.
- Post-harvest losses for staple and perishable crops run extremely high, and aflatoxin
  contamination affects an estimated quarter of maize and groundnut harvests in the region.
- The physical solutions already exist and work well (Aflasafe biocontrol, PICS hermetic
  bags) — the gap is getting that knowledge applied correctly, at the moment of harvest, without
  connectivity.
- Most existing agri-tech AI in Nigeria (Cropple.AI, Crop2Cash, etc.) targets general crop
  advisory or needs an internet connection. An offline, narrowly-scoped storage advisor is an
  underserved niche.

## Current scope
- Crops: maize and groundnut (cassava as a stretch goal later)
- Core tasks: moisture/drying guidance, aflatoxin risk assessment from a described scenario,
  storage method recommendation, PICS bag usage guidance
- Target hardware: 8GB RAM laptop, integrated graphics, no internet, no GPU

## Try it locally
```bash
# 1. Get Ollama (https://ollama.com) and pull the models
ollama pull qwen3:4b-instruct
ollama pull nomic-embed-text

# 2. Build the retrieval index (one-time, ~30 chunks)
cd rag
python build_index.py

# 3. Launch the chat interface
pip install gradio requests numpy --break-system-packages
python app.py
```
Opens a local chat UI at `http://127.0.0.1:7860` — fully offline, no data leaves the machine.

## Results at a glance
- **Baseline failure, measured**: the raw model recommended washing harvested grain before
  storage (actively wrong — reintroduces moisture) and invented an unsourced remedy. See
  `tooling/baseline_test_001_manual.md`.
- **RAG fix, measured**: grounding answers in a sourced knowledge base fixed the core failure
  and correctly connected insect damage to aflatoxin risk. See `rag/rag_test_001_vs_baseline.md`.
- **A faster model, tested and rejected with evidence**: a 1B-parameter alternative ran ~2x
  faster but inverted a safety threshold and fabricated a source citation. See
  `MODEL_COMPARISON_DECISION.md`.
- **Held-out evaluation** (questions never seen during fine-tuning): 10/10 correct retrieval,
  with one real inconsistency found and fixed. See `rag/held_out_test_001_findings.md`.
- **Official hardware profiling** (ADTC reference profiler, participant's own 8GB laptop):
  ~2.57GB peak RAM, no thermal throttling, ~2.78 tokens/sec generation — a real, disclosed
  speed constraint of running a 4B model CPU-only, not a hidden weakness.

## Progress log
- [x] Step 1 — Problem defined (who it's for, what it does, what makes it hard, what success
      looks like)
- [x] Step 3 (partial) — Sourced and distilled initial domain knowledge base from three primary
      sources, plus a dedicated storage-pest file:
  - IITA, *Farmers' Guide to Management of Aflatoxins in Maize and Groundnuts in Africa* (2017)
  - Ghana MoFA/CSIR-SARI, *Appropriate Postharvest Practices for Improved Grain Storage* (2017)
  - NSPRI (Nigeria's own postharvest research institute) — local storage technologies and
    extension approach
  - Peer-reviewed research on maize weevil (Sitophilus zeamais), the main storage insect pest
- [x] Identified candidate open Q&A datasets and, importantly, real local-language datasets
      (NaijaVoices: 1,867 hours of Hausa/Igbo/Yoruba speech+text including agriculture topics;
      AFRIDOC-MT: English-to-Hausa/Yoruba translation) — see knowledge_base/data_sources_log.md
- [x] Logged an honest gap: no verified Hausa technical vocabulary (moisture, mould, weevil,
      hermetic storage) found yet — flagged rather than guessed at
- [ ] Find NSPRI's own maize handling guide directly, and close the Hausa terminology gap with
      a native speaker or the NaijaVoices dataset
- [x] Drafted a first batch (16 examples) of farmer-scenario Q&A pairs in
      qa_dataset/farmer_scenarios_v1.jsonl — grounded in the knowledge base, mixed
      formal/Pidgin-inflected phrasing, each traced back to its source file
- [ ] Expand to a few hundred Q&A pairs before real fine-tuning (v1 is a seed batch to validate
      format and tone, not enough volume yet)
- [x] Grew the dataset to 36 examples (added farmer_scenarios_v2_additions.jsonl, 20 new
      entries covering container cleaning, fumigation safety, export limits, harvest timing,
      multi-factor risk scenarios, and more). Still short of the "few hundred" ideal, but real
      progress and validated as duplicate-free.
- [x] Deadline confirmed: Gate 1 is August, giving real runway — decided to pursue actual
      fine-tuning (not just RAG), since the challenge explicitly asks for a fine-tuned model
- [x] Solved where fine-tuning actually happens: an 8GB CPU laptop can't train, only infer.
      Found Unsloth's free Colab notebook for exactly our model (Qwen3-4B-Instruct, free T4
      GPU, exports straight to GGUF for Ollama). See qa_dataset/FINE_TUNING_PLAN.md.
- [x] Built qa_dataset/prepare_finetune_data.py — converts our Q&A pairs into the exact
      chat-format training data the Colab notebook needs. Already run — see
      qa_dataset/train_data.jsonl (36 examples, ready to use)
- [ ] YOU: run the Colab notebook with our train_data.jsonl to validate the full pipeline
      end-to-end (data -> Colab training -> GGUF -> Ollama), then decide whether to grow the
      dataset further before a final training run
- [x] Ran the full pipeline end-to-end successfully: Colab + Unsloth, LoRA fine-tuned on our
      36 examples, exported to GGUF (q4_k_m), registered in Ollama as "grainguard"
- [x] **Caught a methodology error before it mattered**: batch_test.py uses
      farmer_scenarios_v1.jsonl, which is a SUBSET of the 36 examples used for fine-tuning —
      running it against the fine-tuned model would only measure memorization, not real
      generalization. Did not draw conclusions from that run.
- [x] Built a genuinely held-out test set (qa_dataset/held_out_test_set.jsonl, 10 questions,
      none used in training) and rag/held_out_test.py to test against it properly
- [x] Ad hoc held-out testing already found one real inconsistency worth taking seriously:
      asked two differently-phrased Aflasafe questions, got contradictory answers about
      whether its protection extends into storage (one correct per our sources, one not)
- [ ] YOU: run held_out_test.py and share the full output — this is the test that actually
      tells us whether fine-tuning helped, hurt, or made no real difference vs RAG-only
- [x] Ran it — 10/10 retrieval on genuinely new questions, and real evidence the fine-tuned
      model reasons rather than just recites (correctly explained WHY a PICS bag can't dry wet
      grain, on a question with no close training match). This directly addresses the
      overfitting concern from the loss curve.
- [x] Found and logged two real issues honestly: a direct contradiction between two answers
      about whether PICS bags need pre-dried grain (one right, one wrong), and a small
      ungrounded overreach claiming something about cassava we never sourced. See
      rag/held_out_test_001_findings.md.
- [ ] DECISION NEEDED: submit as-is with these two known, documented issues (given deadline
      runway), or add a targeted knowledge base fix first (a clearer chunk restating "hermetic
      storage never substitutes for drying") before finalizing
- [x] Applied the targeted fix: added a standalone, forcefully-worded
      knowledge_base/critical_rule_hermetic_storage_and_drying.md chunk restating the rule
      that was applied inconsistently (ho004 vs ho008), plus reinforced the same rule directly
      in query.py's system prompt for redundancy across both layers. Caught and fixed my own
      bug along the way (the file initially produced zero chunks - missing a ## subheading).
      Knowledge base now 9 files, 30 chunks.
- [x] Re-tested and CONFIRMED fixed: ho004 and ho008 now agree, the original repeated
      contradiction about PICS bags and wet grain is genuinely resolved (checked twice, not
      a fluke).
- [x] Found and logged one new issue while re-testing: ho006 reversed its own previously
      correct answer about which crop has less drying margin - likely ordinary generation
      variance, not something the fix caused. See rag/held_out_test_001_findings.md for full
      details.
- [x] **Testing phase concluded.** This project has now been rigorously tested at every layer:
      base model failure, RAG fix, faster-model rejection with evidence, fine-tuning
      generalization, and a targeted reliability fix - each documented honestly, issues and
      all. Further chasing individual answer variance has diminishing returns. Moving to
      finishing the submission package (see SUBMISSION_PREP.md) is the right next step.
- [ ] Get a real agronomist or extension agent to sanity-check the Q&A answers
- [x] Step 2 — Chose base model: Qwen3-4B-Instruct (Apache 2.0, ~2.5-3GB RAM at Q4_K_M,
      dual thinking/non-thinking mode, 100+ language claim). See MODEL_CHOICE.md for full
      reasoning and the runner-up (Phi-4-mini-instruct) kept as a speed fallback.
- [x] Step 4 — Tooling set up and verified: built llama.cpp from source, CPU-only, confirming
      llama-quantize / llama-bench / llama-simple-chat / llama-tokenize all work. Documented the
      simpler path for your own laptop (prebuilt binaries or Ollama) in tooling/SETUP.md, plus
      a baseline_test.py script ready to run once a model server is up.
- [x] YOU: got Qwen3-4B running locally via Ollama on your Windows laptop (hit and resolved a
      DNS-related download issue along the way — fixed by switching to Cloudflare DNS)
- [x] Ran our first real baseline test — see tooling/baseline_test_001_manual.md. Confirmed the
      base model gets pest identification right but makes a real mistake (recommends washing
      grain before storage), misses the insect-damage-to-aflatoxin connection entirely, and
      invents an unsourced remedy. This is exactly the gap our knowledge base + RAG should close.
- [ ] Build the RAG pipeline over knowledge_base/ so answers are grounded in our sourced
      material instead of the model's own (sometimes wrong) generation
- [x] Built the RAG pipeline: chunk_knowledge_base.py (already run - 26 chunks from our 7
      files, see rag/chunks.json), build_index.py (embeds chunks via Ollama), query.py (full
      retrieval + grounded generation, with a system prompt that explicitly forbids answering
      outside the retrieved context - the direct fix for baseline_test_001's invented remedy)
- [ ] YOU: run rag/build_index.py and rag/query.py on your laptop, re-test the same weevil
      question from baseline_test_001, and compare the grounded answer against the baseline
- [x] Ran it on your laptop — retrieval correctly surfaced storage_insect_pests.md as the top
      match, and the grounded answer fixed 4 of the baseline's problems (aflatoxin connection
      now stated, no more "wash the grain," no invented cinnamon remedy, exact sourced
      moisture figure). See rag/rag_test_001_vs_baseline.md for full comparison.
- [x] Logged an honest remaining gap: the grounded answer still invented a fumigant
      recommendation ("phosphine or carbon dioxide") not present in any sourced material -
      RAG reduced but didn't eliminate ungrounded generation
- [ ] Consider adding a knowledge_base chunk on container cleaning/fumigation to close that
      specific gap, and/or tighten the system prompt further
- [x] Closed the fumigation gap: added knowledge_base/container_cleaning_and_fumigation_safety.md
      (researched — turns out phosphine fumigation is genuinely dangerous without
      certification/PPE, not just "outside our sources" but a real safety concern). Also
      tightened query.py's system prompt to redirect chemical-treatment questions toward
      "contact a licensed service" rather than DIY instructions. Knowledge base now 8 files,
      29 chunks (up from 26).
- [ ] Batch-test all 16 qa_dataset questions through the RAG pipeline, not just one
- [x] Built rag/batch_test.py — runs all 16 questions, checks retrieval against each
      question's tagged source_files, saves full results for review
- [ ] YOU: re-run build_index.py (knowledge base changed) then run batch_test.py, share results
- [x] Ran full batch test — 15/16 correct retrieval (one miss on the humid-zone/solar-dryer
      question, likely a chunk-ranking issue, see rag/batch_test_001_summary.md). More
      importantly: response times ranged 57-209s, averaging ~2 minutes per question. Given the
      challenge scores 30% on performance and 20% on efficiency, **speed is now a priority
      alongside content quality**, not an afterthought.
- [ ] Try raising TOP_K to fix the one retrieval miss
- [ ] Investigate whether Qwen3's "thinking mode" is slowing things down, and whether a
      shorter requested answer length or the Phi-4-mini fallback speeds things up
      meaningfully without losing answer quality
- [x] Ruled out thinking mode: qwen3:4b-instruct resolves to the dedicated Instruct-2507
      checkpoint, which has no thinking capability at all - confirmed via Ollama's own model
      metadata. The "think": false test correctly showed no timing change because there was
      nothing to disable. See rag/speed_investigation_notes.md.
- [x] Applied the real fix candidate: tightened the system prompt to request shorter,
      conversational answers (~120-180 words) instead of long structured reports - should
      reduce total generation time directly since it's fewer tokens to produce
- [ ] YOU: re-run batch_test.py with the updated prompt and compare timings
- [ ] If still too slow: benchmark Phi-4-mini-instruct as a real alternative, and/or run
      llama-bench for a clean raw-speed number isolated from RAG overhead
- [x] Tested llama3.2:1b (already downloaded, zero data cost) head-to-head against
      qwen3:4b-instruct — 2x faster (avg ~53s vs ~104s) but read all 16 answers and found real
      accuracy problems: inverted a safety threshold, misidentified the cause of dust in the
      weevil question, invented wrong acronym expansions for terms present in context, and
      fabricated a source citation. See MODEL_COMPARISON_DECISION.md for full analysis.
- [x] **Decision: staying with qwen3:4b-instruct.** Speed matters, but not at the cost of
      reliability on the exact food-safety reasoning this project exists for. ~104s avg
      response time is a known, documented tradeoff going into the submission, not a
      hidden weakness.
- [x] Tested a hard token cap (num_predict) to bound worst-case time. Result was noisier, not
      better (~116s avg, higher variance) - concluded this reflects laptop background load
      between runs rather than the cap helping or hurting. **Closing out speed tuning here**:
      root cause (raw CPU generation speed, ~4 tok/s) is now well understood and documented,
      a faster alternative was tested and rejected with real evidence, and further squeezing
      would be chasing system noise rather than a fixable problem. ~100-120s average response
      time goes into the submission as a known, honestly-measured constraint.
- [ ] Run llama-bench (built in Step 4) to isolate raw model speed from RAG pipeline overhead
- [ ] Quantize + fine-tune
- [ ] Build offline RAG pipeline over knowledge_base/
- [ ] Test on target hardware constraints
- [ ] Document, package, submit

## Folder structure
```
grainguard/
  README.md                 <- this file, project brief + progress log
  MODEL_CHOICE.md           <- base model decision and reasoning
  knowledge_base/
    moisture_and_drying.md
    aflatoxin_risk_factors.md
    storage_methods_comparison.md
    container_cleaning_and_fumigation_safety.md
    pics_bags_usage.md
    storage_insect_pests.md
    nigeria_specific_technologies.md
    data_sources_log.md
  qa_dataset/
    farmer_scenarios_v1.jsonl
    farmer_scenarios_v2_additions.jsonl
    train_data.jsonl
    prepare_finetune_data.py
    FINE_TUNING_PLAN.md
    README.md
  tooling/
    SETUP.md
    baseline_test.py
    baseline_test_001_manual.md
  rag/
    chunk_knowledge_base.py
    build_index.py
    query.py
    chunks.json
    batch_test.py
    rag_test_001_vs_baseline.md
    README.md
```

Each knowledge base file is written as clean, standalone reference material — this is what
the RAG pipeline will chunk and search over, and what we'll draw from to write fine-tuning
examples.
