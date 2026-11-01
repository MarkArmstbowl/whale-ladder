# Continue using your existing whale-ladder setup

You do not need my PSC account. Use your own existing two-H100 allocation,
whale-ladder checkout, WHALE installation and data. Check code commit
f84ea4720b7ecd0eb4c5123fff2b0f6bacc3e323 and the recorded dependency versions.

## 1. Download only the new handoff files

Use the final revision in the fork's UPLOAD_RECEIPT.json. With Python and
huggingface_hub available, set SHARED to independent writable storage and run:

    from huggingface_hub import snapshot_download
    snapshot_download(
        repo_id="Marstbowl/whale-chess-qwen35-4b-b1-20261101-j50082733",
        revision="FINAL_HANDOFF_REVISION_FROM_UPLOAD_RECEIPT",
        local_dir="/your/independent/storage/b1-shared",
        allow_patterns=["training_checkpoint/**", "harnesses/**", "handoff/**"],
    )

This intentionally skips the root HF inference-weight duplicate. If you only
want normal inference or a fresh fine-tune from B1 weights, load the root model
at the original model revision b90dde873760e2013c2381a9c7a074cf3b5e9f5d instead.

## 2. Confirm your existing data

Inside your existing activated environment, from your whale-ladder checkout:

    python tools/data_fingerprint.py "$LADDER_ROOT/WHALE/domains/chess_puzzles/data/chess_puzzle"

The recorded fingerprint is 91c2fe70efad772c. A mismatch is not a missing
checkpoint: it means the unpinned dataset downloads differ. Agree on consistent
data before claiming matched results. The existing datasets were not re-uploaded.

## 3. Proposed B2: reuse the original runner's checkpoint input

Set LADDER_ROOT to YOUR existing work directory, SHARED to the downloaded
b1-shared directory, and run from YOUR whale-ladder checkout inside a two-H100
allocation. Keep your normal runtime/cache/compiler setup:

    test -d "$SHARED/training_checkpoint/global_step_1/actor"
    test -f "$SHARED/training_checkpoint/global_step_1/data.pt"
    test -f "$SHARED/harnesses/h1/harness.py"
    HARNESS_PATH="$SHARED/harnesses/h1/harness.py" \
    HYBRID_RESUME_CHECKPOINT="$SHARED/training_checkpoint/global_step_1" \
    HYBRID_MODE=train HYBRID_TRAINING_STEPS=1 \
    HYBRID_RUN_NAME="b2-j${SLURM_JOB_ID}" \
    bash ladder/hybrid_test.sh "$LADDER_ROOT/review/b2-j${SLURM_JOB_ID}"

The directory already ends with global_step_1 as required by the runner.
Use a fresh output directory. Verify the resolved config and receipt show
start_step=1 and target_step=2, with the selected h1 imported by workers.
Do not assume a directory name alone proves resume worked.

B2 was not run here. This is a proposed continuation with Adam state reset,
not a claim of uninterrupted training or an independently tested cross-host
resume. The harness was selected after manual metadata recovery; label that
intervention when reporting the resulting experiment.
