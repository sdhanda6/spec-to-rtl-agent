from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from spec2rtl.ir import ModuleIR


@dataclass
class CollateralBundle:
    top: str
    root_dir: Path
    design_dir: Path
    src_dir: Path
    rtl_copy: Path
    filelist_f: Path
    filelist_tcl: Path
    config_mk: Path
    constraint_sdc: Path
    manifest_yaml: Path
    readme_md: Path
    generated_files: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    clock_port: str | None = None
    clock_period_ns: str | None = None
    platform: str = "sky130hd"
    injected_fault: str | None = None


def generate_collateral(
    root: Path,
    ir: ModuleIR,
    rtl_path: Path,
    tb_path: Path | None = None,
    injected_fault: str | None = None,
) -> CollateralBundle:
    top = ir.name
    root_dir = root / "build" / "flow" / top
    design_dir = root_dir / "design"
    src_dir = design_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    rtl_copy = src_dir / rtl_path.name
    shutil.copyfile(rtl_path, rtl_copy)

    filelist_f = design_dir / "filelist.f"
    filelist_tcl = design_dir / "filelist.tcl"
    constraint_sdc = design_dir / "constraint.sdc"
    config_mk = design_dir / "config.mk"
    manifest_yaml = design_dir / "design_manifest.yaml"
    readme_md = design_dir / "README.md"

    clock_port = _infer_clock_port(ir)
    clock_period_ns, clock_warning = _infer_clock_period_ns(ir)
    platform = _infer_platform(ir)
    warnings = [clock_warning] if clock_warning else []

    bad_rtl_ref = injected_fault == "bad_filelist"
    missing_sdc = injected_fault == "missing_sdc"
    wrong_top = injected_fault == "wrong_top"

    filelist_target = src_dir / ("missing_top.v" if bad_rtl_ref else rtl_path.name)
    filelist_f.write_text(f"{filelist_target.as_posix()}\n", encoding="utf-8")
    filelist_tcl.write_text(
        "\n".join(
            [
                "set rtl_files [list \\",
                f"    {filelist_target.as_posix()} \\",
                "]",
                "",
            ]
        ),
        encoding="utf-8",
    )

    if not missing_sdc:
        constraint_sdc.write_text(_render_sdc(ir, clock_port, clock_period_ns), encoding="utf-8")
    elif constraint_sdc.exists():
        constraint_sdc.unlink()

    design_name = f"{top}_broken" if wrong_top else top
    config_mk.write_text(
        _render_config_mk(
            design_name=design_name,
            platform=platform,
            rtl_copy=rtl_copy,
            constraint_sdc=constraint_sdc,
            clock_port=clock_port,
            clock_period_ns=clock_period_ns,
        ),
        encoding="utf-8",
    )
    manifest_yaml.write_text(_render_manifest(ir, rtl_copy, tb_path, platform, clock_port, clock_period_ns), encoding="utf-8")
    readme_md.write_text(_render_readme(ir, platform, clock_port, clock_period_ns), encoding="utf-8")

    generated_files = [rtl_copy, filelist_f, filelist_tcl, config_mk, manifest_yaml, readme_md]
    if constraint_sdc.exists():
        generated_files.append(constraint_sdc)
    return CollateralBundle(
        top=top,
        root_dir=root_dir,
        design_dir=design_dir,
        src_dir=src_dir,
        rtl_copy=rtl_copy,
        filelist_f=filelist_f,
        filelist_tcl=filelist_tcl,
        config_mk=config_mk,
        constraint_sdc=constraint_sdc,
        manifest_yaml=manifest_yaml,
        readme_md=readme_md,
        generated_files=generated_files,
        warnings=warnings,
        clock_port=clock_port,
        clock_period_ns=clock_period_ns,
        platform=platform,
        injected_fault=injected_fault,
    )


def _infer_clock_port(ir: ModuleIR) -> str | None:
    if ir.clock:
        return ir.clock
    for port in ir.ports:
        if port.direction == "input" and port.name.lower() in {"clk", "clock"}:
            return port.name
    return None


def _infer_clock_period_ns(ir: ModuleIR) -> tuple[str | None, str | None]:
    raw = ir.flow_hints.get("clock_period")
    if raw is None:
        if _infer_clock_port(ir):
            return "10.0", "clock_period was not explicit; defaulted OpenROAD collateral to 10.0ns"
        return None, None
    text = str(raw).strip().lower()
    if text.endswith("ns"):
        return text[:-2], None
    return text, None


