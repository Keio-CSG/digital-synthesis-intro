#!/bin/csh -f
# Calibre LVS: layout (GDS) vs. the netlist written by ICC2.  Run in verif/:  csh run_lvs.csh
source ../env.csh >& /dev/null
mkdir -p lvs; cd lvs
# Site hook: from ../../icc2/MAC4.icc2.lvs.v and MAC4.gds produce
#   MAC4.src.sp   (SPICE source netlist)   and   MAC4.lvs.deck  (the foundry LVS deck, patched)
csh $COURSE_ROOT/config/prep_lvs.csh
calibre -lvs -hier -turbo 4 -hyper -spice MAC4.lvs.sp MAC4.lvs.deck >& lvs.log
grep -E "CORRECT|INCORRECT" MAC4.lvs.report | head -3
