from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from spec2rtl.collateral import CollateralBundle, generate_collateral
from spec2rtl.ir import ModuleIR


@dataclass
class FlowIssue:
    code: str
    message: str
    severity: str = "error"


@dataclass
class FlowRepairResult:
    repaired: bool
    actions: list[str] = field(default_factory=list)
    issues: list[FlowIssue] = field(default_factory=list)
    bundle: CollateralBundle | None = None


QOR_KNOB_REGISTRY: dict[str, list[dict[str, Any]]] = {
    "setup": [
        {
            "candidate_id": "setup_relax_clock_small",
            "why_this_candidate": "relax the clock slightly and add placement whitespace to reduce setup pressure",
            "metric_kind_it_targets": "setup",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.05, "reason": "reduce setup pressure"},
                {"knob": "CORE_AREA", "action": "scale_box", "value": 1.05, "reason": "give timing repair more room"},
            ],
        },
        {
            "candidate_id": "setup_lower_density",
            "why_this_candidate": "reduce placement density to ease setup closure",
            "metric_kind_it_targets": "setup",
            "knobs": [
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.60", "reason": "lower placement pressure for setup repair"},
                {"knob": "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT", "action": "set", "value": "1", "reason": "increase local spacing"},
            ],
        },
        {
            "candidate_id": "setup_relax_clock_and_spread",
            "why_this_candidate": "relax the clock and spread placement further to force a third setup exploration point",
            "metric_kind_it_targets": "setup",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.08, "reason": "reduce setup pressure with a larger margin"},
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.57", "reason": "spread cells more aggressively for setup repair"},
            ],
        },
    ],
    "timing": [
        {
            "candidate_id": "timing_relax_clock_small",
            "why_this_candidate": "relax the clock slightly and add a small amount of placement whitespace",
            "metric_kind_it_targets": "timing",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.05, "reason": "reduce setup pressure"},
                {"knob": "CORE_AREA", "action": "scale_box", "value": 1.05, "reason": "give placer/resizer more room"},
            ],
        },
        {
            "candidate_id": "timing_relax_clock_medium",
            "why_this_candidate": "relax timing more aggressively and bias placement density downward",
            "metric_kind_it_targets": "timing",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.10, "reason": "reduce setup pressure further"},
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.60", "reason": "lower placement pressure"},
            ],
        },
        {
            "candidate_id": "timing_spread_and_pad",
            "why_this_candidate": "expand floorplan and add cell padding for timing repair space",
            "metric_kind_it_targets": "timing",
            "knobs": [
                {"knob": "CORE_AREA", "action": "scale_box", "value": 1.10, "reason": "more whitespace for repair"},
                {"knob": "DIE_AREA", "action": "scale_box", "value": 1.08, "reason": "keep margins consistent"},
                {"knob": "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT", "action": "set", "value": "1", "reason": "reduce local crowding"},
            ],
        },
    ],
    "hold": [
        {
            "candidate_id": "hold_spread_cells",
            "why_this_candidate": "add spacing so hold fixing has more routing and buffering freedom",
            "metric_kind_it_targets": "hold",
            "knobs": [
                {"knob": "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT", "action": "set", "value": "1", "reason": "give hold fixing more local spacing"},
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.58", "reason": "reduce tight placement that can worsen short paths"},
            ],
        },
        {
            "candidate_id": "hold_expand_core",
            "why_this_candidate": "expand the core slightly to give detailed routing and resizing more hold-fix flexibility",
            "metric_kind_it_targets": "hold",
            "knobs": [
                {"knob": "CORE_AREA", "action": "scale_box", "value": 1.06, "reason": "increase whitespace for hold repair"},
                {"knob": "DIE_AREA", "action": "scale_box", "value": 1.04, "reason": "preserve margins while expanding the core"},
            ],
        },
        {
            "candidate_id": "hold_relax_density_and_clock",
            "why_this_candidate": "lower density and relax clock assumptions slightly to provide a third hold-fix candidate",
            "metric_kind_it_targets": "hold",
            "knobs": [
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.54", "reason": "give hold buffers and routing more room"},
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.03, "reason": "avoid over-tight optimization while exploring hold fixes"},
            ],
        },
    ],
    "logical_area": [
        {
            "candidate_id": "logical_area_map_area2",
            "why_this_candidate": "push synthesis to prefer smaller mapped area",
            "metric_kind_it_targets": "logical_area",
            "knobs": [
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "AREA 2", "reason": "area-biased synthesis strategy"},
                {"knob": "ABC_AREA", "action": "set", "value": "1", "reason": "prefer area-optimized mapping"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "avoid extra buffers when possible"},
            ],
        },
        {
            "candidate_id": "logical_area_share_resources",
            "why_this_candidate": "encourage sharing and reduce over-buffering",
            "metric_kind_it_targets": "logical_area",
            "knobs": [
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "AREA 1", "reason": "moderate area strategy"},
                {"knob": "MAX_FANOUT_CONSTRAINT", "action": "set", "value": "12", "reason": "avoid strict fanout-driven buffering"},
                {"knob": "SYNTH_SHARE_RESOURCES", "action": "set", "value": "1", "reason": "prefer shared logic"},
            ],
        },
        {
            "candidate_id": "logical_area_no_size_no_buffer",
            "why_this_candidate": "strip area growth from sizing and buffering heuristics",
            "metric_kind_it_targets": "logical_area",
            "knobs": [
                {"knob": "SYNTH_SIZING", "action": "set", "value": "0", "reason": "avoid upsizing for marginal gain"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "avoid inserted buffers"},
                {"knob": "MAX_FANOUT_CONSTRAINT", "action": "set", "value": "16", "reason": "allow fewer extra repeaters"},
            ],
        },
    ],
    "physical_area": [
        {
            "candidate_id": "physical_area_shrink_core",
            "why_this_candidate": "trim physical footprint with a tighter core",
            "metric_kind_it_targets": "physical_area",
            "knobs": [
                {"knob": "CORE_AREA", "action": "scale_box", "value": 0.92, "reason": "shrink core footprint"},
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.72", "reason": "push denser placement"},
            ],
        },
        {
            "candidate_id": "physical_area_shrink_die",
            "why_this_candidate": "shrink die and core together for a smaller layout footprint",
            "metric_kind_it_targets": "physical_area",
            "knobs": [
                {"knob": "DIE_AREA", "action": "scale_box", "value": 0.94, "reason": "reduce die footprint"},
                {"knob": "CORE_AREA", "action": "scale_box", "value": 0.95, "reason": "reduce core footprint"},
            ],
        },
        {
            "candidate_id": "physical_area_pack_cells",
            "why_this_candidate": "pack cells harder and remove padding",
            "metric_kind_it_targets": "physical_area",
            "knobs": [
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.78", "reason": "pack placement denser"},
                {"knob": "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT", "action": "set", "value": "0", "reason": "remove extra placement padding"},
            ],
        },
    ],
    "power": [
        {
            "candidate_id": "power_reduce_buffering",
            "why_this_candidate": "cut switching power by avoiding surplus buffering",
            "metric_kind_it_targets": "power",
            "knobs": [
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "reduce unnecessary buffer insertion"},
                {"knob": "MAX_FANOUT_CONSTRAINT", "action": "set", "value": "12", "reason": "avoid aggressive repeater insertion"},
            ],
        },
        {
            "candidate_id": "power_area_strategy",
            "why_this_candidate": "smaller mapped cells often lower total power on tiny designs",
            "metric_kind_it_targets": "power",
            "knobs": [
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "AREA 2", "reason": "prefer smaller mapped cells"},
                {"knob": "ABC_AREA", "action": "set", "value": "1", "reason": "bias mapping away from larger cells"},
            ],
        },
        {
            "candidate_id": "power_relax_clock",
            "why_this_candidate": "relax performance slightly to reduce dynamic activity pressure",
            "metric_kind_it_targets": "power",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.08, "reason": "reduce timing pressure"},
                {"knob": "SYNTH_SIZING", "action": "set", "value": "0", "reason": "avoid power-costly upsizing"},
            ],
        },
    ],
    "routability": [
        {
            "candidate_id": "routability_spread_core",
            "why_this_candidate": "expand the core to reduce local routing demand",
            "metric_kind_it_targets": "routability",
            "knobs": [
                {"knob": "CORE_AREA", "action": "scale_box", "value": 1.12, "reason": "reduce placement crowding"},
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.55", "reason": "lower routing pressure"},
            ],
        },
        {
            "candidate_id": "routability_expand_die",
            "why_this_candidate": "give the design more global routing resources",
            "metric_kind_it_targets": "routability",
            "knobs": [
                {"knob": "DIE_AREA", "action": "scale_box", "value": 1.10, "reason": "increase routing resource grid"},
                {"knob": "CORE_AREA", "action": "scale_box", "value": 1.08, "reason": "spread placement with the die"},
            ],
        },
        {
            "candidate_id": "routability_add_padding",
            "why_this_candidate": "increase placement spacing to reduce pin access and congestion issues",
            "metric_kind_it_targets": "routability",
            "knobs": [
                {"knob": "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT", "action": "set", "value": "1", "reason": "increase placement spacing"},
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.50", "reason": "further reduce congestion"},
            ],
        },
    ],
    "congestion": [
        {
            "candidate_id": "congestion_spread_core",
            "why_this_candidate": "expand the core and lower density to reduce congestion overflow",
            "metric_kind_it_targets": "congestion",
            "knobs": [
                {"knob": "CORE_AREA", "action": "scale_box", "value": 1.12, "reason": "reduce placement crowding"},
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.55", "reason": "lower congestion pressure"},
            ],
        },
        {
            "candidate_id": "congestion_add_padding",
            "why_this_candidate": "increase cell padding to improve pin access and reduce overflow hotspots",
            "metric_kind_it_targets": "congestion",
            "knobs": [
                {"knob": "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT", "action": "set", "value": "1", "reason": "increase cell spacing"},
                {"knob": "PLACE_DENSITY", "action": "set", "value": "0.50", "reason": "reduce routing demand"},
            ],
        },
        {
            "candidate_id": "congestion_expand_die_and_core",
            "why_this_candidate": "expand die and core together for a third congestion exploration point",
            "metric_kind_it_targets": "congestion",
            "knobs": [
                {"knob": "DIE_AREA", "action": "scale_box", "value": 1.10, "reason": "increase global routing resources"},
                {"knob": "CORE_AREA", "action": "scale_box", "value": 1.08, "reason": "spread placement to relieve overflow"},
            ],
        },
    ],
    "correctness": [
        {
            "candidate_id": "correctness_regenerate_collateral",
            "why_this_candidate": "regenerate downstream collateral so LVS compares refreshed netlists and flow inputs",
            "metric_kind_it_targets": "correctness",
            "knobs": [
                {"knob": "REGENERATE_COLLATERAL", "action": "set", "value": "1", "reason": "refresh flow collateral for LVS consistency"},
            ],
        },
        {
            "candidate_id": "correctness_refresh_verilog_reference",
            "why_this_candidate": "force the schematic reference netlist to be rebuilt from the current RTL",
            "metric_kind_it_targets": "correctness",
            "knobs": [
                {"knob": "REFRESH_SCHEMATIC_NETLIST", "action": "set", "value": "1", "reason": "rebuild schematic-side netlist collateral"},
            ],
        },
        {
            "candidate_id": "correctness_refresh_all_references",
            "why_this_candidate": "refresh both collateral and schematic references to force a third correctness candidate",
            "metric_kind_it_targets": "correctness",
            "knobs": [
                {"knob": "REGENERATE_COLLATERAL", "action": "set", "value": "1", "reason": "refresh downstream collateral"},
                {"knob": "REFRESH_SCHEMATIC_NETLIST", "action": "set", "value": "1", "reason": "refresh the schematic reference netlist"},
            ],
        },
    ],
}

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ML_HISTORY_PATH = REPO_ROOT / "build" / "ml_history.json"

