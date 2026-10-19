#!/bin/csh -f
# Gate-level simulation with the post-layout SDF from PrimeTime.
#   csh run_gls.csh setup 2.0    slow-corner delays, clock period 2.0 ns
#   csh run_gls.csh hold  2.0    fast-corner delays
# Defaults: setup 10.0
source ../env.csh >& /dev/null
set mode = setup; set per = 10.0
if ($#argv >= 1) set mode = $argv[1]
if ($#argv >= 2) set per  = $argv[2]
set half = `echo "$per / 2" | bc -l`
rm -rf xcelium_gls.d
# SDF command file: back-annotate the DUT with the chosen delays
cat > sdf_$mode.cmd <<CMD
SDF_FILE = "../sta/MAC4.$mode.sdf",
SCOPE = tb_MAC4.dut,
MTM_CONTROL = "MAXIMUM",
LOG_FILE = "sdf_$mode.log";
CMD
xrun -64bit -timescale 1ns/1ps -access +r \
     ../icc2/MAC4.icc2.nopg.v $STD_VERILOG ../tb/tb_MAC4.v \
     -xmlibdirname xcelium_gls.d -sdf_cmd_file sdf_$mode.cmd +HALF=$half -l gls_${mode}_$per.log
grep -E "PASS|FAIL|MISMATCH|SDF.*(ERROR|WARN)" gls_${mode}_$per.log | head -5
