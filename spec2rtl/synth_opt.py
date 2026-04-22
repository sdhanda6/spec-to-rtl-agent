from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SYNTH_HISTORY_PATH = REPO_ROOT / "build" / "synth_history.json"


SYNTH_KNOB_REGISTRY: dict[str, list[dict[str, Any]]] = {
    "timing": [
        {
            "candidate_id": "synth_timing_push_clock_07x",
            "why_this_candidate": "tighten the clock aggressively and enable retiming to force a harder timing search point",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 0.7, "reason": "push synthesis toward a much stronger timing target"},
                {"knob": "SYNTH_RETIMING", "action": "set", "value": "1", "reason": "allow retiming under tighter timing pressure"},
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "DELAY 3", "reason": "use the most aggressive timing-biased strategy"},
                {"knob": "MAX_FANOUT_CONSTRAINT", "action": "set", "value": "6", "reason": "reduce critical fanout aggressively"},
            ],
        },
        {
            "candidate_id": "synth_timing_retime_small",
            "why_this_candidate": "relax the clock slightly and enable retiming for a timing-biased remap",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.05, "reason": "slightly reduce synthesis timing pressure"},
                {"knob": "SYNTH_RETIMING", "action": "set", "value": "1", "reason": "allow retiming during synthesis"},
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "DELAY 1", "reason": "use a timing-oriented mapping strategy"},
            ],
        },
        {
            "candidate_id": "synth_timing_effort_high",
            "why_this_candidate": "increase synthesis effort and use a more aggressive delay strategy",
            "knobs": [
                {"knob": "SYNTH_RETIMING", "action": "set", "value": "1", "reason": "allow retiming for critical paths"},
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "DELAY 2", "reason": "push for stronger delay optimization"},
                {"knob": "SYNTH_SIZING", "action": "set", "value": "1", "reason": "allow upsizing when timing needs it"},
            ],
        },
        {
            "candidate_id": "synth_timing_flatten_retime",
            "why_this_candidate": "flatten hierarchy and retime to expose more logic optimization opportunities",
            "knobs": [
                {"knob": "SYNTH_NO_FLAT", "action": "set", "value": "0", "reason": "allow hierarchy flattening for optimization"},
                {"knob": "SYNTH_RETIMING", "action": "set", "value": "1", "reason": "enable retiming"},
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "DELAY 3", "reason": "use a stronger timing strategy"},
            ],
        },
        {
            "candidate_id": "synth_timing_retime_fanout",
            "why_this_candidate": "combine retiming with tighter fanout control for critical-path cleanup",
            "knobs": [
                {"knob": "SYNTH_RETIMING", "action": "set", "value": "1", "reason": "allow retiming"},
                {"knob": "MAX_FANOUT_CONSTRAINT", "action": "set", "value": "8", "reason": "reduce excessive fanout on critical paths"},
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "DELAY 2", "reason": "keep timing-biased mapping enabled"},
            ],
        },
        {
            "candidate_id": "synth_timing_conservative_baseline",
            "why_this_candidate": "keep timing-oriented mapping but remove extra restructuring to probe a different local optimum",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.0, "reason": "preserve the baseline clock target"},
                {"knob": "SYNTH_RETIMING", "action": "set", "value": "0", "reason": "disable retiming to test a simpler mapping point"},
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "DELAY 1", "reason": "keep timing-oriented mapping without maximal effort"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "1", "reason": "allow normal buffering under timing optimization"},
            ],
        },
    ],
    "area": [
        {
            "candidate_id": "synth_area_map_area2",
            "why_this_candidate": "bias mapping for minimum area and reduce extra buffering",
            "knobs": [
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "AREA 2", "reason": "favor smaller mapped area"},
                {"knob": "ABC_AREA", "action": "set", "value": "1", "reason": "bias mapping toward smaller cells"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "avoid surplus buffers"},
            ],
        },
        {
            "candidate_id": "synth_area_share_resources",
            "why_this_candidate": "encourage logic sharing and keep hierarchy where it helps reuse",
            "knobs": [
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "AREA 1", "reason": "moderate area optimization"},
                {"knob": "SYNTH_SHARE_RESOURCES", "action": "set", "value": "1", "reason": "encourage logic sharing"},
                {"knob": "SYNTH_NO_FLAT", "action": "set", "value": "1", "reason": "keep hierarchy if it reduces remap churn"},
            ],
        },
        {
            "candidate_id": "synth_area_reduce_buffers",
            "why_this_candidate": "avoid area growth from sizing and fanout-driven buffering",
            "knobs": [
                {"knob": "SYNTH_SIZING", "action": "set", "value": "0", "reason": "avoid upsizing for marginal gain"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "cut inserted buffers"},
                {"knob": "MAX_FANOUT_CONSTRAINT", "action": "set", "value": "16", "reason": "reduce buffer insertion pressure"},
            ],
        },
        {
            "candidate_id": "synth_area_flatten_compact",
            "why_this_candidate": "flatten the design and remap with an area-biased strategy",
            "knobs": [
                {"knob": "SYNTH_NO_FLAT", "action": "set", "value": "0", "reason": "enable flattening for global compaction"},
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "AREA 2", "reason": "favor compact mapping after flattening"},
                {"knob": "SYNTH_SHARE_RESOURCES", "action": "set", "value": "1", "reason": "share duplicated structures"},
            ],
        },
        {
            "candidate_id": "synth_area_relaxed_clock_13x",
            "why_this_candidate": "relax timing pressure to let synthesis choose smaller cells and fewer buffers",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.3, "reason": "reduce timing pressure for area-biased mapping"},
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "AREA 2", "reason": "favor compact mapping"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "avoid surplus buffer insertion"},
                {"knob": "MAX_FANOUT_CONSTRAINT", "action": "set", "value": "18", "reason": "reduce fanout-driven buffer pressure"},
            ],
        },
    ],
    "power": [
        {
            "candidate_id": "synth_power_reduce_buffers",
            "why_this_candidate": "limit buffer insertion and sizing to lower switching power",
            "knobs": [
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "reduce inserted buffers"},
                {"knob": "SYNTH_SIZING", "action": "set", "value": "0", "reason": "avoid unnecessary upsizing"},
                {"knob": "MAX_FANOUT_CONSTRAINT", "action": "set", "value": "12", "reason": "reduce repeater pressure"},
            ],
        },
        {
            "candidate_id": "synth_power_area_strategy",
            "why_this_candidate": "smaller mapped cells often reduce total power on small blocks",
            "knobs": [
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "AREA 2", "reason": "prefer smaller cells"},
                {"knob": "ABC_AREA", "action": "set", "value": "1", "reason": "bias mapping for area and lower capacitance"},
                {"knob": "SYNTH_SHARE_RESOURCES", "action": "set", "value": "1", "reason": "reduce duplicate logic"},
            ],
        },
        {
            "candidate_id": "synth_power_relax_clock",
            "why_this_candidate": "relax timing pressure slightly to avoid power-costly optimization",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.08, "reason": "reduce timing pressure"},
                {"knob": "SYNTH_SIZING", "action": "set", "value": "0", "reason": "avoid power-heavy upsizing"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "avoid extra clock/data buffering"},
            ],
        },
        {
            "candidate_id": "synth_power_keep_hierarchy",
            "why_this_candidate": "preserve hierarchy and reduce optimization churn to limit power-heavy remapping",
            "knobs": [
                {"knob": "SYNTH_NO_FLAT", "action": "set", "value": "1", "reason": "keep hierarchy intact"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "limit inserted buffers"},
                {"knob": "MAX_FANOUT_CONSTRAINT", "action": "set", "value": "14", "reason": "avoid aggressive repeater insertion"},
            ],
        },
        {
            "candidate_id": "synth_power_relaxed_clock_13x",
            "why_this_candidate": "combine a relaxed clock with conservative mapping to search a lower-power point",
            "knobs": [
                {"knob": "CLOCK_PERIOD", "action": "scale", "value": 1.3, "reason": "reduce timing pressure further for lower-power mapping"},
                {"knob": "SYNTH_SIZING", "action": "set", "value": "0", "reason": "avoid power-heavy upsizing"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "avoid inserted buffers"},
                {"knob": "SYNTH_NO_FLAT", "action": "set", "value": "1", "reason": "limit disruptive remapping"},
            ],
        },
    ],
    "structural": [
        {
            "candidate_id": "synth_struct_flatten",
            "why_this_candidate": "flatten hierarchy to expose more global optimization opportunities",
            "knobs": [
                {"knob": "SYNTH_NO_FLAT", "action": "set", "value": "0", "reason": "allow flattening"},
                {"knob": "SYNTH_SHARE_RESOURCES", "action": "set", "value": "1", "reason": "share equivalent structures"},
                {"knob": "SYNTH_RETIMING", "action": "set", "value": "0", "reason": "keep this structural-focused instead of timing-focused"},
            ],
        },
        {
            "candidate_id": "synth_struct_keep_hierarchy",
            "why_this_candidate": "preserve hierarchy to reduce over-optimization and keep structure stable",
            "knobs": [
                {"knob": "SYNTH_NO_FLAT", "action": "set", "value": "1", "reason": "keep module boundaries intact"},
                {"knob": "SYNTH_SHARE_RESOURCES", "action": "set", "value": "0", "reason": "avoid aggressive merging"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "0", "reason": "keep the mapped netlist smaller and simpler"},
            ],
        },
        {
            "candidate_id": "synth_struct_flatten_area",
            "why_this_candidate": "combine flattening with area-biased mapping to explore an alternate structural point",
            "knobs": [
                {"knob": "SYNTH_NO_FLAT", "action": "set", "value": "0", "reason": "enable flattening"},
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "AREA 1", "reason": "apply area-biased mapping after flattening"},
                {"knob": "ABC_AREA", "action": "set", "value": "1", "reason": "favor compact mapping"},
            ],
        },
        {
            "candidate_id": "synth_struct_flatten_timing",
            "why_this_candidate": "combine flattening with timing effort to expose deeper structural rewrites",
            "knobs": [
                {"knob": "SYNTH_NO_FLAT", "action": "set", "value": "0", "reason": "enable flattening"},
                {"knob": "SYNTH_RETIMING", "action": "set", "value": "1", "reason": "allow timing-aware restructuring"},
                {"knob": "SYNTH_STRATEGY", "action": "set", "value": "DELAY 1", "reason": "use timing-biased remapping after flattening"},
            ],
        },
        {
            "candidate_id": "synth_struct_fanout_rebalance",
            "why_this_candidate": "explore a structural rebalance point with moderate flattening pressure and tighter fanout control",
            "knobs": [
                {"knob": "SYNTH_NO_FLAT", "action": "set", "value": "0", "reason": "allow cross-hierarchy restructuring"},
                {"knob": "MAX_FANOUT_CONSTRAINT", "action": "set", "value": "10", "reason": "push synthesis to rebalance high-fanout cones"},
                {"knob": "SYNTH_BUFFERING", "action": "set", "value": "1", "reason": "allow controlled structural buffering"},
                {"knob": "SYNTH_SHARE_RESOURCES", "action": "set", "value": "1", "reason": "merge structurally similar logic where possible"},
            ],
        },
    ],
}


