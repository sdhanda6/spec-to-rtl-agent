# 🚀 Spec-to-Tapeout AI Agent  
### End-to-End RTL-to-GDSII ASIC Design Automation with QoR Optimization

---

## 📌 Overview
## 🎯 What Makes This Project Unique

- AI-driven design optimization  
- Pareto tradeoff analysis  
- Self-explaining agent decisions  
- Fully automated RTL → GDS pipeline  
This project implements an AI-driven Spec-to-Tapeout agent that converts high-level design specifications into manufacturable GDSII layouts.

The system automates the full ASIC flow:
Spec → RTL → Simulation → Synthesis → OpenROAD → QoR → Signoff → GDSII

---

## 🧠 Key Features
- Fully automated pipeline (single command execution)  
- QoR optimization (Area, Power, Timing)  
- Post-synthesis equivalence checking  
- Failure-aware repair loops  
- Pareto design exploration  
- QoR visualization (plots + reports)  

---

## 🏗️ Pipeline
Spec → RTL → Simulation → Synthesis → Equivalence → P&R → QoR → Signoff → GDS  

---

## ⚙️ Setup Instructions (IMPORTANT)

### 1. Clone repository
```bash
git clone https://github.com/sdhanda6/spec-to-rtl-agent.git
cd spec-to-rtl-agent

## ⚡ Quick Start (Recommended)

Run the entire pipeline with a single command:

```bash
python3 run_all_specs.py


---

# 🔴 3. Add “Sample Output”

### 📍 Insert **AFTER** this section:
## ✅ Sample Output

After execution, you should observe:

- FINAL SUMMARY → all designs PASS  
- QoR SUMMARY TABLE → WNS ≈ 0  
- Generated plots in `build/plots/`

Example:

Design | Area | Power | WNS  

```text
## 📊 Expected Results

## 🧪 Hidden Testcases

To run custom/hidden specifications:

```bash
python3 run_pipeline.py --spec <your_spec.yaml> --mode full --overwrite


---

# 🔴 5. Add Environment Fix (VERY IMPORTANT)

### 📍 Insert **AFTER** this section:

```text
## ⚙️ Setup Instructions
## ⚠️ Environment Note

If `venv` fails, use:

```bash
pip install --user virtualenv
export PATH=$HOME/.local/bin:$PATH
virtualenv venv
source venv/bin/activate

---