ASIC_STAGE_REPAIR_CLASSIFICATIONS: dict[str, dict[str, str]] = {
    "coverage_analysis": {
        "classification": "coverage_issue",
        "metric_kind": "verification",
        "action_family_hint": "coverage",
    },
    "dft_insertion": {
        "classification": "dft_issue",
        "metric_kind": "testability",
        "action_family_hint": "dft",
    },
    "atpg_generation": {
        "classification": "atpg_issue",
        "metric_kind": "testability",
        "action_family_hint": "atpg",
    },
    "lec_check": {
        "classification": "lec_mismatch",
        "metric_kind": "correctness",
        "action_family_hint": "lec",
    },
}


def classify_asic_stage_issue(stage_name: str, result: dict[str, Any]) -> dict[str, Any]:
    status = str(result.get("status", "not_run"))
    mapping = ASIC_STAGE_REPAIR_CLASSIFICATIONS.get(stage_name, {})
    issue_class = mapping.get("classification", "flow_issue")
    reason = str(result.get("reason") or result.get("message") or f"{stage_name} status is {status}")

    if status == "pass":
        return {
            "primary_bottleneck": "none",
            "bottleneck_classification": "clean",
            "metric_kind": mapping.get("metric_kind", "unknown"),
            "metric_family_priority": 99,
            "metric_source_file": None,
            "reasons": [f"{stage_name} passed"],
            "action_family_hint": "none",
            "ordered_bottlenecks": [],
            "failure_kind": "none",
            "repairable": False,
        }
    if status == "not_run":
        return {
            "primary_bottleneck": "not_run",
            "bottleneck_classification": "not_run",
            "metric_kind": "unknown",
            "metric_family_priority": 99,
            "metric_source_file": None,
            "reasons": [reason],
            "action_family_hint": "none",
            "ordered_bottlenecks": [],
            "failure_kind": "not_run",
            "repairable": False,
        }
    if status == "not_supported":
        return {
            "primary_bottleneck": "tool_support",
            "bottleneck_classification": "not_supported",
            "metric_kind": "support",
            "metric_family_priority": 99,
            "metric_source_file": None,
            "reasons": [reason],
            "action_family_hint": "none",
            "ordered_bottlenecks": ["tool_support"],
            "failure_kind": "not_supported",
            "repairable": False,
        }

    return {
        "primary_bottleneck": issue_class,
        "bottleneck_classification": issue_class,
        "metric_kind": mapping.get("metric_kind", "unknown"),
        "metric_family_priority": 0 if issue_class == "lec_mismatch" else 3,
        "metric_source_file": _first_evidence_path(result),
        "reasons": [reason],
        "action_family_hint": mapping.get("action_family_hint", "none"),
        "ordered_bottlenecks": [issue_class],
        "failure_kind": issue_class,
        "repairable": issue_class in {"coverage_issue", "lec_mismatch"},
    }