def generate_synth_candidates(base_cfg: dict[str, Any], bottleneck: dict[str, Any]) -> list[dict[str, Any]]:
    primary = str(bottleneck.get("metric_kind", "unknown"))
    family_order = _family_search_order(primary)
    candidates: list[dict[str, Any]] = []
    for rank, family in enumerate(family_order, start=1):
        for template in SYNTH_KNOB_REGISTRY.get(family, []):
            knobs = [dict(item) for item in template.get("knobs", [])]
            mismatch = primary not in {family, "mixed", "unknown", "logical_area"} if family != "area" else primary not in {"logical_area", "area", "cell_count", "mixed", "unknown"}
            candidates.append(
                {
                    "family": family,
                    "candidate_id": str(template["candidate_id"]),
                    "family_priority_rank": rank,
                    "why_this_candidate": template["why_this_candidate"],
                    "metric_kind_it_targets": primary,
                    "knobs": knobs,
                    "mismatch": mismatch,
                    "rejected": False,
                    "reject_reason": None,
                    "action_family_matched_bottleneck": not mismatch,
                    "base_vars": dict(base_cfg.get("vars", {})) if isinstance(base_cfg.get("vars"), dict) else {},
                }
            )
    return candidates


def rank_synth_candidates(
    candidates: list[dict[str, Any]],
    history: list[dict[str, Any]],
    bottleneck: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    bottleneck = bottleneck or {}
    context = context or {}
    if not history:
        ranked = sorted(
            [dict(candidate) for candidate in candidates],
            key=lambda item: (bool(item.get("rejected")), bool(item.get("mismatch")), int(item.get("family_priority_rank", 999)), str(item.get("candidate_id", ""))),
        )
        for index, candidate in enumerate(ranked, start=1):
            candidate["predicted_score"] = 0.0
            candidate["ranking_reason"] = "rule-based fallback because no synthesis history exists yet"
            candidate["rank"] = index
        return ranked

    ranked: list[dict[str, Any]] = []
    for candidate in candidates:
        enriched = dict(candidate)
        enriched.update({key: value for key, value in context.items() if key not in enriched})
        predicted = predict_synth_candidate_score(enriched, history, bottleneck)
        enriched["predicted_score"] = predicted
        enriched["ranking_reason"] = _candidate_reason(enriched, history, bottleneck, predicted)
        ranked.append(enriched)
    ranked.sort(
        key=lambda item: (
            bool(item.get("rejected")),
            bool(item.get("mismatch")),
            -float(item.get("predicted_score", 0.0)),
            int(item.get("family_priority_rank", 999)),
            str(item.get("candidate_id", "")),
        )
    )
    for index, candidate in enumerate(ranked, start=1):
        candidate["rank"] = index
    return ranked


def select_synth_candidates_for_round(
    candidates: list[dict[str, Any]],
    attempted_ids: set[str],
    max_candidates: int = 3,
    min_families: int = 3,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_families: set[str] = set()
    remaining = [item for item in candidates if str(item.get("candidate_id")) not in attempted_ids]
    for candidate in remaining:
        family = str(candidate.get("family", "unknown"))
        if family in seen_families and len(seen_families) < min_families:
            continue
        selected.append(candidate)
        seen_families.add(family)
        if len(selected) >= max_candidates:
            break
    if len(selected) < max_candidates:
        for candidate in remaining:
            if candidate in selected:
                continue
            selected.append(candidate)
            if len(selected) >= max_candidates:
                break
    return selected


def synth_candidate_to_config(candidate: dict[str, Any], base_cfg: dict[str, Any]) -> dict[str, Any]:
    suggestions = [
        dict(knob, action_family=candidate.get("family"), metric_kind=candidate.get("metric_kind_it_targets", candidate.get("metric_kind", "unknown")))
        for knob in candidate.get("knobs", [])
    ]
    return apply_synth_strategy(base_cfg, suggestions)


def load_synth_history(history_path: Path | None = None) -> list[dict[str, Any]]:
    path = history_path or DEFAULT_SYNTH_HISTORY_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def update_synth_history(attempt: dict[str, Any], history_path: Path | None = None) -> None:
    path = history_path or DEFAULT_SYNTH_HISTORY_PATH
    history = load_synth_history(path)
    history.append(dict(attempt))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history[-1000:], indent=2, sort_keys=True), encoding="utf-8")


