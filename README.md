# 🚀 Spec-to-Tapeout AI Agent  
### End-to-End RTL-to-GDSII ASIC Design Automation with QoR Optimization

---

## 📌 Overview
This project implements an AI-driven Spec-to-Tapeout agent that converts high-level design specifications into manufacturable GDSII layouts.

The system automates the complete ASIC design flow:
- RTL generation  
- Functional verification  
- Synthesis optimization  
- Physical design (OpenROAD)  
- QoR optimization  
- Post-synthesis equivalence checking  
- Signoff-aware validation  

---

## 🧠 Key Features

### 🔹 Spec → RTL Automation
- Parses YAML-based specifications  
- Generates synthesizable Verilog RTL  
- Auto-generates SystemVerilog testbenches  

---

### 🔹 Functional Verification
- RTL simulation using Icarus Verilog  
- Oracle-based validation  
- Automatic repair loop  

---

### 🔹 Synthesis Optimization 🚀
- Iterative synthesis tuning (Yosys/OpenROAD)  
- Explores multiple configurations:
  - timing-driven  
  - area-driven  
  - power-aware  
- Selects best gate-level netlist  

---

### 🔹 Post-Synthesis Equivalence Checking
- Verifies:
  RTL behavior == synthesized netlist behavior  
- Detects:
  - reset mismatches  
  - wrapper/testbench issues  
  - synthesis inconsistencies  
- Auto-repair and retry  

---

### 🔹 Physical Design (OpenROAD)
- Floorplanning  
- Placement  
- CTS  
- Routing  
- GDSII generation  

---

### 🔹 QoR Optimization
Optimizes:
- WNS / TNS  
- Setup / Hold violations  
- Congestion  
- Area  
- Power  

---

### 🔹 Signoff-Aware Flow
- Magic (DRC)  
- Netgen (LVS)  
- Graceful handling of missing PDK  

---

### 🔹 Robust Failure Handling
- Distinguishes:
  - infra_failure  
  - logical_failure  
  - partial  
- Prevents false mismatch classification  

---

## 🏗️ Pipeline

Spec → RTL → Simulation → Synthesis → Equivalence → P&R → QoR → Signoff → GDS

---

## ⚙️ Installation

git clone https://github.com/sdhanda6/spec-to-rtl-agent.git  
cd spec-to-rtl-agent  
pip install -r requirements.txt  

---

## ▶️ Usage

python3 run_pipeline.py --spec examples/specs/p1.yaml --mode full --overwrite  

Advanced:

python3 run_pipeline.py \
  --spec examples/specs/p1.yaml \
  --mode full \
  --overwrite \
  --optimize-synth \
  --optimize-qor \
  --verify-post-synth \
  --run-signoff  

---

## 📊 Outputs
- RTL → rtl/  
- Testbench → tb/  
- Reports → build/reports/  
- Logs → build/flow/  
- GDS → OpenROAD results  

---

## 📈 Results
- RTL verified ✔  
- Post-synth equivalence ✔  
- GDS generated ✔  
- QoR loop validated ✔  

---

## ⚠️ Limitations
- Full DRC/LVS needs complete Sky130 PDK  
- Small designs show limited QoR improvement  

---

## 🎯 Contributions
- End-to-end ASIC automation  
- Synthesis + QoR optimization loops  
- Equivalence checking  
- Signoff-aware pipeline  

---

## 🧑‍💻 Author
Sudarshan (sdhanda6)

---

## ⭐ Summary
AI-driven Spec-to-GDSII automation system with iterative optimization, verification, and signoff awareness.
