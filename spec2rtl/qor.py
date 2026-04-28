from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from spec2rtl.flow_repair import classify_signoff_bottleneck as _classify_signoff_bottleneck


FAMILY_PRIORITY = {
    "correctness": 0,
    "timing": 1,
    "setup": 1,
    "hold": 2,
    "routability": 3,
    "congestion": 3,
    "logical_area": 4,
    "physical_area": 5,
    "power": 6,
    "unknown": 99,
}


def parse_finish_report(path: Path) -> dict:
    text = _safe_read(path)
    power_w = _search_float(text, r"^Total\s+\S+\s+\S+\s+\S+\s+([0-9.eE+-]+)\s+\d+\.\d+%", flags=re.MULTILINE)
    metrics = _empty_metrics()
    metrics["timing"]["wns_ns"] = _search_float(text, r"\bwns\s+max\s+([-+]?(?:\d+\.?\d*|\.\d+|inf))")
    metrics["timing"]["tns_ns"] = _search_float(text, r"\btns\s+max\s+([-+]?(?:\d+\.?\d*|\.\d+|inf))")
    metrics["timing"]["setup_violation_count"] = _search_int(text, r"setup violation count\s+(\d+)")
    metrics["timing"]["hold_violation_count"] = _search_int(text, r"hold violation count\s+(\d+)")
    metrics["timing"]["source"] = path.as_posix()
    metrics["area"]["physical_um2"] = _search_first_float(
        text,
        [
            r"\b(?:design|instance|instances)\s+area\s*:?\s*([0-9.eE+-]+)\s*(?:um\^2|um2)?",
            r"\bstd\s*cell\s+area\s*:?\s*([0-9.eE+-]+)\s*(?:um\^2|um2)?",
        ],
    )
    if metrics["area"]["physical_um2"] is not None:
        metrics["area"]["source"] = {"physical_um2": path.as_posix()}
    metrics["power"]["mw"] = None if power_w is None else power_w * 1000.0
    metrics["power"]["source"] = path.as_posix() if power_w is not None else None
    metrics["raw_reports"] = [path.as_posix()]
    return _finalize_metrics(metrics)


def parse_synth_stats(path: Path) -> dict:
    text = _safe_read(path)
    metrics = _empty_metrics()
    metrics["area"]["logical_um2"] = _search_float(text, r"Chip area for module .*?:\s*([0-9.eE+-]+)")
    metrics["area"]["cell_count"] = _search_int(text, r"^\s*(\d+)\s+[0-9.\-]+\s+\d+\s+[0-9.\-]+\s+cells\b", flags=re.MULTILINE)
    metrics["area"]["source"] = {
        "logical_um2": path.as_posix(),
        "cell_count": path.as_posix(),
    }
    metrics["raw_reports"] = [path.as_posix()]
    return _finalize_metrics(metrics)


def extract_qor_metrics(flow_root: Path, platform: str, design_name: str) -> dict:
    flow_dir = _normalize_flow_dir(flow_root)
    report_dir = flow_dir / "reports" / platform / design_name / "base"
    result_dir = flow_dir / "results" / platform / design_name / "base"
    log_dir = flow_dir / "logs" / platform / design_name / "base"

    metrics = _empty_metrics()
    metrics["metadata"]["platform"] = platform
    metrics["metadata"]["design_name"] = design_name

    discovered = {
        "finish_report": report_dir / "6_finish.rpt",
        "synth_stats": report_dir / "synth_stat.txt",
        "qor_summary": _first_existing(
            [
                report_dir / "qor_summary.rpt",
                report_dir / "qor_summary.txt",
                report_dir / "qor_summary.json",
                report_dir / "metrics.json",
            ]
        ),
        "floorplan_report": report_dir / "2_floorplan_final.rpt",
        "route_report": report_dir / "5_global_route.rpt",
        "finish_json": log_dir / "6_report.json",
        "grt_log": log_dir / "5_1_grt.log",
        "clock_period": result_dir / "clock_period.txt",
        "congestion_report": report_dir / "congestion.rpt",
    }
    metrics["metadata"]["report_paths"] = {key: path.as_posix() for key, path in discovered.items() if path is not None and path.exists()}
    metrics["metadata"]["missing_reports"] = [
        key for key, path in discovered.items() if path is not None and not path.exists()
    ]

    parsers = [
        (discovered["finish_report"], parse_finish_report),
        (discovered["synth_stats"], parse_synth_stats),
        (discovered["qor_summary"], _parse_qor_summary),
        (discovered["finish_json"], _parse_finish_json),
        (discovered["floorplan_report"], _parse_floorplan_report),
        (discovered["route_report"], _parse_route_report),
        (discovered["grt_log"], _parse_grt_log),
        (discovered["congestion_report"], _parse_congestion_report),
    ]
    for path, parser in parsers:
        if path is not None and path.exists():
            _merge_metrics(metrics, parser(path))

    if discovered["clock_period"].exists():
        metrics["metadata"]["clock_period_ns"] = _search_float(
            discovered["clock_period"].read_text(encoding="utf-8", errors="ignore"),
            r"([-+]?[0-9]*\.?[0-9]+)",
        )

    return _finalize_metrics(metrics)


