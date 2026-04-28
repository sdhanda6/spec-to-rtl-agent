# AGENTS.md

## Scope
This repository is for Mini Project 2 Spec-to-RTL only.

The project goal is to build a lightweight agent that:
- reads a structured hardware specification from `spec.yaml`
- extracts a top module name and interface/behavior semantics
- generates a synthesizable Verilog RTL module in `rtl/`

Out of scope:
- floorplanning
- placement and routing
- timing closure
- GDS generation
- any other physical-design tasks

## Primary Files
- `spec.yaml`: structured YAML input specification for the hardware block
- `agent.py`: Spec-to-RTL generator
- `run_sim.py`: Verilog compile/syntax check for generated RTL
- `rtl/`: generated or edited RTL modules
- `tb/`: optional sandbox area, not required for this project scope

## Expected Workflow
1. Write the hardware spec in `spec.yaml`.
2. Run `python agent.py`.
3. Inspect the generated RTL in `rtl/`.
4. Run `python run_sim.py` to compile-check the RTL.
5. Refine the spec and regenerate as needed.

## Input Expectations
The input is structured YAML. The generator works best if the spec includes:
- `module.name`
- `ports`
- timing/reset information when sequential logic is present
- `design.behavior`
- `verification.tb`

Example:

```yaml
module:
  name: pulse_counter

ports:
  - {name: clk, dir: input, width: 1}
  - {name: rst_n, dir: input, width: 1}
  - {name: en, dir: input, width: 1}
  - {name: count, dir: output, width: 8, kind: reg}

timing:
  clock: clk
  reset: {signal: rst_n, active: low, mode: async}

design:
  kind: counter
  state:
    - {name: count, width: 8, reset: 0}
  behavior:
    counter: {target: count, enable: en, direction: up, step: 1, wrap: true}
```

## Generator Behavior
- If the spec names clock/reset signals such as `clk`, `clock`, `rst`, or `rst_n`, the agent emits a sequential skeleton using `always @(posedge ... )`.
- Otherwise, the agent emits a combinational skeleton using `always @*`.
- Output ports are given safe default assignments so the emitted module is synthesizable.
- The generator is intentionally conservative. It creates a correct starter RTL shell, not a full behavioral implementation of arbitrary English requirements.

## Typical Commands
Generate RTL from the current spec:

```powershell
python agent.py
```

Write to a different output file:

```powershell
python agent.py --out rtl\my_block.v
```

Compile-check the generated module:

```powershell
python run_sim.py
```

## Notes
- Generated RTL is standard Verilog, not a physical-design artifact.
- `run_sim.py` validates compilation only; it does not require a testbench.
