from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from spec2rtl.frontend import load_spec_document
from spec2rtl.lowering import lower_document_to_ir


ROOT = Path(__file__).resolve().parent
BUILD_DIR = ROOT / "build"
LOG_DIR = BUILD_DIR / "logs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full YAML Spec-to-RTL pipeline")
    parser.add_argument("--spec", type=Path, default=ROOT / "spec.yaml", help="Path to a YAML spec")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated outputs")
    return parser.parse_args()


def resolve_spec(spec: Path) -> Path:
    path = spec if spec.is_absolute() else ROOT / spec
    if path.suffix.lower() not in {".yaml", ".yml"}:
        raise ValueError(f"Only YAML specs are supported: {path}")
    return path


def infer_top(spec_path: Path) -> str:
    document = load_spec_document(spec_path)
    ir = lower_document_to_ir(document)
    return ir.name


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True)


def write_log(top: str, sections: list[tuple[str, str]]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"{top}_pipeline.log"
    parts: list[str] = []
    for title, body in sections:
        parts.append(f"## {title}")
        parts.append(body.rstrip())
        parts.append("")
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    spec_path = resolve_spec(args.spec)
    top = infer_top(spec_path)

    agent_cmd = ["python", "agent.py", "--spec", str(spec_path), "--verify", "sim"]
    if args.overwrite:
        agent_cmd.append("--overwrite")
    agent_proc = run_command(agent_cmd)

    verify_cmd = ["python", "run_sim.py", "--mode", "sim", "--top", top]
    verify_proc = run_command(verify_cmd) if agent_proc.returncode == 0 else None

    log_sections = [
        ("Agent Command", " ".join(agent_cmd)),
        ("Agent Output", (agent_proc.stdout + ("\n" + agent_proc.stderr if agent_proc.stderr else "")).strip()),
    ]
    if verify_proc is not None:
        log_sections.extend(
            [
                ("Verification Command", " ".join(verify_cmd)),
                (
                    "Verification Output",
                    (verify_proc.stdout + ("\n" + verify_proc.stderr if verify_proc.stderr else "")).strip(),
                ),
            ]
        )
    log_path = write_log(top, log_sections)

    if agent_proc.stdout:
        print(agent_proc.stdout.rstrip())
    if agent_proc.stderr:
        print(agent_proc.stderr.rstrip(), file=sys.stderr)

    if agent_proc.returncode != 0:
        print(f"Pipeline failed during agent generation. Log: {log_path.relative_to(ROOT)}", file=sys.stderr)
        return agent_proc.returncode

    if verify_proc is not None:
        if verify_proc.stdout:
            print(verify_proc.stdout.rstrip())
        if verify_proc.stderr:
            print(verify_proc.stderr.rstrip(), file=sys.stderr)
        if verify_proc.returncode != 0:
            print(f"Pipeline failed during verification. Log: {log_path.relative_to(ROOT)}", file=sys.stderr)
            return verify_proc.returncode

    print(f"Pipeline succeeded. Log: {log_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
