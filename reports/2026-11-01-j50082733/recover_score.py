import copy
import hashlib
import json
import os
import shutil
from pathlib import Path

from two_gpu_search import Experiment
from meta_harness import meta_harness_chess_puzzle as mh

out = Path(os.environ["SWITCH_OUT"])
session = Path(os.environ["AGENT_SESSION_DIR"])
source = session / "search"
archive = Path((source / "harness-run-dir").read_text().strip())
logs = out / "logs"
names = ["h1", "h2", "h3"]

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")

assert json.loads((session / "train/passed.json").read_text())["passed"]
original = json.loads((archive / "pending_eval.json").read_text())
candidates = copy.deepcopy(original["candidates"])
for candidate in candidates:
    candidate["name"] = candidate.get("name") or candidate.get("harness")
assert [c["name"] for c in candidates] == names

shutil.copy2(archive / "pending_eval.json",
             out / "pending_eval.original.json")
save(out / "pending_eval.json", {"candidates": candidates})

hashes = {}
for name in ["h0"] + names:
    src = archive / "harnesses" / name / "harness.py"
    dst = out / "harnesses" / name / "harness.py"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    hashes[name] = hashlib.sha256(src.read_bytes()).hexdigest()
    assert hashlib.sha256(dst.read_bytes()).hexdigest() == hashes[name]
    mh.validate_candidate(out, name)

shutil.copytree(archive / "logs/mh_val/h0", logs / "mh_val/h0")
config = json.loads((source / "state/mh_config.json").read_text())
assert len(config["models"]) == 1
config["models"][0]["api_base"] = (
    f"http://127.0.0.1:{os.environ['SOLVER_PORT']}/v1"
)
config["models"][0]["batch_concurrency"] = 256
save(Path(os.environ["SWITCH_CONFIG"]), config)
save(out / "recovery-manifest.json", {
    "manual_recovery": True,
    "original_search_passed": False,
    "original_archive": str(archive),
    "checkpoint": os.environ["SWITCH_CHECKPOINT"],
    "repair": "Add top-level name from harness; candidate code unchanged.",
    "new_proposals": 0,
    "baseline_reused": True,
    "expected_new_scoring_rollouts": 768,
    "harness_sha256": hashes,
})

experiment = Experiment()
try:
    experiment.status("manual recovery: loading two B1 solvers")
    experiment.start("solver0")
    experiment.start("solver1")
    experiment.check_model("solver0")
    experiment.check_model("solver1")
    experiment.pool.enable([0, 1])
    before = experiment.pool.snapshot()

    for name in names:
        experiment.status(f"manual recovery: scoring {name}")
        results = mh.run_sweep(
            copy.deepcopy(experiment.config),
            [(name, out / "harnesses" / name / "harness.py")],
            logs,
            force=False,
        )
        assert len(results) == 1 and results[0][1], results
        experiment.validate_scores(logs, [name])

    after = experiment.pool.snapshot()
    assert after["failed"] == before["failed"], "Solver request failed"
    assert all(after["completed"][i] > before["completed"][i]
               for i in (0, 1)), "Both GPUs must score requests"
    experiment.validate_scores(logs, ["h0"] + names)

    frontier = mh.print_frontier(logs, experiment.config)
    rows = mh.candidate_summary_rows(1, candidates, logs, frontier)
    early = mh.find_early_stop_candidate(rows, names, 1.0)
    accepted = early["harness"] if early else mh.pick_accepted(frontier, out)
    mh.set_accepted_harness(out, accepted)
    mh.append_evolution_summary(out, rows)

    save(out / "comparison.json", {
        "accepted_harness": accepted,
        "summary": rows,
        "frontier": frontier,
    })
    save(out / "recovery-passed.json", {
        "passed": True,
        "manual_recovery": True,
        "new_proposals": 0,
        "baseline_reused": True,
        "new_scoring_rollouts": 768,
        "accepted_harness": accepted,
    })
    print("MANUAL RECOVERY PASSED; selected harness:", accepted, flush=True)
except BaseException as exc:
    experiment.event("recovery_failure",
                     type=type(exc).__name__, message=str(exc))
    raise
finally:
    experiment.close()
