export DESIGN_NAME := sum_stage
export PLATFORM := sky130hd
export VERILOG_FILES := /home/sudar762/projects/spec-to-rtl-agent/build/flow/sum_stage/design/src/sum_stage.v
export SDC_FILE := /home/sudar762/projects/spec-to-rtl-agent/build/flow/sum_stage/design/constraint.sdc
export DIE_AREA ?= 0 0 200 200
export CORE_AREA ?= 10 10 190 190
export CLOCK_PORT := clk
export CLOCK_PERIOD := 10.0

# This file is intended for OpenROAD-flow-scripts style DESIGN_CONFIG usage.