def extract_synth_metrics(flow_root: Path, platform: str, design_name: str) -> dict:
    flow_dir = _normalize_flow_dir(flow_root)
    report_dir = flow_dir / "reports" / platform / design_name / "base"
    result_dir = flow_dir / "results" / platform / design_name / "base"
    log_dir = flow_dir / "logs" / platform / design_name / "base"

    metrics = _empty_metrics()
    metrics["metadata"]["platform"] = platform
    metrics["metadata"]["design_name"] = design_name
    discovered = {
        "synth_stats": report_dir / "synth_stat.txt",
        "synth_json": log_dir / "1_synth.json",
        "clock_period": result_dir / "clock_period.txt",
    }
    metrics["metadata"]["report_paths"] = {key: path.as_posix() for key, path in discovered.items() if path.exists()}
    metrics["metadata"]["missing_reports"] = [key for key, path in discovered.items() if not path.exists()]

    if discovered["synth_stats"].exists():
        _merge_metrics(metrics, parse_synth_stats(discovered["synth_stats"]))
    if discovered["synth_json"].exists():
        _merge_metrics(metrics, _parse_synth_json(discovered["synth_json"]))
    if discovered["clock_period"].exists():
        metrics["metadata"]["clock_period_ns"] = _search_float(
            discovered["clock_period"].read_text(encoding="utf-8", errors="ignore"),
            r"([-+]?[0-9]*\.?[0-9]+)",
        )
    return _finalize_metrics(metrics)


def classify_qor_bottleneck(metrics: dict) -> dict:
    targets = metrics.get("targets", {}) if isinstance(metrics.get("targets"), dict) else {}
    candidates: list[dict[str, Any]] = []

    wns = _metric(metrics, "wns_ns")
    tns = _metric(metrics, "tns_ns")
    setup_violations = _metric(metrics, "setup_violation_count")
    hold_violations = _metric(metrics, "hold_violation_count")
    wns_target = _target(targets, "wns", 0.0)
    tns_target = _target(targets, "tns", 0.0)
    setup_target = _target(targets, "setup_violations", 0.0)
    hold_target = _target(targets, "hold_violations", 0.0)
    if setup_violations is not None and setup_violations > setup_target:
        candidates.append(
            _classification(
                family="setup",
                reasons=[
                    f"setup violations={int(setup_violations)} exceed target {int(setup_target)}",
                    f"WNS={wns}ns below target {wns_target}ns" if wns is not None and wns < wns_target else None,
                    f"TNS={tns}ns below target {tns_target}ns" if tns is not None and tns < tns_target else None,
                ],
                source=metrics.get("timing", {}).get("source"),
                action_family="timing",
            )
        )
    elif (wns is not None and wns < wns_target) or (tns is not None and tns < tns_target):
        candidates.append(
            _classification(
                family="timing",
                reasons=[
                    f"WNS={wns}ns below target {wns_target}ns" if wns is not None and wns < wns_target else None,
                    f"TNS={tns}ns below target {tns_target}ns" if tns is not None and tns < tns_target else None,
                ],
                source=metrics.get("timing", {}).get("source"),
                action_family="timing",
            )
        )

    if hold_violations is not None and hold_violations > hold_target:
        candidates.append(
            _classification(
                family="hold",
                reasons=[f"hold violations={int(hold_violations)} exceed target {int(hold_target)}"],
                source=metrics.get("timing", {}).get("source"),
                action_family="hold",
            )
        )

    congestion = _metric(metrics, "congestion")
    utilization = _metric(metrics, "utilization")
    routability_target = _target(targets, "congestion", _target(targets, "routability", None))
    if (
        (routability_target is not None and congestion is not None and congestion > routability_target)
        or (congestion is not None and congestion > 0.0)
        or (utilization is not None and utilization > 0.80)
    ):
        candidates.append(
            _classification(
                family="congestion",
                reasons=[
                    f"congestion={congestion} exceeds target {routability_target}" if routability_target is not None and congestion is not None and congestion > routability_target else None,
                    f"congestion overflow={congestion}" if congestion is not None and congestion > 0.0 else None,
                    f"utilization={utilization:.3f}" if utilization is not None and utilization > 0.80 else None,
                ],
                source=_pick_source(metrics.get("routability", {}).get("source"), "congestion", "utilization"),
                action_family="routability",
            )
        )

    logical_area = _metric(metrics, "logical_area_um2")
    logical_area_target = _target(targets, "logical_area", None)
    if logical_area is not None and logical_area_target is not None and logical_area > logical_area_target:
        candidates.append(
            _classification(
                family="logical_area",
                reasons=[f"logical area {logical_area}um^2 exceeds target {logical_area_target}um^2"],
                source=_pick_source(metrics.get("area", {}).get("source"), "logical_um2"),
            )
        )

    power_mw = _metric(metrics, "power_mw")
    power_target = _target(targets, "power", None)
    if power_mw is not None and power_target is not None and power_mw > power_target:
        candidates.append(
            _classification(
                family="power",
                reasons=[f"power {power_mw}mW exceeds target {power_target}mW"],
                source=metrics.get("power", {}).get("source"),
            )
        )

    physical_area = _metric(metrics, "physical_area_um2")
    physical_area_target = _target(targets, "physical_area", None)
    if physical_area is not None and physical_area_target is not None and physical_area > physical_area_target:
        candidates.append(
            _classification(
                family="physical_area",
                reasons=[f"physical area {physical_area}um^2 exceeds target {physical_area_target}um^2"],
                source=_pick_source(metrics.get("area", {}).get("source"), "physical_um2"),
            )
        )

    if not candidates:
        return _classification("unknown", ["No target miss or dominant QoR hotspot detected."], None)

    ordered = sorted(candidates, key=lambda item: item["metric_family_priority"])
    primary = dict(ordered[0])
    primary["ordered_bottlenecks"] = [item["metric_kind"] for item in ordered]
    if len(ordered) > 1:
        primary["primary_bottleneck"] = "mixed"
        primary["bottleneck_classification"] = "mixed"
        primary["reasons"] = [reason for item in ordered for reason in item["reasons"]]
    return primary


