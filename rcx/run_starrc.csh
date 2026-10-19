#!/bin/csh -f
# Parasitic extraction with StarRC from the ICC2 layout.  Run in rcx/:  csh run_starrc.csh
# Writes starrc.cmd from environment variables (config/local.csh), then runs StarXtract.
source ../env.csh >& /dev/null
rm -rf star
# layer mapping: layout database layer names -> technology layer names (site file)
cp $COURSE_ROOT/config/starrc_layer.map layer.map
cat > starrc.cmd <<CMD
BLOCK: MAC4/write_data
NDM_DATABASE: ../icc2/MAC4.ndm
TCAD_GRD_FILE: $STARRC_NXTGRD_MAX
MAPPING_FILE: ./layer.map
EXTRACTION: RC
COUPLE_TO_GROUND: NO
POWER_NETS: VDD VSS
REDUCTION: NO_EXTRA_LOOPS
NETLIST_FORMAT: SPEF
NETLIST_FILE: MAC4.spef
NETLIST_CONNECT_SECTION: YES
SKIP_CELLS: !*
CASE_SENSITIVE: NO
STAR_DIRECTORY: ./star
CMD
StarXtract starrc.cmd >& starrc.log
grep -E "ERROR|Error|SPEF|spef" starrc.log | head
ls -l MAC4.spef*