def predict_synth_candidate_score(candidate: dict[str, Any], history: list[dict[str, Any]], bottleneck: dict[str, Any] | None = None) -> float:
    bottleneck = bottleneck or {}
    family = str(candidate.get("family", "none"))
    metric_kind = str(bottleneck.get("metric_kind", candidate.get("metric_kind_it_targets", "unknown")))
    bottleneck_class = str(bottleneck.get("bottleneck_classification", metric_kind))
    knob_names = set(_candidate_knob_names(candidate))
    weighted_total = 0.0
    weight_sum = 0.0
    family_samples = 0
    exact_samples = 0

    for past in history:
        if str(past.get("candidate_family", "none")) != family:
            continue
        family_samples += 1
        weight = 1.0
        if str(past.get("metric_kind", "unknown")) == metric_kind:
            weight += 2.0
        if str(past.get("bottleneck_classification", "unknown")) == bottleneck_class:
            weight += 1.5
            exact_samples += 1
        if candidate.get("spec_name") and past.get("spec_name") == candidate.get("spec_name"):
            weight += 0.5
        if candidate.get("design_kind") and past.get("design_kind") == candidate.get("design_kind"):
            weight += 1.0
        past_knobs = set(str(item) for item in past.get("candidate_knobs", []) if item)
        if knob_names and past_knobs:
            weight += len(knob_names & past_knobs) / max(len(knob_names | past_knobs), 1)

        outcome = 0.0
        outcome += _float_or_zero(past.get("improvement_amount")) * 4.0
        outcome += _float_or_zero(past.get("score_delta"))
        if past.get("behavior_match"):
            outcome += 2.0
        else:
            outcome -= 6.0
        if past.get("beat_baseline"):
            outcome += 3.0
        if past.get("targets_met"):
            outcome += 3.0

        weighted_total += outcome * weight
        weight_sum += weight

    if weight_sum == 0.0:
        return 0.0
    exploration_bonus = 1.5 / math.sqrt(family_samples + 1.0)
    exact_bonus = 0.5 if exact_samples == 0 else 0.0
    return (weighted_total / weight_sum) + exploration_bonus + exact_bonus


