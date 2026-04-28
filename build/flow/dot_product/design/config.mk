export DESIGN_NAME := dot_product
export TOP_MODULE := dot_product
export PLATFORM := sky130hd
export VERILOG_FILES := /home/sudar762/projects/spec-to-rtl-agent/build/flow/dot_product/design/src/dot_product.v
export SDC_FILE := /home/sudar762/projects/spec-to-rtl-agent/build/flow/dot_product/design/constraint.sdc
export DIE_AREA ?= 0 0 200 200
export CORE_AREA ?= 10 10 190 190

# Synthesis directives: hierarchy -check -top $(DESIGN_NAME), synth -flatten, opt, abc mapping.
export SYNTH_HIERARCHICAL := 0
export SYNTH_ARGS := -top dot_product
export SYNTH_OPT_HIER := 1
export ABC_AREA := 1
export ACTIVITY_FILE = $(RESULTS_DIR)/waves.vcd
export ACTIVITY_SCOPE = tb_$(DESIGN_NAME)/dut
export REPORT_POWER = 1
export PRE_FINAL_REPORT_TCL := /home/sudar762/projects/spec-to-rtl-agent/build/flow/dot_product/design/power_activity.tcl
export CLOCK_PORT := clk
export CLOCK_PERIOD := 10

# This file is intended for OpenROAD-flow-scripts style DESIGN_CONFIG usage.