def validate_collateral(bundle: CollateralBundle, expected_top: str) -> list[FlowIssue]:
    issues: list[FlowIssue] = []
    if not bundle.config_mk.exists():
        issues.append(FlowIssue(code="missing_config", message="config.mk was not generated"))
    if not bundle.constraint_sdc.exists():
        issues.append(FlowIssue(code="missing_sdc", message="constraint.sdc is missing"))
    if not bundle.filelist_f.exists():
        issues.append(FlowIssue(code="missing_filelist", message="filelist.f is missing"))
    else:
        entries = [line.strip() for line in bundle.filelist_f.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not entries:
            issues.append(FlowIssue(code="empty_filelist", message="filelist.f does not list any RTL sources"))
        for entry in entries:
            path = Path(entry)
            if not path.exists():
                issues.append(FlowIssue(code="missing_rtl_source", message=f"filelist entry does not exist: {entry}"))
    if bundle.config_mk.exists():
        config_text = bundle.config_mk.read_text(encoding="utf-8")
        if f"export DESIGN_NAME := {expected_top}" not in config_text:
            issues.append(FlowIssue(code="wrong_top", message=f"config.mk DESIGN_NAME does not match expected top {expected_top}"))
        if f"export TOP_MODULE := {expected_top}" not in config_text:
            issues.append(FlowIssue(code="missing_top_module_var", message=f"config.mk TOP_MODULE does not match expected top {expected_top}"))
        if "export VERILOG_FILES :=" not in config_text:
            issues.append(FlowIssue(code="missing_verilog_var", message="config.mk is missing VERILOG_FILES"))
        if "export SYNTH_HIERARCHICAL := 0" not in config_text:
            issues.append(FlowIssue(code="missing_flat_synth_directive", message="config.mk does not force flat synthesis"))
        if f"export SYNTH_ARGS := -top {expected_top}" not in config_text:
            issues.append(FlowIssue(code="missing_synth_top_arg", message=f"config.mk does not pass -top {expected_top} into synthesis"))
        if "export SYNTH_OPT_HIER := 1" not in config_text:
            issues.append(FlowIssue(code="missing_synth_opt_directive", message="config.mk does not enable synthesis hierarchy optimization"))
        if "export ABC_AREA := 1" not in config_text:
            issues.append(FlowIssue(code="missing_abc_mapping_directive", message="config.mk does not enable ABC area mapping"))
    return issues


def attempt_collateral_repair(
    root: Path,
    ir: ModuleIR,
    rtl_path: Path,
    tb_path: Path | None,
    bundle: CollateralBundle,
    issues: list[FlowIssue],
) -> FlowRepairResult:
    repairable_codes = {issue.code for issue in issues}
    supported = {
        "missing_sdc",
        "missing_rtl_source",
        "empty_filelist",
        "wrong_top",
        "missing_top_module_var",
        "missing_synth_top_arg",
        "missing_synth_opt_directive",
        "missing_flat_synth_directive",
        "missing_abc_mapping_directive",
        "missing_config",
        "missing_filelist",
    }
    if not repairable_codes.intersection(supported):
        return FlowRepairResult(repaired=False, issues=issues, bundle=bundle)

    regenerated = generate_collateral(root, ir, rtl_path, tb_path=tb_path, injected_fault=None)
    actions = [f"regenerated downstream collateral after detecting {issue.code}" for issue in issues]
    return FlowRepairResult(repaired=True, actions=actions, issues=issues, bundle=regenerated)


def analyze_openroad_failure(log_text: str) -> list[FlowIssue]:
    lowered = log_text.lower()
    issues: list[FlowIssue] = []
    if "no rule to make target" in lowered and "config" in lowered:
        issues.append(FlowIssue(code="missing_config", message="OpenROAD flow could not find the requested config.mk"))
    if "cannot open" in lowered and ".sdc" in lowered:
        issues.append(FlowIssue(code="missing_sdc", message="OpenROAD flow could not open the generated SDC file"))
    if "cannot open" in lowered and ".v" in lowered:
        issues.append(FlowIssue(code="missing_rtl_source", message="OpenROAD flow could not open one of the RTL sources"))
    if "design name" in lowered and "mismatch" in lowered:
        issues.append(FlowIssue(code="wrong_top", message="OpenROAD flow reported a design-name mismatch"))
    return issues


def suggest_qor_knobs(metrics: dict[str, object], bottlenecks: dict[str, object]) -> list[dict[str, object]]:
    candidates = generate_qor_candidates(metrics, bottlenecks, {"vars": {}})
    for candidate in candidates:
        if not candidate.get("rejected"):
            return list(candidate.get("knobs", []))
    return []


def suggest_signoff_repairs(results: dict, base_config: dict) -> list[dict]:
    del base_config
    primary = str(results.get("primary_bottleneck", results.get("bottleneck_classification", "unknown")))
    if primary == "drc":
        return [
            {"action_family": "routability", "knob": "CORE_AREA", "action": "scale_box", "value": 1.12, "reason": "DRC failure suggests more routing whitespace and looser placement", "metric_kind": "routability"},
            {"action_family": "routability", "knob": "PLACE_DENSITY", "action": "set", "value": "0.50", "reason": "DRC failure suggests reducing congestion pressure", "metric_kind": "routability"},
            {"action_family": "routability", "knob": "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT", "action": "set", "value": "1", "reason": "DRC failure suggests increasing placement spacing for routing access", "metric_kind": "routability"},
        ]
    if primary == "lvs":
        return [
            {"action_family": "correctness", "knob": "REGENERATE_COLLATERAL", "action": "set", "value": "1", "reason": "LVS failure suggests collateral/netlist refresh", "metric_kind": "correctness"},
            {"action_family": "correctness", "knob": "REFRESH_SCHEMATIC_NETLIST", "action": "set", "value": "1", "reason": "LVS failure suggests schematic reference regeneration", "metric_kind": "correctness"},
        ]
    return []


def classify_signoff_bottleneck(results: dict) -> dict:
    drc_status = str(results.get("drc_status", "not_run"))
    lvs_status = str(results.get("lvs_status", "not_run"))
    drc_count = int(results.get("drc_violation_count", 0) or 0)
    lvs_count = int(results.get("lvs_mismatch_count", 0) or 0)
    failure_kind = str(results.get("failure_kind", ""))
    notes = results.get("notes", []) if isinstance(results.get("notes"), list) else []
    reports = results.get("signoff_reports", {}) if isinstance(results.get("signoff_reports"), dict) else {}
    availability = results.get("signoff_tool_availability", {}) if isinstance(results.get("signoff_tool_availability"), dict) else {}

    if drc_status == "fail" and lvs_status == "fail":
        return {
            "primary_bottleneck": "drc",
            "bottleneck_classification": "mixed",
            "metric_kind": "routability",
            "metric_family_priority": 2,
            "metric_source_file": reports.get("drc_report_paths"),
            "reasons": [
                f"DRC failed with {drc_count} reported violations; route/placement repair should run first",
                f"LVS also failed with {lvs_count} reported mismatches; collateral/netlist repair should follow after DRC cleanup",
            ],
            "action_family_hint": "routability",
            "ordered_bottlenecks": ["drc", "lvs"],
            "failure_kind": "mixed",
        }
    if drc_status == "fail":
        return {
            "primary_bottleneck": "drc",
            "bottleneck_classification": "drc",
            "metric_kind": "routability",
            "metric_family_priority": 2,
            "metric_source_file": reports.get("drc_report_paths"),
            "reasons": [f"DRC failed with {drc_count} reported violations"],
            "action_family_hint": "routability",
            "ordered_bottlenecks": ["drc"],
            "failure_kind": failure_kind or "drc / routability / placement",
        }
    if lvs_status == "fail":
        return {
            "primary_bottleneck": "lvs",
            "bottleneck_classification": "lvs",
            "metric_kind": "correctness",
            "metric_family_priority": 0,
            "metric_source_file": reports.get("lvs_report_paths"),
            "reasons": [f"LVS failed with {lvs_count} reported mismatches"],
            "action_family_hint": "correctness",
            "ordered_bottlenecks": ["lvs"],
            "failure_kind": failure_kind or "lvs / netlist-correctness / collateral",
        }
    if drc_status in {"unsupported", "partial"} or lvs_status in {"unsupported", "partial"}:
        unavailable = []
        if not availability.get("magic_usable", availability.get("magic", False)):
            unavailable.append("magic")
        if not availability.get("netgen_usable", availability.get("netgen", False)):
            unavailable.append("netgen")
        return {
            "primary_bottleneck": "signoff_support",
            "bottleneck_classification": "unsupported",
            "metric_kind": "unknown",
            "metric_family_priority": 99,
            "metric_source_file": None,
            "reasons": [f"signoff partially supported: {', '.join(unavailable) if unavailable else 'collateral incomplete'}"] + [str(item) for item in notes],
            "action_family_hint": "none",
            "ordered_bottlenecks": unavailable,
            "failure_kind": "unsupported",
        }
    return {
        "primary_bottleneck": "unknown",
        "bottleneck_classification": "unknown",
        "metric_kind": "unknown",
        "metric_family_priority": 99,
        "metric_source_file": None,
        "reasons": ["No actionable signoff bottleneck detected."],
        "action_family_hint": "none",
        "ordered_bottlenecks": [],
        "failure_kind": failure_kind or "clean",
    }


def apply_signoff_strategy(base_config: dict[str, object], suggestions: list[dict[str, object]]) -> dict[str, object]:
    updated = apply_qor_strategy(base_config, suggestions)
    chosen_family = str(updated.get("chosen_action_family", "none"))
    for suggestion in suggestions:
        family = str(suggestion.get("action_family") or suggestion.get("family") or "none")
        if family != "none":
            updated["chosen_action_family"] = family
            updated["action_family_matches_bottleneck"] = family == chosen_family or chosen_family == "none" or family == str(updated.get("chosen_action_family"))
            break
    return updated


def classify_post_synth_mismatch(results: dict) -> dict:
    mismatch_kind = str(results.get("mismatch_kind", results.get("primary_mismatch", "unsupported")))
    primary = str(results.get("primary_mismatch", mismatch_kind))
    ordered = [str(item) for item in results.get("ordered_mismatches", [])] if isinstance(results.get("ordered_mismatches"), list) else []
    reasons = [str(item) for item in results.get("reasons", [])] if isinstance(results.get("reasons"), list) else []
    evidence = results.get("evidence_paths", [])
    source = evidence[0] if isinstance(evidence, list) and evidence else None
    family = "none"
    artifact = results.get("artifact_to_regenerate")
    repairable = bool(results.get("repairable", True))

    if mismatch_kind == "mixed":
        ordered = ordered or ["rtl_behavior_mismatch", "uninitialized_or_reset_issue", "wrapper/testbench_mismatch", "synthesis_netlist_mismatch"]
        if "rtl_behavior_mismatch" in ordered:
            primary = "rtl_behavior_mismatch"
            family = "rtl"
            artifact = artifact or "rtl"
        elif "uninitialized_or_reset_issue" in ordered:
            primary = "uninitialized_or_reset_issue"
            family = "reset_init"
            artifact = artifact or "post_synth_testbench"
        elif "wrapper/testbench_mismatch" in ordered:
            primary = "wrapper/testbench_mismatch"
            family = "wrapper_testbench"
            artifact = artifact or "post_synth_testbench"
        else:
            primary = "synthesis_netlist_mismatch"
            family = "synthesis"
            artifact = artifact or "collateral"
    elif mismatch_kind in {"wrapper/testbench_mismatch"}:
        family = "wrapper_testbench"
        artifact = artifact or "post_synth_testbench"
    elif mismatch_kind in {"uninitialized_or_reset_issue", "combinational_vs_sequential_issue"}:
        family = "reset_init" if mismatch_kind == "uninitialized_or_reset_issue" else "wrapper_testbench"
        artifact = artifact or "post_synth_testbench"
    elif mismatch_kind in {"synthesis_netlist_mismatch"}:
        family = "synthesis"
        artifact = artifact or "collateral"
    elif mismatch_kind == "rtl_behavior_mismatch":
        family = "rtl"
        artifact = artifact or "rtl"
    elif mismatch_kind == "unsupported":
        family = "none"
        repairable = False
    return {
        "primary_bottleneck": primary,
        "bottleneck_classification": mismatch_kind,
        "primary_mismatch": primary,
        "ordered_mismatches": ordered or ([primary] if primary else []),
        "metric_kind": "correctness" if family in {"wrapper_testbench", "reset_init", "synthesis"} else "unknown",
        "metric_family_priority": 0 if family != "none" else 99,
        "metric_source_file": source,
        "reasons": reasons or ["post-synthesis behavior mismatch detected"],
        "action_family_hint": family,
        "ordered_bottlenecks": ordered or ([primary] if primary else []),
        "failure_kind": mismatch_kind,
        "repairable": repairable,
        "artifact_to_regenerate": artifact,
    }


def suggest_post_synth_repairs(results: dict, base_config: dict) -> list[dict]:
    del base_config
    kind = str(results.get("primary_mismatch", results.get("bottleneck_classification", results.get("primary_bottleneck", "unsupported"))))
    if kind == "rtl_behavior_mismatch":
        return [
            {
                "action_family": "rtl",
                "repair_kind": "rtl_regeneration",
                "artifact_to_regenerate": "rtl",
                "knob": "REGENERATE_RTL",
                "action": "set",
                "value": "1",
                "reason": "rerun RTL generation because the reference behavior is unstable",
                "metric_kind": "unknown",
            },
        ]
    if kind == "wrapper/testbench_mismatch":
        return [
            {
                "action_family": "wrapper_testbench",
                "repair_kind": "post_synth_testbench_adaptation",
                "artifact_to_regenerate": "post_synth_testbench",
                "verification_mode": "strip_internal_state_checks",
                "knob": "REFRESH_POST_SYNTH_WRAPPER",
                "action": "set",
                "value": "1",
                "reason": "remove RTL-only internal-state checks from the synthesized-design harness",
                "metric_kind": "correctness",
            },
        ]
    if kind == "uninitialized_or_reset_issue":
        return [
            {
                "action_family": "reset_init",
                "repair_kind": "post_synth_reset_adaptation",
                "artifact_to_regenerate": "post_synth_testbench",
                "verification_mode": "gate_reset_settle",
                "knob": "RELAX_POST_SYNTH_RESET_CHECKS",
                "action": "set",
                "value": "1",
                "reason": "delay reset/output observation for gate-level initialization and async-reset settling",
                "metric_kind": "correctness",
            },
        ]
    if kind == "combinational_vs_sequential_issue":
        return [
            {
                "action_family": "wrapper_testbench",
                "repair_kind": "post_synth_sequential_adaptation",
                "artifact_to_regenerate": "post_synth_testbench",
                "verification_mode": "sequential_settle",
                "knob": "RELAX_POST_SYNTH_SEQ_CHECKS",
                "action": "set",
                "value": "1",
                "reason": "add a small post-clock observation delay for synthesized sequential logic",
                "metric_kind": "correctness",
            },
        ]
    if kind == "synthesis_netlist_mismatch":
        return [
            {
                "action_family": "synthesis",
                "repair_kind": "collateral_regeneration",
                "artifact_to_regenerate": "collateral",
                "knob": "REGENERATE_COLLATERAL",
                "action": "set",
                "value": "1",
                "reason": "refresh synthesized collateral and netlist inputs",
                "metric_kind": "correctness",
            },
        ]
    if kind == "mixed":
        ordered = [str(item) for item in results.get("ordered_mismatches", [])] if isinstance(results.get("ordered_mismatches"), list) else []
        for item in ordered:
            suggestion = suggest_post_synth_repairs({"primary_mismatch": item}, {})
            if suggestion:
                return suggestion
    return []


def apply_post_synth_strategy(base_config: dict[str, object], suggestions: list[dict[str, object]]) -> dict[str, object]:
    updated = dict(base_config)
    notes = list(updated.get("notes", [])) if isinstance(updated.get("notes"), list) else []
    history = list(updated.get("applied_suggestions", [])) if isinstance(updated.get("applied_suggestions"), list) else []
    modes = list(updated.get("verification_modes", [])) if isinstance(updated.get("verification_modes"), list) else []
    artifacts = list(updated.get("artifacts_to_regenerate", [])) if isinstance(updated.get("artifacts_to_regenerate"), list) else []
    chosen = "none"
    last_repair: dict[str, object] | None = None
    for suggestion in suggestions:
        history.append(dict(suggestion))
        if suggestion.get("reason"):
            notes.append(str(suggestion.get("reason")))
        family = str(suggestion.get("action_family", "none"))
        if chosen == "none" and family != "none":
            chosen = family
        mode = str(suggestion.get("verification_mode", "")).strip()
        if mode and mode not in modes:
            modes.append(mode)
        artifact = str(suggestion.get("artifact_to_regenerate", "")).strip()
        if artifact and artifact not in artifacts:
            artifacts.append(artifact)
        if last_repair is None:
            last_repair = {
                "repair_kind": suggestion.get("repair_kind"),
                "artifact_to_regenerate": suggestion.get("artifact_to_regenerate"),
                "verification_mode": suggestion.get("verification_mode"),
                "reason": suggestion.get("reason"),
            }
    updated["applied_suggestions"] = history
    updated["notes"] = notes
    updated["chosen_action_family"] = chosen
    updated["verification_modes"] = modes
    updated["artifacts_to_regenerate"] = artifacts
    updated["last_repair"] = last_repair
    updated["regenerate_collateral"] = any(str(item.get("artifact_to_regenerate")) == "collateral" for item in suggestions)
    updated["regenerate_rtl"] = any(str(item.get("artifact_to_regenerate")) == "rtl" for item in suggestions)
    updated["action_family_matches_bottleneck"] = chosen in {"wrapper_testbench", "reset_init", "synthesis", "rtl", "none"}
    return updated


def _first_evidence_path(result: dict[str, Any]) -> str | None:
    evidence = result.get("evidence_paths", [])
    if isinstance(evidence, list) and evidence:
        return str(evidence[0])
    log_path = result.get("log_path")
    return str(log_path) if log_path else None


def generate_qor_candidates(metrics: dict[str, object], bottlenecks: dict[str, object], base_config: dict[str, object]) -> list[dict[str, object]]:
    del base_config
    primary = str(bottlenecks.get("metric_kind", "unknown"))
    ordered = bottlenecks.get("ordered_bottlenecks", [])
    family_order = _family_search_order(primary, ordered)
    candidates: list[dict[str, object]] = []
    logical_area_floorplan_knobs = {"CORE_AREA", "DIE_AREA", "CLOCK_PERIOD", "PLACE_DENSITY", "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT"}
    area_only_knobs = {
        "SYNTH_STRATEGY",
        "ABC_AREA",
        "SYNTH_BUFFERING",
        "MAX_FANOUT_CONSTRAINT",
        "SYNTH_SHARE_RESOURCES",
        "SYNTH_SIZING",
    }

    for rank, family in enumerate(family_order, start=1):
        for template in QOR_KNOB_REGISTRY.get(family, []):
            knobs = [dict(item) for item in template.get("knobs", [])]
            mismatch = family != primary and primary not in {"mixed", "unknown"}
            rejected = False
            reject_reason = None
            if primary == "logical_area" and knobs and {item["knob"] for item in knobs}.issubset(logical_area_floorplan_knobs):
                rejected = True
                reject_reason = "logical_area bottleneck cannot be handled by only floorplan/timing knobs"
            elif primary in {"setup", "timing", "hold"} and knobs and {item["knob"] for item in knobs}.issubset(area_only_knobs):
                rejected = True
                reject_reason = "timing bottlenecks cannot be handled by only area-optimization synthesis knobs"
            candidates.append(
                {
                    "family": family,
                    "candidate_id": str(template["candidate_id"]),
                    "family_priority_rank": rank,
                    "metric_kind_it_targets": template["metric_kind_it_targets"],
                    "why_this_candidate": template["why_this_candidate"],
                    "knobs": knobs,
                    "mismatch": mismatch,
                    "rejected": rejected,
                    "reject_reason": reject_reason,
                    "action_family_matched_bottleneck": not mismatch and not rejected,
                }
            )
    return candidates


def apply_qor_strategy(base_config: dict[str, object], suggestions: list[dict[str, object]]) -> dict[str, object]:
    vars_in = base_config.get("vars", {})
    vars_out = dict(vars_in) if isinstance(vars_in, dict) else {}
    history = list(base_config.get("applied_suggestions", [])) if isinstance(base_config.get("applied_suggestions"), list) else []
    notes = list(base_config.get("notes", [])) if isinstance(base_config.get("notes"), list) else []
    chosen_action_family = base_config.get("chosen_action_family", "none")
    action_family_matches_bottleneck = bool(base_config.get("action_family_matches_bottleneck", True))

    for suggestion in suggestions:
        family = str(suggestion.get("action_family") or suggestion.get("family") or "none")
        knob = str(suggestion.get("knob", ""))
        action = str(suggestion.get("action", ""))
        value = suggestion.get("value")
        reason = str(suggestion.get("reason", ""))
        metric_kind = str(suggestion.get("metric_kind", "unknown"))
        if chosen_action_family == "none" and family != "none":
            chosen_action_family = family
        if metric_kind == "logical_area" and knob in {"CORE_AREA", "DIE_AREA", "CLOCK_PERIOD", "PLACE_DENSITY"} and family != "logical_area":
            action_family_matches_bottleneck = False
            notes.append("logical_area bottleneck received non-synthesis dominant knobs")
        if reason:
            notes.append(reason)
        _apply_single_knob(vars_out, knob, action, value)
        history.append(dict(suggestion))

    updated = dict(base_config)
    updated["vars"] = vars_out
    updated["applied_suggestions"] = history
    updated["notes"] = notes
    updated["chosen_action_family"] = chosen_action_family
    updated["action_family_matches_bottleneck"] = action_family_matches_bottleneck
    return updated


def load_ml_history(history_path: Path | None = None) -> list[dict[str, Any]]:
    path = history_path or DEFAULT_ML_HISTORY_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def update_ml_history(attempt: dict, history_path: Path | None = None) -> None:
    path = history_path or DEFAULT_ML_HISTORY_PATH
    history = load_ml_history(path)
    history.append(dict(attempt))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history[-1000:], indent=2, sort_keys=True), encoding="utf-8")