def classify_synth_bottleneck(metrics: dict) -> dict:
    targets = metrics.get("targets", {}) if isinstance(metrics.get("targets"), dict) else {}
    candidates: list[dict[str, Any]] = []
    logical_area = _metric(metrics, "logical_area_um2")
    logical_area_target = _target(targets, "logical_area", _target(targets, "area", None))
    cell_count = _metric(metrics, "cell_count")
    cell_count_target = _target(targets, "cell_count", None)
    power_mw = _metric(metrics, "power_mw")
    power_target = _target(targets, "power", None)
    wns = _metric(metrics, "wns_ns")
    timing_target = _target(targets, "wns", None)

    if logical_area is not None and logical_area_target is not None and logical_area > logical_area_target:
        candidates.append(
            _classification(
                family="logical_area",
                reasons=[f"logical area {logical_area}um^2 exceeds target {logical_area_target}um^2"],
                source=_pick_source(metrics.get("area", {}).get("source"), "logical_um2"),
                action_family="area",
            )
        )
    if cell_count is not None and cell_count_target is not None and cell_count > cell_count_target:
        candidates.append(
            _classification(
                family="logical_area",
                reasons=[f"cell count {int(cell_count)} exceeds target {int(cell_count_target)}"],
                source=_pick_source(metrics.get("area", {}).get("source"), "cell_count"),
                action_family="area",
            )
        )
    if power_mw is not None and power_target is not None and power_mw > power_target:
        candidates.append(
            _classification(
                family="power",
                reasons=[f"power {power_mw}mW exceeds target {power_target}mW"],
                source=metrics.get("power", {}).get("source"),
                action_family="power",
            )
        )
    if wns is not None and timing_target is not None and wns < timing_target:
        candidates.append(
            _classification(
                family="timing",
                reasons=[f"WNS={wns}ns below target {timing_target}ns"],
                source=metrics.get("timing", {}).get("source"),
                action_family="timing",
            )
        )
    if not candidates:
        fallbacks: list[dict[str, Any]] = []
        if logical_area is not None:
            fallbacks.append(
                _classification(
                    family="logical_area",
                    reasons=[f"defaulting to logical area optimization with logical area {logical_area}um^2"],
                    source=_pick_source(metrics.get("area", {}).get("source"), "logical_um2"),
                    action_family="area",
                )
            )
        if cell_count is not None:
            fallbacks.append(
                _classification(
                    family="logical_area",
                    reasons=[f"defaulting to logical area optimization with cell count {int(cell_count)}"],
                    source=_pick_source(metrics.get("area", {}).get("source"), "cell_count"),
                    action_family="area",
                )
            )
        if power_mw is not None:
            fallbacks.append(
                _classification(
                    family="power",
                    reasons=[f"defaulting to power optimization with estimated power {power_mw}mW"],
                    source=metrics.get("power", {}).get("source"),
                    action_family="power",
                )
            )
        if not fallbacks:
            return _classification("unknown", ["No dominant synthesis bottleneck detected."], None)
        candidates = fallbacks
    ordered = sorted(candidates, key=lambda item: item["metric_family_priority"])
    primary = dict(ordered[0])
    primary["ordered_bottlenecks"] = [item["metric_kind"] for item in ordered]
    if len(ordered) > 1:
        primary["primary_bottleneck"] = "mixed"
        primary["bottleneck_classification"] = "mixed"
        primary["reasons"] = [reason for item in ordered for reason in item["reasons"]]
    return primary


