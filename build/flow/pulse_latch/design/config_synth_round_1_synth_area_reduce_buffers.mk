export DESIGN_NAME := pulse_latch
export TOP_MODULE := pulse_latch
export PLATFORM := sky130hd
export VERILOG_FILES := /home/sudar762/projects/spec-to-rtl-agent/build/flow/pulse_latch/design/src/pulse_latch.v
export SDC_FILE := /home/sudar762/projects/spec-to-rtl-agent/build/flow/pulse_latch/design/constraint.sdc
export DIE_AREA := 0 0 200 200
export CORE_AREA := 10 10 190 190
export SYNTH_HIERARCHICAL := 0
export SYNTH_ARGS := -top pulse_latch
export SYNTH_OPT_HIER := 1
export ABC_AREA := 1
export ACTIVITY_FILE = $(RESULTS_DIR)/waves.vcd
export ACTIVITY_SCOPE := tb_$(DESIGN_NAME)/dut
export REPORT_POWER := 1
export PRE_FINAL_REPORT_TCL := /home/sudar762/projects/spec-to-rtl-agent/build/flow/pulse_latch/design/power_activity.tcl
export CLOCK_PORT := clk
export CLOCK_PERIOD := 10
export SYNTH_SIZING := 0
export SYNTH_BUFFERING := 0
export MAX_FANOUT_CONSTRAINT := 16

# Auto-generated QoR tuning config.