def featurize_attempt(metrics: dict, bottleneck: dict, candidate: dict) -> dict:
    timing = metrics.get("timing", {}) if isinstance(metrics.get("timing"), dict) else {}
    area = metrics.get("area", {}) if isinstance(metrics.get("area"), dict) else {}
    power = metrics.get("power", {}) if isinstance(metrics.get("power"), dict) else {}
    routability = metrics.get("routability", {}) if isinstance(metrics.get("routability"), dict) else {}
    metadata = metrics.get("metadata", {}) if isinstance(metrics.get("metadata"), dict) else {}
    knob_names = _candidate_knob_names(candidate)
    return {
        "spec_name": candidate.get("spec_name"),
        "design_kind": candidate.get("design_kind"),
        "design_name": metadata.get("design_name"),
        "metric_kind": str(bottleneck.get("metric_kind", "unknown")),
        "bottleneck_classification": str(bottleneck.get("bottleneck_classification", bottleneck.get("primary_bottleneck", "unknown"))),
        "primary_bottleneck": str(bottleneck.get("primary_bottleneck", bottleneck.get("metric_kind", "unknown"))),
        "ordered_bottlenecks": [str(item) for item in bottleneck.get("ordered_bottlenecks", [])] if isinstance(bottleneck.get("ordered_bottlenecks"), list) else [],
        "candidate_family": str(candidate.get("family", "none")),
        "candidate_id": str(candidate.get("candidate_id", "")),
        "candidate_knobs": knob_names,
        "knob_signature": "|".join(knob_names),
        "timing_pressure": max(0.0, -_float_or_zero(timing.get("wns_ns"))) + max(0.0, -_float_or_zero(timing.get("tns_ns")) / 10.0),
        "setup_violations": _float_or_zero(timing.get("setup_violation_count")),
        "hold_violations": _float_or_zero(timing.get("hold_violation_count")),
        "logical_area_um2": _float_or_zero(area.get("logical_um2")),
        "physical_area_um2": _float_or_zero(area.get("physical_um2")),
        "power_mw": _float_or_zero(power.get("mw")),
        "congestion": _float_or_zero(routability.get("congestion")),
        "utilization": _float_or_zero(routability.get("utilization")),
        "clock_period_ns": _float_or_zero(metadata.get("clock_period_ns")),
    }


