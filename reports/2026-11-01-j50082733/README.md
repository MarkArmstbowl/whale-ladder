# Yubo's B1 run: handoff for teammates already using whale-ladder

This run used the PR #1–#3 stack at `f84ea4720b7ecd0eb4c5123fff2b0f6bacc3e323`.
Implementation credit remains with the original repository and PR authors.
I started from the pinned original Qwen3.5-4B, not a teammate's trained model.

## Results

- One training batch: 256 puzzles x 8 attempts = 2,048 rollouts.
- 90 successful trajectories from 40 distinct training inputs; one SFT epoch,
  two optimizer updates; saved B1 at `global_step_1`.
- Small post-update test: 0/32 attempts on 16 different test puzzles.
  There was no matched pre-update test, so this is not a before/after comparison.
- Frozen base Qwen proposer generated h1–h3. The automatic search stopped on
  a `name`/`harness` manifest mismatch; the requested JSON schema was underspecified.
- A separate recovery added only candidate names to the manifest. Candidate
  code was unchanged, no extra proposals were generated, and baseline was reused.
- Search-validation successes: h0=5/256; h1=17/256; h2=0/256; h3=7/256.
  h1 was selected. This is not a final held-out test improvement.
- B2 has not run. The proposer was frozen base 4B, not the self-proposer arm.

## Where the new work is shared

All files are in this one public model repository:
https://huggingface.co/Marstbowl/whale-chess-qwen35-4b-b1-20261101-j50082733

- Root: full B1 model for standard HF/vLLM loading.
- `training_checkpoint/`: original two-rank checkpoint, including actor shards,
  extra state and data.pt, for the existing hybrid runner's resume interface.
- `harnesses/`: the three newly generated candidates, h1, h2 and h3.
- `handoff/`: this report, continuation instructions, dependency record,
  results/identity, and an archive of the new training/search/recovery records.

Original model-only revision: `b90dde873760e2013c2381a9c7a074cf3b5e9f5d`.
The final handoff commit is recorded in `UPLOAD_RECEIPT.json` in the fork report.

## What you already have

No original repository, base-model cache, environment or datasets were repackaged.
Use your existing checkout/environment, checked against the tested commit and
`handoff/pip-freeze.txt`. Data fingerprint: `91c2fe70efad772c`. The upstream data
download is not pinned, so compare fingerprints before treating runs as matched.
If they differ, agree on one dataset; do not silently mix splits.

The raw checkpoint saves model, scheduler/RNG and dataloader state, but no Adam
optimizer state. Resume will rebuild Adam. Cross-machine resume still needs a
smoke check; the shared files remove the need to access my PSC account.

GitHub report:
https://github.com/MarkArmstbowl/whale-ladder/blob/yubo/psc-validation/reports/2026-11-01-j50082733/README.md

See NEXT_STEPS.md for the exact existing-runner inputs.
