export DESIGN_NICKNAME = iclad_seq_detector
export DESIGN_NAME = seq_detector_0011
export PLATFORM    = sky130hd

export VERILOG_FILES = $(sort $(wildcard $(DESIGN_HOME)/src/$(DESIGN_NICKNAME)/*.v))
export SDC_FILE      = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/constraint.sdc

export PLACE_PINS_ARGS = -min_distance 4 -min_distance_in_tracks

export CORE_UTILIZATION = 15
export CORE_ASPECT_RATIO = 1
export CORE_MARGIN = 4

export PLACE_DENSITY = 0.6