def classify_signoff_bottleneck(results: dict) -> dict:
    return _classify_signoff_bottleneck(results)


def merge_signoff_with_qor(qor_metrics: dict, signoff_results: dict) -> dict:
    merged = dict(qor_metrics)
    signoff = dict(signoff_results) if isinstance(signoff_results, dict) else {}
    drc_status = str(signoff.get("drc_status", "not_run"))
    lvs_status = str(signoff.get("lvs_status", "not_run"))
    drc_count = int(signoff.get("drc_violation_count", 0) or 0)
    lvs_count = int(signoff.get("lvs_mismatch_count", 0) or 0)
    adjustment = 0.0
    reasons: list[str] = []
    if drc_status == "fail":
        penalty = 30.0 + min(40.0, float(drc_count))
        adjustment -= penalty
        reasons.append(f"signoff penalty {penalty:.2f} for DRC failures")
    elif drc_status in {"unsupported", "partial"}:
        adjustment -= 5.0
        reasons.append("signoff penalty 5.00 because DRC is unsupported or partial")
    if lvs_status == "fail":
        penalty = 40.0 + min(40.0, float(lvs_count) * 2.0)
        adjustment -= penalty
        reasons.append(f"signoff penalty {penalty:.2f} for LVS failures")
    elif lvs_status in {"unsupported", "partial"}:
        adjustment -= 5.0
        reasons.append("signoff penalty 5.00 because LVS is unsupported or partial")
    merged["signoff"] = signoff
    merged["signoff_failure_kind"] = signoff.get("failure_kind")
    merged["signoff_score_adjustment"] = adjustment
    merged["signoff_score_reasons"] = reasons
    return merged


def score_qor(metrics: dict, targets: dict) -> tuple[float, list[str]]:
    reasons: list[str] = []
    score = 0.0

    wns = _metric(metrics, "wns_ns")
    tns = _metric(metrics, "tns_ns")
    setup_violations = _metric(metrics, "setup_violation_count")
    hold_violations = _metric(metrics, "hold_violation_count")
    logical_area = _metric(metrics, "logical_area_um2")
    physical_area = _metric(metrics, "physical_area_um2")
    power_mw = _metric(metrics, "power_mw")
    congestion = _metric(metrics, "congestion")
    utilization = _metric(metrics, "utilization")

    if wns is not None:
        score += max(-40.0, min(40.0, wns * 8.0))
        reasons.append(f"WNS contribution {max(-40.0, min(40.0, wns * 8.0)):.2f}")
    if tns is not None:
        contribution = max(-25.0, min(10.0, tns * 0.5))
        score += contribution
        reasons.append(f"TNS contribution {contribution:.2f}")
    if setup_violations is not None:
        contribution = -min(35.0, float(setup_violations) * 6.0)
        score += contribution
        reasons.append(f"setup violation contribution {contribution:.2f}")
    if hold_violations is not None:
        contribution = -min(30.0, float(hold_violations) * 6.0)
        score += contribution
        reasons.append(f"hold violation contribution {contribution:.2f}")
    if logical_area is not None:
        contribution = -min(30.0, logical_area * 0.35)
        score += contribution
        reasons.append(f"logical area contribution {contribution:.2f}")
    if physical_area is not None:
        contribution = -min(20.0, physical_area * 0.005)
        score += contribution
        reasons.append(f"physical area contribution {contribution:.2f}")
    if power_mw is not None:
        contribution = -min(15.0, power_mw * 10.0)
        score += contribution
        reasons.append(f"power contribution {contribution:.2f}")
    if congestion is not None:
        penalty = -min(20.0, congestion * 5.0)
        score += penalty
        reasons.append(f"routability contribution {penalty:.2f}")
    if utilization is not None and utilization > 0.75:
        penalty = -min(10.0, (utilization - 0.75) * 100.0)
        score += penalty
        reasons.append(f"utilization penalty {penalty:.2f}")

    score += _target_penalty(wns, _target(targets, "wns", None), True, 8.0, "WNS", reasons)
    score += _target_penalty(tns, _target(targets, "tns", None), True, 2.0, "TNS", reasons)
    score += _target_penalty(setup_violations, _target(targets, "setup_violations", None), False, 10.0, "setup violations", reasons)
    score += _target_penalty(hold_violations, _target(targets, "hold_violations", None), False, 10.0, "hold violations", reasons)
    score += _target_penalty(logical_area, _target(targets, "logical_area", None), False, 3.0, "logical area", reasons)
    score += _target_penalty(physical_area, _target(targets, "physical_area", None), False, 1.0, "physical area", reasons)
    score += _target_penalty(power_mw, _target(targets, "power", None), False, 10.0, "power", reasons)
    score += _target_penalty(congestion, _target(targets, "congestion", _target(targets, "routability", None)), False, 10.0, "congestion", reasons)

    return score, reasons


