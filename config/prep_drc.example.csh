#!/bin/csh -f
# Copy to config/prep_drc.csh and implement for your site (git-ignored).
# Runs inside verif/drc/ with the variables of config/local.csh set.
# It must create: MAC4.drc.deck
# Inputs: ../../icc2/MAC4.gds
# Typical steps: copy the foundry rule deck, point it at the layout/top cell, set result file names.
