# PrimeTime signoff STA.  Run in sta/:  env MODE=setup|hold pt_shell -f pt.tcl
#   setup : slow corner (late data, early clock)    -> can the logic finish in one cycle?
#   hold  : fast corner (early data, late clock)    -> does data change too soon after the edge?
set mode [expr {[info exists env(MODE)] ? $env(MODE) : "setup"}]
set db   [expr {$mode eq "setup" ? $env(STD_DB_WC) : $env(STD_DB_BC)}]
set designname MAC4

set link_path [list "*" $db]
set target_library [list $db]
read_verilog ../icc2/$designname.icc2.nopg.v
current_design $designname
link_design

# same constraints as synthesis and P&R
source ../const/$designname.sdc

# real wire RC from StarRC
read_parasitics ../rcx/$designname.spef
report_annotated_parasitics -check > $mode.annotated.log

# clock is now propagated through the real tree (DC/ICC2 pre-CTS used an ideal clock)
set_propagated_clock [all_clocks]

update_timing -full
check_timing -verbose                         > $mode.check_timing.log
report_global_timing                          > $mode.global.log
report_constraint -all_violators              > $mode.violators.log
report_timing -delay_type max -max_paths 5 -slack_lesser_than 1000 -nosplit -input_pins > $mode.max.log
report_timing -delay_type min -max_paths 5 -slack_lesser_than 1000 -nosplit -input_pins > $mode.min.log
report_clock_timing -type skew -nosplit > $mode.skew.log
report_analysis_coverage                      > $mode.coverage.log

# write SDF for gate-level simulation
write_sdf -significant_digits 4 $designname.$mode.sdf
quit
