# Mini Project 2 Phase 2: Spec-to-RTL Agent

## Project Overview
This repository contains a Spec-to-RTL AI agent for Mini Project 2 Phase 2.

The system accepts either structured YAML specifications or less-structured text specifications, normalizes them into semantic candidates, lowers them into a semantic intermediate representation (IR), generates synthesizable Verilog RTL and a matching testbench, runs compile/simulation verification with Icarus Verilog, and emits machine-readable YAML verification reports.

The generation flow includes a bounded feedback-driven repair loop and candidate ranking stage. If a generated design fails compile or simulation, the agent captures the exact `iverilog`/`vvp` output, diagnoses the failure, updates IR or rendering decisions, and retries automatically until the design passes or the retry budget is exhausted. For unstructured or ambiguous specs, the agent can retain multiple semantic candidates and rank them using consistency checks plus verification evidence.

## Problem Definition
The project goal is to automate the flow:

`spec text/YAML -> semantic candidate normalization -> IR -> RTL -> testbench -> compile/sim verification -> report`

The repository is focused on logical RTL generation and verification only. Physical-design tasks are out of scope.

## Repository Contents
- `agent.py`: main RTL/testbench generation and reporting driver
- `run_pipeline.py`: single-command end-to-end entry point for grading and reproduction
- `run_sim.py`: EDA interaction layer for `iverilog` / `vvp`
- `spec.yaml`: default YAML input spec
- `spec2rtl/`: parser, IR, lowering, expression, rendering, and feedback/repair modules
- `examples/specs/`: sample YAML specs
- `examples/outputs/`: sample generated RTL, testbench, report, and pipeline log
- `rtl/`: generated RTL output location
- `tb/`: generated testbench output location
- `build/attempts/`: per-attempt RTL/testbench snapshots from the repair loop
- `build/reports/`: generated YAML verification reports
- `build/logs/`: pipeline execution logs

## Setup Instructions
### Python
- Python 3.11+ is recommended.

### EDA Tools
- Install Icarus Verilog and ensure both `iverilog` and `vvp` are available in `PATH`.

Windows example:
- Install Icarus Verilog
- Confirm:

```powershell
iverilog -V
vvp -V
```

## Dependencies
Python dependencies are standard-library only.

```powershell
pip install -r requirements.txt
```

## Single-Command Run
Run the full pipeline on the default YAML spec:

```powershell
python run_pipeline.py --spec spec.yaml --overwrite
```

Run the full pipeline on a sample example:

```powershell
python run_pipeline.py --spec examples/specs/upcounter16.yaml --overwrite
```

Run the pipeline with a reproducible first-pass bug to demonstrate repair:

```powershell
python run_pipeline.py --spec spec.yaml --overwrite --inject-fault counter_hold_when_enabled --max-passes 3
```

## Input / Output Description
### Input
A YAML spec describing:
- module name
- ports
- timing/reset semantics
- behavior
- verification intent

Default input:
- `spec.yaml`

Sample inputs:
- `examples/specs/upcounter16.yaml`

### Outputs
For a spec with top module `<top>`:
- RTL: `rtl/<top>.v`
- testbench: `tb/tb_<top>.sv`
- per-attempt snapshots: `build/attempts/<top>/attempt_<n>/`
- verification report: `build/reports/<top>_report.yaml`
- pipeline log: `build/logs/<top>_pipeline.log`

## Expected Results
For the included `upcounter16` sample, a successful run should:
- generate `rtl/upcounter16.v`
- generate `tb/tb_upcounter16.sv`
- pass `iverilog` compilation
- pass `vvp` simulation
- emit a YAML report marking:
  - `compile_pass: true`
  - `functional_sim_pass: true`
  - `overall_pass: true`

Example output artifacts are included in:
- `examples/outputs/upcounter16/`

## Workflow Summary
1. Parse YAML spec.
2. Lower the spec into semantic IR.
3. Render RTL and testbench.
4. Compile with `iverilog`.
5. Simulate with `vvp`.
6. If compile/sim fails, analyze diagnostics and update IR or rendering strategy.
7. Retry generation up to the configured repair limit.
8. Emit YAML report and pipeline log.

