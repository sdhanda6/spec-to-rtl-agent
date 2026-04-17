from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from spec2rtl.collateral import CollateralBundle


@dataclass
class OpenROADEnvironment:
    openroad_bin: str | None
    yosys_bin: str | None
    flow_root: Path | None
    make_c_dir: Path | None
    make_bin: str | None
    messages: list[str] = field(default_factory=list)


@dataclass
class OpenROADRunResult:
    requested_mode: str
    attempted: bool
    succeeded: bool
    status: str
    command: str | None
    log_path: Path | None
    stdout: str
    stderr: str
    message: str
    artifacts: list[Path] = field(default_factory=list)


def detect_openroad_environment(root: Path) -> OpenROADEnvironment:
    openroad_bin = shutil.which("openroad")
    yosys_bin = shutil.which("yosys")
    make_bin = shutil.which("make")
    flow_root = _detect_flow_root(root)
    make_c_dir = _flow_make_dir(flow_root) if flow_root else None
    messages: list[str] = []
    if not openroad_bin:
        messages.append("openroad not found in PATH")
    if not yosys_bin:
        messages.append("yosys not found in PATH")
    if not flow_root or not make_c_dir:
        messages.append("OpenROAD-flow-scripts root not found; set OPENROAD_FLOW_ROOT or OPENROAD_FLOW_DIR")
    if not make_bin:
        messages.append("make not found in PATH")
    return OpenROADEnvironment(
        openroad_bin=openroad_bin,
        yosys_bin=yosys_bin,
        flow_root=flow_root,
        make_c_dir=make_c_dir,
        make_bin=make_bin,
        messages=messages,
    )


def run_openroad_flow(
    root: Path,
    bundle: CollateralBundle,
    env: OpenROADEnvironment,
    mode: str,
    attempt: int = 1,
) -> OpenROADRunResult:
    log_dir = root / "build" / "flow" / bundle.top / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"openroad_{mode}_attempt_{attempt}.log"

    if not env.flow_root or not env.make_c_dir or not env.make_bin:
        return OpenROADRunResult(
            requested_mode=mode,
            attempted=False,
            succeeded=False,
            status="missing_tool",
            command=None,
            log_path=None,
            stdout="",
            stderr="",
            message="; ".join(env.messages) if env.messages else "OpenROAD environment is unavailable",
            artifacts=[],
        )

    target = "synth" if mode == "synth" else "finish"
    command = [
        env.make_bin,
        "-C",
        env.make_c_dir.as_posix(),
        f"DESIGN_CONFIG={bundle.config_mk.as_posix()}",
        target,
    ]
    proc = subprocess.run(command, capture_output=True, text=True)
    combined = (proc.stdout + ("\n" + proc.stderr if proc.stderr else "")).strip()
    log_path.write_text(combined + ("\n" if combined else ""), encoding="utf-8")
    artifacts = _collect_flow_outputs(env.make_c_dir, bundle.top)
    return OpenROADRunResult(
        requested_mode=mode,
        attempted=True,
        succeeded=proc.returncode == 0,
        status="pass" if proc.returncode == 0 else "fail",
        command=" ".join(command),
        log_path=log_path,
        stdout=proc.stdout,
        stderr=proc.stderr,
        message=combined or ("OpenROAD flow passed" if proc.returncode == 0 else "OpenROAD flow failed"),
        artifacts=artifacts,
    )


def _detect_flow_root(root: Path) -> Path | None:
    for env_name in ["OPENROAD_FLOW_ROOT", "OPENROAD_FLOW_DIR"]:
        value = os.environ.get(env_name)
        if value:
            path = Path(value)
            normalized = _normalize_flow_root(path)
            if normalized:
                return normalized
    candidates = [
        root / "OpenROAD-flow-scripts",
        root / "openroad-flow-scripts",
        root / "flow",
    ]
    for path in candidates:
        normalized = _normalize_flow_root(path)
        if normalized:
            return normalized
    return None


def _normalize_flow_root(path: Path) -> Path | None:
    resolved = path.expanduser()
    if not resolved.exists():
        return None
    if resolved.name == "flow" and (resolved / "Makefile").exists():
        parent = resolved.parent
        return parent if (parent / "flow").exists() else resolved
    if (resolved / "flow" / "Makefile").exists():
        return resolved
    return None


def _flow_make_dir(flow_root: Path | None) -> Path | None:
    if flow_root is None:
        return None
    if flow_root.name == "flow" and (flow_root / "Makefile").exists():
        return flow_root
    candidate = flow_root / "flow"
    if (candidate / "Makefile").exists():
        return candidate
    return None


def _collect_flow_outputs(flow_dir: Path, top: str) -> list[Path]:
    collected: list[Path] = []
    for folder_name in ["reports", "results", "logs"]:
        folder = flow_dir / folder_name
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if path.is_file() and top.lower() in path.as_posix().lower():
                collected.append(path)
    return collected
