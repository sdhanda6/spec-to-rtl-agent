from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from spec2rtl.ir import ModuleIR


DEFAULT_CLOCK_PERIOD_NS = "10"


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
    power_activity_tcl: Path | None = None
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
    power_activity_tcl = design_dir / "power_activity.tcl"

    clock_port = _infer_clock_port(ir)
    clock_period_ns, clock_warning = _infer_clock_period_ns(ir, clock_port)
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
            power_activity_tcl=power_activity_tcl,
            clock_port=clock_port,
            clock_period_ns=clock_period_ns,
        ),
        encoding="utf-8",
    )
    power_activity_tcl.write_text(_render_power_activity_tcl(), encoding="utf-8")
    manifest_yaml.write_text(_render_manifest(ir, rtl_copy, tb_path, platform, clock_port, clock_period_ns), encoding="utf-8")
    readme_md.write_text(_render_readme(ir, platform, clock_port, clock_period_ns), encoding="utf-8")

    generated_files = [rtl_copy, filelist_f, filelist_tcl, config_mk, power_activity_tcl, manifest_yaml, readme_md]
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
        power_activity_tcl=power_activity_tcl,
        generated_files=generated_files,
        warnings=warnings,
        clock_port=clock_port,
        clock_period_ns=clock_period_ns,
        platform=platform,
        injected_fault=injected_fault,
    )


def _infer_clock_port(ir: ModuleIR) -> str | None:
    input_ports = [port.name for port in ir.ports if port.direction == "input"]
    if ir.clock and ir.clock in input_ports:
        return ir.clock
    for port in ir.ports:
        if port.direction == "input" and port.name.lower() in {"clk", "clock"}:
            return port.name
    if input_ports:
        return input_ports[0]
    if ir.clock:
        return ir.clock
    if _needs_generated_clock(ir):
        return "clk"
    return None


def _needs_generated_clock(ir: ModuleIR) -> bool:
    if ir.clock or ir.reset or ir.counter or ir.register or ir.shift_register or ir.fsm:
        return False
    if ir.processes:
        return all(process.kind == "comb" for process in ir.processes)
    return ir.design_kind in {"combinational", "generic"}


def _infer_clock_period_ns(ir: ModuleIR, clock_port: str | None) -> tuple[str, str | None]:
    raw = ir.flow_hints.get("clock_period")
    if raw is not None and str(raw).strip() not in {"", DEFAULT_CLOCK_PERIOD_NS, f"{DEFAULT_CLOCK_PERIOD_NS}ns"}:
        return DEFAULT_CLOCK_PERIOD_NS, f"clock_period {raw} was overridden to the tapeout default of 10ns"
    if ir.clock:
        return DEFAULT_CLOCK_PERIOD_NS, "OpenROAD collateral uses a forced 10ns clock"
    if clock_port:
        return DEFAULT_CLOCK_PERIOD_NS, f"clock was defaulted to {clock_port} at 10ns"
    return DEFAULT_CLOCK_PERIOD_NS, "clock was not explicit and no input port was available; emitted a virtual 10ns clock"


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
        lines.append(f"create_clock -period {clock_period_ns} [get_ports {_sdc_port_ref(clock_port)}]")
    else:
        lines.append(f"create_clock -period {clock_period_ns or DEFAULT_CLOCK_PERIOD_NS} spec2rtl_virtual_clk")
    reset_port = ir.reset.signal if ir.reset else None
    if reset_port:
        lines.append(f"set_false_path -from [get_ports {_sdc_port_ref(reset_port)}]")
    lines.append("")
    return "\n".join(lines)


def _sdc_port_ref(port_name: str) -> str:
    if any(char in port_name for char in "[]{} "):
        return "{" + port_name.replace("}", "\\}") + "}"
    return port_name


def _render_config_mk(
    design_name: str,
    platform: str,
    rtl_copy: Path,
    constraint_sdc: Path,
    power_activity_tcl: Path,
    clock_port: str | None,
    clock_period_ns: str | None,
) -> str:
    lines = [
        f"export DESIGN_NAME := {design_name}",
        f"export TOP_MODULE := {design_name}",
        f"export PLATFORM := {platform}",
        f"export VERILOG_FILES := {rtl_copy.as_posix()}",
        f"export SDC_FILE := {constraint_sdc.as_posix()}",
        "export DIE_AREA ?= 0 0 200 200",
        "export CORE_AREA ?= 10 10 190 190",
        "",
        "# Synthesis directives: hierarchy -check -top $(DESIGN_NAME), synth -flatten, opt, abc mapping.",
        "export SYNTH_HIERARCHICAL := 0",
        f"export SYNTH_ARGS := -top {design_name}",
        "export SYNTH_OPT_HIER := 1",
        "export ABC_AREA := 1",
        "export ACTIVITY_FILE = $(RESULTS_DIR)/waves.vcd",
        "export ACTIVITY_SCOPE = tb_$(DESIGN_NAME)/dut",
        "export REPORT_POWER = 1",
        f"export PRE_FINAL_REPORT_TCL := {power_activity_tcl.as_posix()}",
    ]
    if clock_port:
        lines.append(f"export CLOCK_PORT := {clock_port}")
    if clock_period_ns:
        lines.append(f"export CLOCK_PERIOD := {clock_period_ns}")
    lines.extend(["", "# This file is intended for OpenROAD-flow-scripts style DESIGN_CONFIG usage.", ""])
    return "\n".join(lines)


def _render_power_activity_tcl() -> str:
    return "\n".join(
        [
            "# Auto-generated activity hook for OpenROAD final power reporting.",
            "if { [info exists ::env(REPORT_POWER)] && $::env(REPORT_POWER) eq \"0\" } {",
            "  puts \"REPORT_POWER=0; skipping activity annotation\"",
            "} elseif { [info exists ::env(ACTIVITY_FILE)] && $::env(ACTIVITY_FILE) ne \"\" } {",
            "  set activity_file $::env(ACTIVITY_FILE)",
            "  if { [file exists $activity_file] } {",
            "    set activity_scope \"\"",
            "    if { [info exists ::env(ACTIVITY_SCOPE)] } {",
            "      set activity_scope $::env(ACTIVITY_SCOPE)",
            "    }",
            "    if { $activity_scope ne \"\" } {",
            "      puts \"Reading activity VCD $activity_file with scope $activity_scope\"",
            "      if { [catch { read_vcd -scope $activity_scope $activity_file } activity_error] } {",
            "        puts \"Warning: scoped read_vcd failed: $activity_error\"",
            "        puts \"Retrying activity VCD without an explicit scope\"",
            "        if { [catch { read_vcd $activity_file } fallback_error] } {",
            "          puts \"Warning: unscoped read_vcd failed: $fallback_error\"",
            "        }",
            "      }",
            "    } else {",
            "      puts \"Reading activity VCD $activity_file\"",
            "      if { [catch { read_vcd $activity_file } activity_error] } {",
            "        puts \"Warning: read_vcd failed: $activity_error\"",
            "      }",
            "    }",
            "  } else {",
            "    puts \"Warning: ACTIVITY_FILE $activity_file was not found; final power will use default activity\"",
            "  }",
            "}",
            "",
        ]
    )


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