def predict_candidate_score(features: dict, history: list[dict]) -> float:
    if not history:
        return 0.0

    weighted_total = 0.0
    weight_sum = 0.0
    family_samples = 0
    exact_samples = 0
    family = str(features.get("candidate_family", "none"))
    metric_kind = str(features.get("metric_kind", "unknown"))
    bottleneck = str(features.get("bottleneck_classification", "unknown"))
    knob_names = set(features.get("candidate_knobs", []))

    for past in history:
        past_family = str(past.get("candidate_family", past.get("chosen_action_family", "none")))
        if past_family != family:
            continue
        family_samples += 1
        weight = 1.0
        if str(past.get("metric_kind", "unknown")) == metric_kind:
            weight += 2.0
        if str(past.get("bottleneck_classification", "unknown")) == bottleneck:
            weight += 1.5
            exact_samples += 1
        if features.get("design_kind") and past.get("design_kind") == features.get("design_kind"):
            weight += 1.0
        if features.get("spec_name") and past.get("spec_name") == features.get("spec_name"):
            weight += 0.5
        past_knobs = set(str(item) for item in past.get("candidate_knobs", []) if item)
        if knob_names and past_knobs:
            weight += len(knob_names & past_knobs) / max(len(knob_names | past_knobs), 1)

        outcome = 0.0
        outcome += _float_or_zero(past.get("improvement_amount"))
        outcome += _float_or_zero(past.get("score_delta")) * 0.2
        if past.get("beat_baseline"):
            outcome += 2.0
        if past.get("targets_met"):
            outcome += 3.0
        signoff = past.get("signoff_metrics", past.get("signoff", {}))
        if isinstance(signoff, dict):
            if str(signoff.get("drc_status", "pass")) == "fail":
                outcome -= 2.0
            if str(signoff.get("lvs_status", "pass")) == "fail":
                outcome -= 2.0
        if past.get("post_synth_pass") is False or past.get("behavior_match") is False:
            outcome -= 1.5

        weighted_total += outcome * weight
        weight_sum += weight

    if weight_sum == 0.0:
        return 0.0

    exploration_bonus = 1.5 / math.sqrt(family_samples + 1.0)
    exact_bonus = 0.5 if exact_samples == 0 else 0.0
    return (weighted_total / weight_sum) + exploration_bonus + exact_bonus