def score_synth(metrics: dict, targets: dict, behavior_match: bool = True) -> tuple[float, list[str]]:
    reasons: list[str] = []
    if not behavior_match:
        return -1_000_000.0, ["behavior mismatch rejects this synthesized netlist"]

    score = 0.0
    logical_area = _metric(metrics, "logical_area_um2")
    cell_count = _metric(metrics, "cell_count")
    power_mw = _metric(metrics, "power_mw")
    wns = _metric(metrics, "wns_ns")
    tns = _metric(metrics, "tns_ns")

    if logical_area is not None:
        contribution = -min(120.0, math.log10(max(float(logical_area), 1.0)) * 45.0)
        score += contribution
        reasons.append(f"logical area contribution {contribution:.2f}")
    if cell_count is not None:
        contribution = -min(80.0, math.log10(max(float(cell_count), 1.0)) * 30.0)
        score += contribution
        reasons.append(f"cell count contribution {contribution:.2f}")
    if power_mw is not None:
        contribution = -min(35.0, math.log10(max(float(power_mw), 0.001) * 1000.0) * 8.0)
        score += contribution
        reasons.append(f"power contribution {contribution:.2f}")
    if wns is not None:
        contribution = max(-45.0, min(35.0, wns * 12.0))
        score += contribution
        reasons.append(f"WNS contribution {contribution:.2f}")
    if tns is not None:
        contribution = max(-30.0, min(12.0, tns * 0.75))
        score += contribution
        reasons.append(f"TNS contribution {contribution:.2f}")

    score += _target_penalty(logical_area, _target(targets, "logical_area", _target(targets, "area", None)), False, 10.0, "logical area", reasons)
    score += _target_penalty(cell_count, _target(targets, "cell_count", None), False, 6.0, "cell count", reasons)
    score += _target_penalty(power_mw, _target(targets, "power", None), False, 14.0, "power", reasons)
    score += _target_penalty(wns, _target(targets, "wns", None), True, 14.0, "WNS", reasons)
    if wns is not None and float(wns) < 0.0:
        penalty = -min(40.0, abs(float(wns)) * 20.0)
        score += penalty
        reasons.append(f"negative WNS penalty {penalty:.2f}")
    return score, reasons


def collect_qor_summary(paths: list[Path]) -> dict[str, object]:
    summary = {
        "timing_wns_ns": None,
        "timing_tns_ns": None,
        "setup_violations": None,
        "hold_violations": None,
        "logical_area_um2": None,
        "physical_area_um2": None,
        "power_mw": None,
        "congestion_overflow": None,
        "cell_count": None,
        "source_reports": [],
    }
    for path in paths:
        if not path.exists():
            continue
        parsed = _parse_from_name(path)
        if not parsed:
            continue
        _merge_metrics(parsed, {})
        if summary["timing_wns_ns"] is None:
            summary["timing_wns_ns"] = parsed.get("wns_ns")
        if summary["timing_tns_ns"] is None:
            summary["timing_tns_ns"] = parsed.get("tns_ns")
        if summary["logical_area_um2"] is None:
            summary["logical_area_um2"] = parsed.get("logical_area_um2")
        if summary["physical_area_um2"] is None:
            summary["physical_area_um2"] = parsed.get("physical_area_um2")
        if summary["setup_violations"] is None:
            summary["setup_violations"] = parsed.get("setup_violation_count")
        if summary["hold_violations"] is None:
            summary["hold_violations"] = parsed.get("hold_violation_count")
        if summary["power_mw"] is None:
            summary["power_mw"] = parsed.get("power_mw")
        if summary["congestion_overflow"] is None:
            summary["congestion_overflow"] = parsed.get("congestion")
        if summary["cell_count"] is None:
            summary["cell_count"] = parsed.get("cell_count")
        summary["source_reports"].extend(parsed.get("raw_reports", []))
    summary["source_reports"] = _dedupe(summary["source_reports"])
    _mark_missing_summary_values(summary)
    return summary


