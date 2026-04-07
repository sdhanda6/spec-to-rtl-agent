from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RTL_DIR = ROOT / "rtl"
TB_DIR = ROOT / "tb"
BUILD_DIR = ROOT / "build"
DEFAULT_TOP = "phase2_top"


@dataclass
class VerificationResult:
    mode: str
    succeeded: bool
    returncode: int
    command: str
    stdout: str
    stderr: str
    message: str
    attempt: int = 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile-check generated Verilog RTL or run RTL+testbench simulation"
    )
    parser.add_argument("--mode", choices=["compile", "sim"], default="compile")
    parser.add_argument("--top", default=DEFAULT_TOP)
    parser.add_argument("--rtl", type=Path, default=None)
    parser.add_argument("--tb", type=Path, default=None)
    return parser.parse_args()


def resolve_rtl_path(top: str, requested: Path | None) -> Path:
    if requested:
        return requested if requested.is_absolute() else ROOT / requested
    preferred = RTL_DIR / f"{top}.v"
    if preferred.exists():
        return preferred
    return RTL_DIR / f"{top}.sv"


def resolve_tb_path(top: str, requested: Path | None) -> Path:
    if requested:
        return requested if requested.is_absolute() else ROOT / requested
    return TB_DIR / f"tb_{top}.sv"


def ensure_iverilog_tools() -> tuple[str, str]:
    iverilog = shutil.which("iverilog")
    vvp = shutil.which("vvp")
    if not iverilog or not vvp:
        raise FileNotFoundError("iverilog/vvp not found in PATH")
    return iverilog, vvp


def verify_design(
    mode: str,
    rtl_path: Path,
    tb_path: Path | None,
    top_name: str,
    attempt: int = 1,
) -> VerificationResult:
    iverilog, vvp = ensure_iverilog_tools()
    if mode == "compile":
        return compile_with_iverilog(rtl_path, iverilog, attempt=attempt)
    if tb_path is None:
        return VerificationResult(
            mode=mode,
            succeeded=False,
            returncode=1,
            command="",
            stdout="",
            stderr="",
            message="Simulation requested without a testbench path",
            attempt=attempt,
        )
    return simulate_with_iverilog(rtl_path, tb_path, top_name, iverilog, vvp, attempt=attempt)


def compile_with_iverilog(rtl_path: Path, iverilog: str, attempt: int = 1) -> VerificationResult:
    if not rtl_path.exists():
        return VerificationResult(
            mode="compile",
            succeeded=False,
            returncode=1,
            command="",
            stdout="",
            stderr="",
            message=f"RTL file not found: {rtl_path}",
            attempt=attempt,
        )
    cmd = [iverilog, "-g2012", "-t", "null", str(rtl_path)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return VerificationResult(
        mode="compile",
        succeeded=proc.returncode == 0,
        returncode=proc.returncode,
        command=" ".join(cmd),
        stdout=proc.stdout,
        stderr=proc.stderr,
        message=(proc.stderr or proc.stdout).strip() or "compile ok",
        attempt=attempt,
    )


def simulate_with_iverilog(
    rtl_path: Path,
    tb_path: Path,
    top_name: str,
    iverilog: str,
    vvp: str,
    attempt: int = 1,
) -> VerificationResult:
    if not rtl_path.exists():
        return VerificationResult(
            mode="sim",
            succeeded=False,
            returncode=1,
            command="",
            stdout="",
            stderr="",
            message=f"RTL file not found: {rtl_path}",
            attempt=attempt,
        )
    if not tb_path.exists():
        return VerificationResult(
            mode="sim",
            succeeded=False,
            returncode=1,
            command="",
            stdout="",
            stderr="",
            message=f"Testbench file not found: {tb_path}",
            attempt=attempt,
        )

    BUILD_DIR.mkdir(exist_ok=True)
    out_path = BUILD_DIR / f"{top_name}_sim.out"
    compile_cmd = [iverilog, "-g2012", "-o", str(out_path), str(rtl_path), str(tb_path)]
    compile_proc = subprocess.run(compile_cmd, cwd=ROOT, capture_output=True, text=True)
    if compile_proc.returncode != 0:
        return VerificationResult(
            mode="sim",
            succeeded=False,
            returncode=compile_proc.returncode,
            command=" ".join(compile_cmd),
            stdout=compile_proc.stdout,
            stderr=compile_proc.stderr,
            message=(compile_proc.stderr or compile_proc.stdout).strip() or "compile for sim failed",
            attempt=attempt,
        )

    run_cmd = [vvp, str(out_path)]
    run_proc = subprocess.run(run_cmd, cwd=ROOT, capture_output=True, text=True)
    return VerificationResult(
        mode="sim",
        succeeded=run_proc.returncode == 0,
        returncode=run_proc.returncode,
        command=" ".join(run_cmd),
        stdout=run_proc.stdout,
        stderr=run_proc.stderr,
        message=(run_proc.stderr or run_proc.stdout).strip() or "simulation ok",
        attempt=attempt,
    )


def main() -> int:
    args = parse_args()
    rtl_path = resolve_rtl_path(args.top, args.rtl)
    tb_path = resolve_tb_path(args.top, args.tb)
    result = verify_design(args.mode, rtl_path, tb_path if args.mode == "sim" else None, args.top)
    print(result.message)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    return 0 if result.succeeded else 1


if __name__ == "__main__":
    sys.exit(main())
