#!/bin/csh -f
# Calibre DRC on the ICC2 GDS.  Run in verif/:  csh run_drc.csh
source ../env.csh >& /dev/null
mkdir -p drc; cd drc          # the deck writes many report files
# Site hook: write MAC4.drc.deck = the foundry DRC deck pointed at ../../icc2/MAC4.gds, top cell MAC4,
# results MAC4.drc.results, summary MAC4.drc.summary.  (Deck internals are site specific.)
csh $COURSE_ROOT/config/prep_drc.csh
calibre -drc -hier -turbo 4 -hyper MAC4.drc.deck >& drc.log
# list failing rules, skipping the ones that only make sense for a full chip (DRC_IGNORE)
grep -E "RULECHECK .*Result Count" MAC4.drc.summary | grep -v "Count = 0 " | grep -v "RULECHECK $DRC_IGNORE" | tee drc.nonzero.txt
echo "rules failing (excluding chip-level rules): `wc -l < drc.nonzero.txt`"