def rank_qor_candidates(
    candidates: list[dict],
    history: list[dict],
    metrics: dict | None = None,
    bottlenecks: dict | None = None,
    context: dict | None = None,
) -> list[dict]:
    metrics = metrics or {}
    bottlenecks = bottlenecks or {}
    context = context or {}
    if not history:
        ranked = sorted(
            [dict(candidate) for candidate in candidates],
            key=lambda item: (bool(item.get("rejected")), int(item.get("family_priority_rank", 999)), bool(item.get("mismatch", False))),
        )
        for index, candidate in enumerate(ranked, start=1):
            candidate["ml_predicted_score"] = 0.0
            candidate["ml_ranking_reason"] = "rule-based fallback because no ML history exists yet"
            candidate["ml_rank"] = index
        return ranked

    ranked: list[dict[str, Any]] = []
    for candidate in candidates:
        enriched = dict(candidate)
        enriched.update({key: value for key, value in context.items() if key not in enriched})
        features = featurize_attempt(metrics, bottlenecks, enriched)
        predicted = predict_candidate_score(features, history)
        enriched["ml_features"] = features
        enriched["ml_predicted_score"] = predicted
        enriched["ml_ranking_reason"] = _candidate_reason(features, history, predicted)
        ranked.append(enriched)

    ranked.sort(
        key=lambda item: (
            bool(item.get("rejected")),
            -float(item.get("ml_predicted_score", 0.0)),
            int(item.get("family_priority_rank", 999)),
            bool(item.get("mismatch", False)),
        )
    )
    for index, candidate in enumerate(ranked, start=1):
        candidate["ml_rank"] = index
    return ranked


