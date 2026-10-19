#!/bin/csh -f
# RTL simulation with Xcelium.  Run from sim/:  csh run_rtl.csh
source ../env.csh >& /dev/null
rm -rf xcelium.d
xrun -64bit -timescale 1ns/1ps -access +r -define DUMP ../rtl/MAC4_LANE.v ../rtl/MAC4.v ../tb/tb_MAC4.v -l rtl.log -xmlibdirname xcelium.d
grep -E "PASS|FAIL|MISMATCH" rtl.log
