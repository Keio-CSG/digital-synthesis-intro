# SDC for MAC4 -- shared by DC, ICC2, PrimeTime. Units: ns / pF.
set CLK_PERIOD 2.0

create_clock -name clk -period $CLK_PERIOD [get_ports clk]
set_clock_uncertainty -setup 0.15 [get_clocks clk]  ;# skew + jitter margin
set_clock_uncertainty -hold  0.05 [get_clocks clk]
set_clock_transition  0.1  [get_clocks clk]

set in_ports [remove_from_collection [all_inputs] [get_ports {clk rst_n}]]
set_input_delay  0.6 -clock clk $in_ports         ;# data arrives 0.6 ns after clk edge
set_output_delay 0.6 -clock clk [all_outputs]     ;# next block needs 0.6 ns setup

set_input_transition 0.1  $in_ports
set_load             0.05 [all_outputs]

# rst_n is asynchronous and de-asserted by the board: not timed against clk
set_false_path -from [get_ports rst_n]
