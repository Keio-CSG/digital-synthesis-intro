# Formality: is the synthesized netlist logically equivalent to the RTL?
# Run in fm/:  fm_shell -f fm.tcl
set designname MAC4
set corner [expr {[info exists env(CORNER)] ? $env(CORNER) : "wc"}]

# Tell Formality what DC did (retiming/constant propagation hints)
set_svf ../dc/$designname.svf

# reference = RTL
read_verilog -container r -libname WORK -01 [list ../rtl/MAC4_LANE.v ../rtl/$designname.v]
set_top r:/WORK/$designname

# implementation = gate-level netlist (+ std-cell library as black-box models)
read_db -container i [list $env(STD_DB_[string toupper $corner])]
read_verilog -container i -libname WORK -netlist ../dc/$designname.net.v
set_top i:/WORK/$designname

match
report_unmatched_points > unmatched.log
set ok [verify]
report_failing_points > failing.log
report_passing_points > passing.log
if {$ok == 1} { puts "FORMALITY RESULT: PASS" } else { puts "FORMALITY RESULT: FAIL" }
quit
