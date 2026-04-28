#Edge: BOTTOM
#Edge: RIGHT
place_pin -pin_name rst_n -layer met3 -location {199.6 96.9} -force_to_die_boundary
place_pin -pin_name shreg[2] -layer met3 -location {199.6 98.26} -force_to_die_boundary
place_pin -pin_name shreg[3] -layer met3 -location {199.6 99.62} -force_to_die_boundary
#Edge: TOP
#Edge: LEFT
place_pin -pin_name clk -layer met3 -location {0.4 96.9} -force_to_die_boundary
place_pin -pin_name en -layer met3 -location {0.4 98.26} -force_to_die_boundary
place_pin -pin_name serial_in -layer met3 -location {0.4 100.98} -force_to_die_boundary
place_pin -pin_name shreg[0] -layer met3 -location {0.4 99.62} -force_to_die_boundary
place_pin -pin_name shreg[1] -layer met3 -location {0.4 95.54} -force_to_die_boundary
