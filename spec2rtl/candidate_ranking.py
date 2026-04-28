from __future__ import annotations

from spec2rtl.ir import VerificationEvidenceIR


def score_candidate(
    internal_score: float,
    compile_ok: bool,
    sim_ok: bool,
    evidence: VerificationEvidenceIR,
    ambiguity_count: int,
    unsupported_count: int,
    attempts_used: int,
) -> float:
    score = internal_score
    if compile_ok:
        score += 3.0
    if sim_ok:
        score += 2.0
    if evidence.achieved_level == "functional" and evidence.oracle_independent and sim_ok:
        score += 3.0
    elif evidence.achieved_level == "smoke" and sim_ok:
        score += 1.0
    score -= 0.35 * ambiguity_count
    score -= 0.75 * unsupported_count
    score -= 0.15 * max(0, attempts_used - 1)
    return score


def classify_final_verdict(
    compile_ok: bool,
    sim_ok: bool,
    evidence: VerificationEvidenceIR,
    ambiguity_count: int,
    unsupported_count: int,
) -> str:
    if sim_ok and evidence.achieved_level == "functional" and evidence.oracle_independent and unsupported_count == 0:
        return "functionally_verified"
    if compile_ok and sim_ok and evidence.achieved_level == "smoke":
        return "compile_and_smoke_verified"
    if compile_ok or sim_ok:
        return "partially_supported"
    if ambiguity_count > 0 or unsupported_count > 0:
        return "unsupported_or_ambiguous"
    return "unsupported_or_ambiguous"