def _infer_platform(ir: ModuleIR) -> str:
    explicit = ir.flow_hints.get("platform")
    if explicit:
        return str(explicit)
    tech_node = str(ir.flow_hints.get("tech_node", "")).lower()
    if "130" in tech_node or "sky" in tech_node:
        return "sky130hd"
    if "45" in tech_node:
        return "nangate45"
    return "sky130hd"


def _render_sdc(ir: ModuleIR, clock_port: str | None, clock_period_ns: str | None) -> str:
    lines = ["# Auto-generated timing constraints"]
    if clock_port and clock_period_ns:
        lines.append(f"create_clock [get_ports {clock_port}] -name {clock_port} -period {clock_period_ns}")
    else:
        lines.append("# No clock was inferred; add clock constraints manually if the design is sequential.")
    reset_port = ir.reset.signal if ir.reset else None
    if reset_port:
        lines.append(f"set_false_path -from [get_ports {reset_port}]")
    lines.append("")
    return "\n".join(lines)


def _render_config_mk(
    design_name: str,
    platform: str,
    rtl_copy: Path,
    constraint_sdc: Path,
    clock_port: str | None,
    clock_period_ns: str | None,
) -> str:
    lines = [
        f"export DESIGN_NAME := {design_name}",
        f"export PLATFORM := {platform}",
        f"export VERILOG_FILES := {rtl_copy.as_posix()}",
        f"export SDC_FILE := {constraint_sdc.as_posix()}",
        "export DIE_AREA ?= 0 0 200 200",
        "export CORE_AREA ?= 10 10 190 190",
    ]
    if clock_port:
        lines.append(f"export CLOCK_PORT := {clock_port}")
    if clock_period_ns:
        lines.append(f"export CLOCK_PERIOD := {clock_period_ns}")
    lines.extend(["", "# This file is intended for OpenROAD-flow-scripts style DESIGN_CONFIG usage.", ""])
    return "\n".join(lines)


def _render_manifest(
    ir: ModuleIR,
    rtl_copy: Path,
    tb_path: Path | None,
    platform: str,
    clock_port: str | None,
    clock_period_ns: str | None,
) -> str:
    lines = [
        f"top: {ir.name}",
        f"design_kind: {ir.design_kind}",
        f"platform: {platform}",
        f"rtl: {rtl_copy.as_posix()}",
        f"testbench: {tb_path.as_posix() if tb_path else 'null'}",
        f"clock_port: {clock_port if clock_port else 'null'}",
        f"clock_period_ns: {clock_period_ns if clock_period_ns else 'null'}",
        "ports:",
    ]
    for port in ir.ports:
        lines.extend(
            [
                "  -",
                f"    name: {port.name}",
                f"    dir: {port.direction}",
                f"    width: {port.width}",
            ]
        )
    return "\n".join(lines) + "\n"


def _render_readme(ir: ModuleIR, platform: str, clock_port: str | None, clock_period_ns: str | None) -> str:
    lines = [
        f"# {ir.name} Spec-to-Tapeout Collateral",
        "",
        "Generated files:",
        "- `config.mk`: OpenROAD-flow-scripts style design config",
        "- `constraint.sdc`: timing constraints",
        "- `filelist.f` and `filelist.tcl`: RTL source lists",
        "- `design_manifest.yaml`: machine-readable artifact summary",
        "",
        "Suggested usage:",
        "```powershell",
        f"python run_pipeline.py --spec <spec> --mode full --overwrite",
        "```",
        "",
        "If OpenROAD-flow-scripts is installed separately, point `OPENROAD_FLOW_ROOT` or `OPENROAD_FLOW_DIR` to it and run:",
        "```powershell",
        f"make DESIGN_CONFIG={Path('build') / 'flow' / ir.name / 'design' / 'config.mk'}",
        "```",
        "",
        f"Platform hint: `{platform}`",
        f"Clock port: `{clock_port}`" if clock_port else "Clock port: not inferred",
        f"Clock period: `{clock_period_ns} ns`" if clock_period_ns else "Clock period: not inferred",
        "",
        "Visible and hidden-case note: unsupported or ambiguous physical-design requirements should be treated as partial support, not tapeout-ready success.",
        "",
    ]
    return "\n".join(lines)
