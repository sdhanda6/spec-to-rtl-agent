export DESIGN_NAME := text_counter
export TOP_MODULE := text_counter
export PLATFORM := sky130hd
export VERILOG_FILES := /home/sudar762/projects/spec-to-rtl-agent/build/flow/text_counter/design/src/text_counter.v
export SDC_FILE := /home/sudar762/projects/spec-to-rtl-agent/build/flow/text_counter/design/constraint.sdc
export DIE_AREA := 0 0 200 200
export CORE_AREA := 10 10 190 190
export SYNTH_HIERARCHICAL := 0
export SYNTH_ARGS := -top text_counter
export SYNTH_OPT_HIER := 1
export ABC_AREA := 1
export ACTIVITY_FILE = $(RESULTS_DIR)/waves.vcd
export ACTIVITY_SCOPE := tb_$(DESIGN_NAME)/dut
export REPORT_POWER := 1
export PRE_FINAL_REPORT_TCL := /home/sudar762/projects/spec-to-rtl-agent/build/flow/text_counter/design/power_activity.tcl
export CLOCK_PORT := clk
export CLOCK_PERIOD := 10
export SYNTH_SIZING := 0
export SYNTH_BUFFERING := 0
export MAX_FANOUT_CONSTRAINT := 16

# Auto-generated QoR tuning config.
