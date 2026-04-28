#Edge: BOTTOM
#Edge: RIGHT
place_pin -pin_name rst_n -layer met3 -location {199.6 96.9} -force_to_die_boundary
place_pin -pin_name start -layer met3 -location {199.6 99.62} -force_to_die_boundary
place_pin -pin_name valid -layer met3 -location {199.6 98.26} -force_to_die_boundary
#Edge: TOP
#Edge: LEFT
place_pin -pin_name busy -layer met3 -location {0.4 96.9} -force_to_die_boundary
place_pin -pin_name clk -layer met3 -location {0.4 99.62} -force_to_die_boundary
place_pin -pin_name done -layer met3 -location {0.4 98.26} -force_to_die_boundary