def _mark_missing_summary_values(summary: dict[str, object]) -> None:
    for key in [
        "timing_wns_ns",
        "timing_tns_ns",
        "setup_violations",
        "hold_violations",
        "logical_area_um2",
        "physical_area_um2",
        "power_mw",
        "congestion_overflow",
        "cell_count",
    ]:
        if summary.get(key) is None:
            summary[key] = "N/A"


def _empty_metrics() -> dict[str, Any]:
    return {
        "timing": {"wns_ns": None, "tns_ns": None, "setup_violation_count": None, "hold_violation_count": None, "source": None},
        "area": {"logical_um2": None, "physical_um2": None, "cell_count": None, "source": {}},
        "power": {"mw": None, "source": None},
        "routability": {"congestion": None, "utilization": None, "wirelength_um": None, "source": {}},
        "metadata": {"platform": None, "design_name": None, "clock_period_ns": None, "report_paths": {}},
        "metric_kind": None,
        "bottleneck_classification": None,
        "metric_source_file": None,
        "raw_reports": [],
        "targets": {},
        "wns_ns": None,
        "tns_ns": None,
        "setup_violation_count": None,
        "hold_violation_count": None,
        "logical_area_um2": None,
        "physical_area_um2": None,
        "power_mw": None,
        "congestion": None,
        "congestion_overflow": None,
        "utilization": None,
        "wirelength_um": None,
        "cell_count": None,
    }


def _parse_finish_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    metrics = _empty_metrics()
    metrics["timing"]["wns_ns"] = _sanitize_slack(payload.get("finish__timing__setup__ws"))
    metrics["timing"]["tns_ns"] = _sanitize_slack(payload.get("finish__timing__setup__tns"))
    metrics["timing"]["setup_violation_count"] = _to_int(payload.get("finish__timing__drv__setup_violation_count"))
    metrics["timing"]["hold_violation_count"] = _to_int(payload.get("finish__timing__drv__hold_violation_count"))
    metrics["timing"]["source"] = path.as_posix()
    metrics["area"]["physical_um2"] = _first_float(payload.get("finish__design__instance__area__stdcell"), payload.get("finish__design__instance__area"))
    metrics["area"]["cell_count"] = _first_int(payload.get("finish__design__instance__count__stdcell"), payload.get("finish__design__instance__count"))
    metrics["area"]["source"] = {"physical_um2": path.as_posix(), "cell_count": path.as_posix()}
    metrics["routability"]["congestion"] = _first_float(payload.get("finish__route__overflow"), payload.get("finish__route__wirelength__overflow"))
    metrics["routability"]["utilization"] = _to_float(payload.get("finish__design__instance__utilization"))
    metrics["routability"]["source"] = {"congestion": path.as_posix(), "utilization": path.as_posix()}
    power = _watts_to_mw(payload.get("finish__power__total"))
    metrics["power"]["mw"] = power
    metrics["power"]["source"] = path.as_posix() if power is not None else None
    metrics["raw_reports"] = [path.as_posix()]
    return _finalize_metrics(metrics)


def _parse_floorplan_report(path: Path) -> dict:
    metrics = _empty_metrics()
    metrics["raw_reports"] = [path.as_posix()]
    return _finalize_metrics(metrics)


def _parse_synth_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    metrics = _empty_metrics()
    area = _first_float(payload.get("synth__design__instance__area__stdcell"), payload.get("synth__design__instance__area"))
    count = _first_int(payload.get("synth__design__instance__count__stdcell"), payload.get("synth__design__instance__count"))
    power = _watts_to_mw(payload.get("synth__power__total"))
    metrics["area"]["logical_um2"] = area
    metrics["area"]["cell_count"] = count
    metrics["area"]["source"] = {"logical_um2": path.as_posix(), "cell_count": path.as_posix()}
    metrics["power"]["mw"] = power
    metrics["power"]["source"] = path.as_posix() if power is not None else None
    metrics["raw_reports"] = [path.as_posix()]
    return _finalize_metrics(metrics)


