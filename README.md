# 🚀 Spec-to-Tapeout AI Agent  
### End-to-End RTL-to-GDSII ASIC Design Automation with QoR Optimization

---

## 📌 Overview
This project implements an AI-driven Spec-to-Tapeout agent that converts high-level YAML design specifications into manufacturable GDSII layouts.

The system automates the complete ASIC design flow:

Spec → RTL → Simulation → Synthesis → OpenROAD → QoR → Signoff → GDSII

---

## What Makes This Project Unique
- AI-driven design optimization  
- Pareto tradeoff analysis  
- Self-explaining agent decisions  
- Fully automated RTL → GDS pipeline  

---

## Key Features
- Fully automated pipeline (single-command execution)  
- QoR optimization (Area, Power, Timing)  
- Post-synthesis equivalence checking  
- Failure-aware repair loops  
- Pareto design exploration  
- QoR visualization (plots and reports)  

---

## Pipeline
Spec → RTL → Simulation → Synthesis → Equivalence → P&R → QoR → Signoff → GDSII  

---

## One-Command Execution

Run the entire pipeline:

```bash
python3 run_all_specs.py

This command:

Executes all designs
Generates QoR reports
Produces plots
Prints final summary
⚙️ Setup Instructions
1. Clone repository
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
Run single design
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

Design specifications are located in:

examples/specs/

Each YAML file defines:

Module behavior
Inputs/outputs
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
📊 Expected Results

After execution:

All designs PASS
RTL generation successful
Simulation passes
OpenROAD completes flow
Timing closure achieved (WNS ≈ 0)
QoR metrics generated
Pareto-optimal designs identified

Workflow
Parse YAML → generate RTL
Run simulation → verify correctness
Perform synthesis (Yosys)
Run OpenROAD (placement, routing, STA)
Extract QoR metrics
Apply optimization loops
Generate reports and plots

Hidden Testcases

To run custom specifications:

python3 run_pipeline.py --spec <your_spec.yaml> --mode full --overwrite

Ensure the YAML format matches the examples.

Limitations
Full DRC/LVS requires complete Sky130 PDK
Open-source tools provide limited optimization compared to commercial tools
Parallel execution may require careful resource handling

Contributions
End-to-end ASIC automation
QoR-driven optimization
Post-synthesis equivalence verification
Failure-aware self-repair pipeline
Pareto-based design exploration
Automated visualization and insights

Authors
Sudarshan Dhandapani
Lakshminarayanaa Rajamanar

Summary

An AI-driven system for automating ASIC design flow with adaptive optimization, verification, and intelligent decision-making.