def _family_search_order(primary: str, ordered: object) -> list[str]:
    if primary == "mixed" and isinstance(ordered, list) and ordered:
        base = [str(item) for item in ordered]
    elif primary in QOR_KNOB_REGISTRY:
        base = [primary]
    else:
        base = []
    for family in ["correctness", "setup", "timing", "hold", "congestion", "routability", "logical_area", "physical_area", "power"]:
        if family not in base:
            base.append(family)
    return base


def _apply_single_knob(vars_out: dict[str, str], knob: str, action: str, value: Any) -> None:
    if knob == "CLOCK_PERIOD" and action == "scale":
        current = _parse_float(vars_out.get("CLOCK_PERIOD"))
        if current is not None and isinstance(value, (int, float)):
            vars_out["CLOCK_PERIOD"] = _format_float(current * float(value))
        return
    if knob in {"CORE_AREA", "DIE_AREA"} and action == "scale_box":
        current_box = _parse_box(vars_out.get(knob))
        if current_box is not None and isinstance(value, (int, float)):
            vars_out[knob] = _format_box(_scale_box(current_box, float(value)))
        return
    if knob and action == "set":
        vars_out[knob] = str(value)


def _candidate_reason(features: dict[str, Any], history: list[dict[str, Any]], predicted: float) -> str:
    family = str(features.get("candidate_family", "none"))
    metric_kind = str(features.get("metric_kind", "unknown"))
    related = [item for item in history if str(item.get("candidate_family", item.get("chosen_action_family", "none"))) == family]
    exact = [
        item
        for item in related
        if str(item.get("metric_kind", "unknown")) == metric_kind
        and str(item.get("bottleneck_classification", "unknown")) == str(features.get("bottleneck_classification", "unknown"))
    ]
    if exact:
        wins = sum(1 for item in exact if item.get("beat_baseline"))
        return f"learned from {len(exact)} similar attempts for {metric_kind}; {wins} beat baseline; predicted score {predicted:.2f}"
    if related:
        wins = sum(1 for item in related if item.get("beat_baseline"))
        return f"learned from {len(related)} prior {family} attempts; {wins} beat baseline; predicted score {predicted:.2f}"
    return f"exploration bonus for unseen {family} family; predicted score {predicted:.2f}"


def _candidate_knob_names(candidate: dict[str, Any]) -> list[str]:
    knobs = candidate.get("knobs", [])
    if not isinstance(knobs, list):
        return []
    names = [str(item.get("knob")) for item in knobs if isinstance(item, dict) and item.get("knob")]
    return sorted(dict.fromkeys(names))


def _float_or_zero(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _parse_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def _format_float(value: float) -> str:
    text = f"{value:.4f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def _parse_box(value: object) -> tuple[float, float, float, float] | None:
    if value is None:
        return None
    parts = [part for part in str(value).split() if part]
    if len(parts) != 4:
        return None
    try:
        return tuple(float(part) for part in parts)  # type: ignore[return-value]
    except ValueError:
        return None


def _scale_box(box: tuple[float, float, float, float], scale: float) -> tuple[float, float, float, float]:
    x0, y0, x1, y1 = box
    width = max(1.0, (x1 - x0) * scale)
    height = max(1.0, (y1 - y0) * scale)
    return x0, y0, x0 + width, y0 + height


def _format_box(box: tuple[float, float, float, float]) -> str:
    return " ".join(_format_float(value) for value in box)