def apply_synth_strategy(base_config: dict[str, Any], suggestions: list[dict[str, Any]]) -> dict[str, Any]:
    vars_in = base_config.get("vars", {})
    vars_out = dict(vars_in) if isinstance(vars_in, dict) else {}
    history = list(base_config.get("applied_suggestions", [])) if isinstance(base_config.get("applied_suggestions"), list) else []
    notes = list(base_config.get("notes", [])) if isinstance(base_config.get("notes"), list) else []
    chosen_action_family = str(base_config.get("chosen_action_family", "none"))

    for suggestion in suggestions:
        family = str(suggestion.get("action_family") or suggestion.get("family") or "none")
        if chosen_action_family == "none" and family != "none":
            chosen_action_family = family
        knob = str(suggestion.get("knob", ""))
        action = str(suggestion.get("action", ""))
        value = suggestion.get("value")
        reason = str(suggestion.get("reason", ""))
        if reason:
            notes.append(reason)
        _apply_single_knob(vars_out, knob, action, value)
        history.append(dict(suggestion))

    updated = dict(base_config)
    updated["vars"] = vars_out
    updated["applied_suggestions"] = history
    updated["notes"] = notes
    updated["chosen_action_family"] = chosen_action_family
    updated["action_family_matches_bottleneck"] = True
    return updated


