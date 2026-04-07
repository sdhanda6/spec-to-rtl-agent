from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from spec2rtl.spec_ingest import load_spec_source


ROOT = Path(__file__).resolve().parent
BUILD_DIR = ROOT / "build"
SUMMARY_PATH = BUILD_DIR / "reports" / "generalized_repair_demo_summary.yaml"


DEMOS = [
    ("examples/specs/upcounter16.yaml", "counter_hold_when_enabled"),
    ("examples/specs/register8.yaml", "register_hold_when_enabled"),
    ("examples/specs/shift_left4.yaml", "shift_reverse_direction"),
    ("examples/specs/fsm_handshake.yaml", "fsm_force_self_loop"),
    ("examples/specs/comb_adder8.yaml", "zero_output:y"),
    ("examples/specs/sum_stage.yaml", "zero_output:sum_out"),
    ("examples/specs/text_counter.txt", "zero_output:count"),
]


def infer_top(spec_path: Path) -> str:
    parsed = load_spec_source(spec_path)
    if not parsed.candidates:
        return spec_path.stem
    module = parsed.candidates[0].document.get("module", {})
    if isinstance(module, dict) and module.get("name"):
        return str(module["name"])
    return spec_path.stem


def render_summary(items: list[dict[str, object]]) -> str:
    lines = ["demo_runs:"]
    for item in items:
        first = True
        for key, value in item.items():
            prefix = "  - " if first else "    "
            lines.append(f"{prefix}{key}: {value}")
            first = False
    return "\n".join(lines) + "\n"


def main() -> int:
    BUILD_DIR.mkdir(exist_ok=True)
    results: list[dict[str, object]] = []
    overall_rc = 0
    for spec_rel, fault in DEMOS:
        spec_path = ROOT / spec_rel
        top = infer_top(spec_path)
        cmd = [
            sys.executable,
            "agent.py",
            "--spec",
            str(spec_path),
            "--verify",
            "sim",
            "--max-passes",
            "3",
            "--overwrite",
            "--inject-fault",
            fault,
        ]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        report = ROOT / "build" / "reports" / f"{top}_report.yaml"
        results.append(
            {
                "spec": spec_rel,
                "top": top,
                "fault": fault,
                "returncode": proc.returncode,
                "report": report.relative_to(ROOT),
            }
        )
        if proc.stdout:
            print(proc.stdout.rstrip())
        if proc.stderr:
            print(proc.stderr.rstrip(), file=sys.stderr)
        overall_rc = max(overall_rc, proc.returncode)

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(render_summary(results), encoding="utf-8")
    print(f"Demo summary: {SUMMARY_PATH.relative_to(ROOT)}")
    return overall_rc


if __name__ == "__main__":
    sys.exit(main())
