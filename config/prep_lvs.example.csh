#!/bin/csh -f
# Copy to config/prep_lvs.csh and implement for your site (git-ignored).
# Runs inside verif/lvs/ with the variables of config/local.csh set.
# It must create: MAC4.src.sp and MAC4.lvs.deck
# Inputs: ../../icc2/MAC4.gds and ../../icc2/MAC4.icc2.lvs.v
# Typical steps: copy the foundry rule deck, point it at the layout/top cell, set result file names.