def _parse_qor_summary(path: Path) -> dict:
    text = _safe_read(path)
    metrics = _empty_metrics()
    payload: Any = None
    if path.suffix.lower() == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = None
    if isinstance(payload, dict):
        metrics["area"]["logical_um2"] = _first_payload_float(
            payload,
            [
                "logical_area_um2",
                "logical_area",
                "synth__design__instance__area__stdcell",
                "synth__design__instance__area",
                "design__instance__area",
            ],
        )
        metrics["power"]["mw"] = _first_payload_float(payload, ["power_mw", "total_power_mw"])
        if metrics["power"]["mw"] is None:
            metrics["power"]["mw"] = _watts_to_mw(
                _first_payload_float(payload, ["finish__power__total", "synth__power__total", "power_w", "total_power_w"])
            )
    if metrics["area"]["logical_um2"] is None:
        metrics["area"]["logical_um2"] = _search_first_float(
            text,
            [
                r"\blogical[_\s-]*area(?:[_\s-]*(?:um2|um\^2))?\s*[:=]\s*([0-9.eE+-]+)",
                r"\bsynth(?:esized)?[_\s-]*area(?:[_\s-]*(?:um2|um\^2))?\s*[:=]\s*([0-9.eE+-]+)",
                r"\bChip area for module .*?:\s*([0-9.eE+-]+)",
            ],
        )
    if metrics["area"]["logical_um2"] is not None:
        metrics["area"]["source"] = {"logical_um2": path.as_posix()}
    if metrics["power"]["mw"] is None:
        metrics["power"]["mw"] = _search_first_float(
            text,
            [
                r"\bpower[_\s-]*mw\s*[:=]\s*([0-9.eE+-]+)",
                r"\btotal[_\s-]*power(?:[_\s-]*mw)?\s*[:=]\s*([0-9.eE+-]+)\s*mW",
            ],
        )
    if metrics["power"]["mw"] is not None:
        metrics["power"]["source"] = path.as_posix()
    metrics["raw_reports"] = [path.as_posix()]
    return _finalize_metrics(metrics)


def _parse_route_report(path: Path) -> dict:
    text = _safe_read(path)
    metrics = _empty_metrics()
    metrics["routability"]["congestion"] = _search_float(text, r"Total\s+\d+\s+\d+\s+[0-9.]+%\s+\d+\s*/\s*\d+\s*/\s*([0-9.]+)")
    metrics["routability"]["source"] = {"congestion": path.as_posix()}
    metrics["raw_reports"] = [path.as_posix()]
    return _finalize_metrics(metrics)


def _parse_congestion_report(path: Path) -> dict:
    text = _safe_read(path)
    metrics = _empty_metrics()
    metrics["routability"]["congestion"] = _search_float(text, r"Total\s+\d+\s+\d+\s+[0-9.]+%\s+\d+\s*/\s*\d+\s*/\s*([0-9.]+)")
    metrics["routability"]["source"] = {"congestion": path.as_posix()}
    metrics["raw_reports"] = [path.as_posix()]
    return _finalize_metrics(metrics)


def _parse_grt_log(path: Path) -> dict:
    text = _safe_read(path)
    metrics = _empty_metrics()
    utilization_pct = _search_float(text, r"Utilization:\s*([0-9.]+)%")
    metrics["routability"]["congestion"] = _search_float(text, r"Total\s+\d+\s+\d+\s+[0-9.]+%\s+\d+\s*/\s*\d+\s*/\s*([0-9.]+)")
    metrics["routability"]["utilization"] = None if utilization_pct is None else utilization_pct / 100.0
    metrics["routability"]["wirelength_um"] = _search_float(text, r"Total wirelength:\s+([0-9.]+)\s+um")
    metrics["routability"]["source"] = {
        "congestion": path.as_posix(),
        "utilization": path.as_posix(),
        "wirelength_um": path.as_posix(),
    }
    metrics["raw_reports"] = [path.as_posix()]
    return _finalize_metrics(metrics)


def _merge_metrics(dest: dict[str, Any], src: dict[str, Any]) -> None:
    if not src:
        return
    for section in ["timing", "area", "power", "routability"]:
        src_section = src.get(section, {})
        dest_section = dest.setdefault(section, {})
        for key, value in src_section.items():
            if value is None:
                continue
            if key == "source":
                dest_section[key] = _merge_sources(dest_section.get(key), value)
            elif dest_section.get(key) is None:
                dest_section[key] = value
    dest["raw_reports"].extend(src.get("raw_reports", []))
    for key in ["metric_kind", "bottleneck_classification", "metric_source_file"]:
        if dest.get(key) is None and src.get(key) is not None:
            dest[key] = src.get(key)


def _finalize_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    metrics["raw_reports"] = _dedupe(metrics.get("raw_reports", []))
    metrics["wns_ns"] = metrics.get("timing", {}).get("wns_ns")
    metrics["tns_ns"] = metrics.get("timing", {}).get("tns_ns")
    metrics["setup_violation_count"] = metrics.get("timing", {}).get("setup_violation_count")
    metrics["hold_violation_count"] = metrics.get("timing", {}).get("hold_violation_count")
    metrics["logical_area_um2"] = metrics.get("area", {}).get("logical_um2")
    metrics["physical_area_um2"] = metrics.get("area", {}).get("physical_um2")
    metrics["power_mw"] = metrics.get("power", {}).get("mw")
    metrics["congestion"] = metrics.get("routability", {}).get("congestion")
    metrics["congestion_overflow"] = metrics.get("routability", {}).get("congestion")
    metrics["utilization"] = metrics.get("routability", {}).get("utilization")
    metrics["wirelength_um"] = metrics.get("routability", {}).get("wirelength_um")
    metrics["cell_count"] = metrics.get("area", {}).get("cell_count")
    return metrics


