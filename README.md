# Spec-to-Tapeout AI Agent  
### End-to-End RTL-to-GDSII ASIC Design Automation with QoR Optimization

---

## Overview
This project implements an AI-driven Spec-to-Tapeout agent that converts high-level YAML design specifications into manufacturable GDSII layouts.

The system automates the complete ASIC design flow:

**Spec → RTL → Simulation → Synthesis → OpenROAD → QoR → Signoff → GDSII**

---

## Key Contributions
- End-to-end ASIC design automation  
- QoR-driven optimization (Area, Power, Timing)  
- Post-synthesis equivalence verification  
- Failure-aware self-repair pipeline  
- Pareto-based design space exploration  
- Automated QoR visualization and reporting  

---

## Key Features
- Fully automated pipeline (single-command execution)  
- Iterative QoR optimization  
- Functional verification and equivalence checking  
- Robust failure detection and recovery  
- Pareto tradeoff analysis  
- Performance visualization (plots and reports)  

---

## Pipeline
Spec → RTL → Simulation → Synthesis → Equivalence → P&R → QoR → Signoff → GDSII  

---

## Quick Start (Recommended)

Run the complete pipeline:

```bash
python3 run_all_specs.py

This command:

Executes all designs
Generates QoR reports
Produces plots
Prints final summary
⚙️ Setup Instructions
1. Clone the repository
git clone https://github.com/sdhanda6/spec-to-rtl-agent.git
cd spec-to-rtl-agent
2. Create virtual environment
pip install --user virtualenv
export PATH=$HOME/.local/bin:$PATH
virtualenv venv
3. Activate environment
source venv/bin/activate
4. Install dependencies
pip install -r requirements.txt

Usage
Run a single design
python3 run_pipeline.py --spec examples/specs/p1.yaml --mode full --overwrite
Run optimized flow
python3 run_pipeline.py \
  --spec examples/specs/p1.yaml \
  --mode full \
  --overwrite \
  --optimize-synth \
  --optimize-qor \
  --verify-post-synth \
  --run-signoff

Input

All design specifications are located in:

examples/specs/

Each YAML file defines:

Module behavior
Inputs and outputs
Functional logic

Output

All outputs are organized per design in:

outputs/<design_name>/

Each design folder contains:

Logs
Reports
QoR metrics
Intermediate flow outputs

Generated Artifacts

Plots are stored in:

outputs/plots/

Includes:

area.png
power.png
pareto.png

Expected Results after execution:

All designs complete successfully
RTL generation and simulation pass
OpenROAD completes full flow
Timing closure achieved (WNS ≈ 0)
QoR metrics generated (Area, Power, WNS, TNS)
Pareto-optimal designs identified

Workflow
Parse YAML → generate RTL
Run simulation → verify correctness
Perform synthesis (Yosys)
Run OpenROAD (placement, routing, STA)
Extract QoR metrics
Apply optimization loops
Generate reports and plots

Running Custom / Hidden Testcases
python3 run_pipeline.py --spec <your_spec.yaml> --mode full --overwrite

Ensure:

YAML format matches examples
Includes module definition and behavior

Limitations
Full DRC/LVS requires complete Sky130 PDK
Open-source tools provide limited optimization compared to commercial EDA tools
Parallel execution requires careful resource handling

Authors
Sudarshan Dhandapani
Lakshminarayanaa Rajamanar

Summary

An AI-driven system for automating ASIC design flow with adaptive optimization, verification, and intelligent decision-making.