## Feedback-Driven Repair Loop
The repair loop is implemented as a bounded iterative flow inside `agent.py` with diagnostics and repair logic factored into `spec2rtl/feedback.py`.

Each attempt performs:
1. RTL/testbench generation
2. `iverilog` compile
3. `vvp` simulation when compile succeeds
4. diagnosis of the exact tool output
5. targeted IR or renderer updates before the next regeneration

Each YAML report stores structured per-attempt diagnostics including:
- attempt number
- render strategy used
- RTL and testbench snapshot paths
- compile command
- simulation command
- compile status
- simulation status
- exact compile stdout/stderr
- exact simulation stdout/stderr
- diagnosis summary
- next regeneration changes

Current repair actions are conservative and deterministic:
- compile failures can trigger renderer fallback or verification downgrades for unsupported cases
- counter simulation failures can repair increment/hold behavior when the failure message matches known checks
- register simulation failures can repair missing enabled loads or missing hold behavior
- shift-register simulation failures can repair reversed shift direction or missing enable gating
- FSM simulation failures can repair injected self-loop behavior that blocks declared transitions
- combinational, generic sequential, and datapath-style vector/step failures can repair targeted forced-zero output overrides

Current front-end generalization features:
- YAML specs still map directly into normalized semantic candidates
- text specs are mined for module name, ports, clock/reset semantics, state, and simple sequential/combinational rules
- ambiguity findings are reported explicitly instead of being hidden
- candidate ranking favors internally consistent, independently verified interpretations

Functional success is only claimed when the final simulation evidence explicitly passes. If retries are exhausted, the report marks the design as unrepaired rather than claiming success.

## Repair Demo
The repository supports a reproducible repair demo via fault injection.

Example:

```powershell
python run_pipeline.py --spec spec.yaml --overwrite --inject-fault counter_hold_when_enabled --max-passes 3
```

In that demo:
1. Attempt 1 generates a faulty counter that holds value when `en` is high.
2. The generated testbench fails with `increment failed`.
3. The repair loop captures that `vvp` failure text and diagnoses the counter increment mismatch.
4. Attempt 2 regenerates corrected RTL.
5. The final simulation passes and the report marks the design as repaired after feedback.

The resulting repair history is written to:
- `build/reports/upcounter16_report.yaml`
- `build/attempts/upcounter16/attempt_1/`
- `build/attempts/upcounter16/attempt_2/`

To run the generalized multi-class demo:

```powershell
python run_repair_demos.py
```

That script exercises:
- counter
- register
- shift register
- FSM
- combinational logic
- generic sequential logic
- arithmetic/datapath-style sequential logic
- less-structured text normalization

It writes a summary to:
- `build/reports/generalized_repair_demo_summary.yaml`

## Hidden Testcase Instructions
To run a hidden testcase, the grader only needs to supply a different YAML spec path:

```powershell
python run_pipeline.py --spec path\to\hidden_case.yaml --overwrite
```

No code changes are required.

The hidden spec must be a `.yaml` or `.yml` file compatible with the documented structured workflow.

## Limitations / Current Scope
- Unstructured text support is heuristic rather than language-complete; broad prose can still be only partially normalized.
- The system supports a broader IR-driven set of combinational and sequential designs, but it is not a universal natural-language-to-RTL compiler.
- Functional verification is only claimed when explicit evidence is generated by the testbench/oracle path.
- Unsupported or partially supported cases are reported conservatively in YAML reports instead of being labeled as full success.
- Candidate generation is intentionally bounded; the tool explores a few plausible interpretations, not an open-ended search over all circuits consistent with the prose.
- The repair loop is real but still conservative: it applies targeted compile/render and behavioral fixes rather than inventing arbitrary semantics after a failed test.
- Generic and benchmark-style designs still repair conservatively, and many unmatched failures fall back to renderer changes or partial-support reports instead of deep semantic correction.
Run the full pipeline on a less-structured text spec:

```powershell
python run_pipeline.py --spec examples/specs/text_counter.txt --overwrite
```