def _classification(
    family: str,
    reasons: list[str | None],
    source: Any,
    primary: str | None = None,
    action_family: str | None = None,
) -> dict[str, Any]:
    filtered = [reason for reason in reasons if reason]
    return {
        "primary_bottleneck": primary or family,
        "metric_kind": family,
        "bottleneck_classification": primary or family,
        "reasons": filtered or ["No reasons recorded."],
        "metric_source_file": source,
        "action_family_hint": action_family or (family if family != "unknown" else "none"),
        "metric_family_priority": FAMILY_PRIORITY.get(family, FAMILY_PRIORITY["unknown"]),
    }


def _target_penalty(value: float | None, target: float | None, higher_is_better: bool, scale: float, label: str, reasons: list[str]) -> float:
    if value is None or target is None:
        return 0.0
    miss = (target - value) if higher_is_better else (value - target)
    if miss <= 0:
        return 0.0
    penalty = -miss * scale
    reasons.append(f"{label} miss penalty {penalty:.2f}")
    return penalty


def _metric(metrics: dict[str, Any], key: str) -> float | None:
    return _to_float(metrics.get(key))


def _target(targets: dict[str, Any], key: str, default: float | None) -> float | None:
    return _to_float(targets.get(key), default)


def _pick_source(source: Any, *keys: str) -> Any:
    if isinstance(source, dict):
        for key in keys:
            if source.get(key):
                return source[key]
    return source


def _merge_sources(current: Any, incoming: Any) -> Any:
    if current is None or current == "":
        return incoming
    if isinstance(current, dict) and isinstance(incoming, dict):
        merged = dict(current)
        for key, value in incoming.items():
            merged.setdefault(key, value)
        return merged
    return current


def _parse_from_name(path: Path) -> dict[str, Any]:
    if path.name == "6_finish.rpt":
        return parse_finish_report(path)
    if path.name == "synth_stat.txt":
        return parse_synth_stats(path)
    if path.name.startswith("qor_summary") or path.name == "metrics.json":
        return _parse_qor_summary(path)
    if path.name == "6_report.json":
        return _parse_finish_json(path)
    if path.name == "2_floorplan_final.rpt":
        return _parse_floorplan_report(path)
    if path.name == "5_global_route.rpt":
        return _parse_route_report(path)
    if path.name == "5_1_grt.log":
        return _parse_grt_log(path)
    if path.name == "congestion.rpt":
        return _parse_congestion_report(path)
    return {}


def _normalize_flow_dir(flow_root: Path) -> Path:
    if flow_root.name == "flow" and (flow_root / "Makefile").exists():
        return flow_root
    if (flow_root / "flow" / "Makefile").exists():
        return flow_root / "flow"
    return flow_root


def _sanitize_slack(value: Any) -> float | None:
    parsed = _to_float(value)
    if parsed is None or math.isinf(parsed) or abs(parsed) >= 1e30:
        return None
    return parsed


def _search_float(text: str, pattern: str, flags: int = 0) -> float | None:
    match = re.search(pattern, text, flags | re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    return _to_float(match.group(match.lastindex or 1))


def _search_first_float(text: str, patterns: list[str], flags: int = 0) -> float | None:
    for pattern in patterns:
        value = _search_float(text, pattern, flags)
        if value is not None:
            return value
    return None


def _search_int(text: str, pattern: str, flags: int = 0) -> int | None:
    match = re.search(pattern, text, flags | re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    return _to_int(match.group(match.lastindex or 1))


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _first_float(*values: Any) -> float | None:
    for value in values:
        parsed = _to_float(value)
        if parsed is not None:
            return parsed
    return None


def _first_int(*values: Any) -> int | None:
    for value in values:
        parsed = _to_int(value)
        if parsed is not None:
            return parsed
    return None


def _first_payload_float(payload: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        if key in payload:
            parsed = _to_float(payload.get(key))
            if parsed is not None:
                return parsed
    for value in payload.values():
        if isinstance(value, dict):
            parsed = _first_payload_float(value, keys)
            if parsed is not None:
                return parsed
    return None


def _first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _to_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return default
    lowered = text.lower()
    if lowered in {"inf", "+inf", "infinity", "+infinity"}:
        return math.inf
    if lowered in {"-inf", "-infinity"}:
        return -math.inf
    try:
        return float(text)
    except ValueError:
        return default


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return None


def _watts_to_mw(value: Any) -> float | None:
    parsed = _to_float(value)
    if parsed is None:
        return None
    return parsed * 1000.0


def _dedupe(values: list[Any]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            ordered.append(text)
    return ordered