def _family_search_order(primary: str) -> list[str]:
    base: list[str] = []
    if primary in {"logical_area", "area", "cell_count"}:
        base.extend(["area", "structural", "power"])
    elif primary in {"timing", "setup", "hold"}:
        base.extend(["timing", "structural", "area"])
    elif primary == "power":
        base.extend(["power", "area", "structural"])
    elif primary == "structural":
        base.extend(["structural", "area", "timing"])
    for family in ["timing", "area", "power", "structural"]:
        if family not in base:
            base.append(family)
    return base


def _candidate_reason(candidate: dict[str, Any], history: list[dict[str, Any]], bottleneck: dict[str, Any], predicted: float) -> str:
    family = str(candidate.get("family", "none"))
    metric_kind = str(bottleneck.get("metric_kind", candidate.get("metric_kind_it_targets", "unknown")))
    related = [item for item in history if str(item.get("candidate_family", "none")) == family]
    exact = [item for item in related if str(item.get("metric_kind", "unknown")) == metric_kind]
    if exact:
        wins = sum(1 for item in exact if item.get("beat_baseline"))
        return f"learned from {len(exact)} similar synth attempts for {metric_kind}; {wins} beat baseline; predicted score {predicted:.2f}"
    if related:
        wins = sum(1 for item in related if item.get("beat_baseline"))
        return f"learned from {len(related)} prior {family} synth attempts; {wins} beat baseline; predicted score {predicted:.2f}"
    return f"exploration bonus for unseen {family} family; predicted score {predicted:.2f}"


def _candidate_knob_names(candidate: dict[str, Any]) -> list[str]:
    knobs = candidate.get("knobs", [])
    if not isinstance(knobs, list):
        return []
    return sorted(dict.fromkeys(str(item.get("knob")) for item in knobs if isinstance(item, dict) and item.get("knob")))


def _apply_single_knob(vars_out: dict[str, str], knob: str, action: str, value: Any) -> None:
    if knob == "CLOCK_PERIOD" and action == "scale":
        try:
            current = float(str(vars_out.get("CLOCK_PERIOD", "")).strip())
        except ValueError:
            current = None
        if current is not None and isinstance(value, (int, float)):
            vars_out["CLOCK_PERIOD"] = _format_float(current * float(value))
        return
    if knob and action == "set":
        vars_out[knob] = str(value)


def _format_float(value: float) -> str:
    text = f"{value:.4f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def _float_or_zero(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0
