export DESIGN_NAME := fir_filter
export PLATFORM := sky130hd
export VERILOG_FILES := /home/sudar762/projects/spec-to-rtl-agent/build/flow/fir_filter/design/src/fir_filter.v
export SDC_FILE := /home/sudar762/projects/spec-to-rtl-agent/build/flow/fir_filter/design/constraint.sdc
export DIE_AREA ?= 0 0 200 200
export CORE_AREA ?= 10 10 190 190
export CLOCK_PORT := clk
export CLOCK_PERIOD := 8

# This file is intended for OpenROAD-flow-scripts style DESIGN_CONFIG usage.
