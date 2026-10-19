# Copy to config/local.csh and fill in for YOUR site. local.csh is git-ignored.
# --- tool setup: load the EDA tools in whatever way your site does it ---
# source <site scripts that put dc_shell, icc2_shell, fm_shell, pt_shell,
#         StarXtract, calibre, v2lvs and xrun on PATH>

# --- technology files supplied by your foundry/library vendor ---
setenv STD_DB_WC     <path to slow-corner  .db>     # setup signoff corner
setenv STD_DB_TC     <path to typical      .db>
setenv STD_DB_BC     <path to fast-corner  .db>     # hold  signoff corner
setenv STD_NDM       <path to std-cell reference NDM>
setenv STD_LIBNAME   <library name inside the NDM>
setenv TECH_FILE     <ICC2 technology file>
setenv TLUP_TYP      <TLU+ typical>
setenv TLUP_CMAX     <TLU+ cworst>
setenv TLUP_CMIN     <TLU+ cbest>
setenv LAYER_MAP     <TLU+ layer map>
setenv GDS_LAYER_MAP <ICC2 -> GDS layer map>
setenv STD_GDS       <std-cell GDS>
setenv STD_CDL       <std-cell SPICE/CDL>
setenv FILLER_CELLS  "<space-separated filler cell names, big to small>"
setenv DRC_DECK      <Calibre DRC rule file>
setenv LVS_DECK      <Calibre LVS rule file>
setenv STARRC_NXTGRD_MAX <StarRC nxtgrd (technology) file>
setenv LVS_DEFINES   "<#DEFINE switches the LVS deck needs for your std-cell library, space separated>"
setenv STD_VERILOG   <std-cell Verilog simulation models>
setenv DRC_IGNORE    '<regex of chip-level-only rule names to hide in the DRC summary>'
