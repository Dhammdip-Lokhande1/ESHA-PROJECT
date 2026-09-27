# AGENTS.md
## Standing instructions for every agent working in this workspace

Read `INSTRUCTIONS.md` in full before taking any action — it is the single source of truth for this rebuild (product requirements, tech stack, module interfaces, UI/UX spec, API contract, DB schema, milestones, and definition of done all live there).

## Working process

1. Confirm current milestone by checking the "Current status" block below.
2. Re-read the relevant section(s) of `INSTRUCTIONS.md` for that milestone.
3. Produce a Task List / Implementation Plan before writing code. Pause for review if working in Antigravity's agent-assisted mode.
4. Build the module + its full test set (section 13 of INSTRUCTIONS.md).
5. Run the Definition of Done checklist (section 16) before marking anything complete.
6. Log the review to `experiments/review_log.csv`.
7. Update the "Current status" block below.

## Non-negotiables (repeated here because they're the most commonly violated)

- No score without evidence attached (Non-Negotiable Rule 2).
- The behavioral module MUST be wired into `/api/v1/analyze` — this was silently skipped in a prior build. Verify explicitly during M4's review pass.
- Evidence must be persisted to the `evidence` DB table, not just returned in API JSON — this was also silently skipped previously.
- Zero cost — no paid APIs, no paid hosting tier, ever, for the core pipeline.
- Do not skip M4.5 (adaptive fusion) or M10 (real instructor study data) under time pressure — these are the two milestones that differentiate this build from prior versions and from existing published work.

## Current status

```
Current milestone: ALL PHASES 1-7 RIGOROUS EVALUATION, HARDENING & THESIS SYNC COMPLETE & VERIFIED
Last completed: Phase 1 Fair Evaluation, Phase 2 TransBench-Lite Benchmark, Phase 3 External Baselines & 15-Channel Ablation, Phase 4 Transformation Classifier & DecisionTree, Phase 5 Code Hardening & Inventory, Phase 6 Adaptive Learning Curve Study, Phase 7 Thesis Complete Source Synchronization
Next up: Ready for final thesis defense and paper publication!
```

