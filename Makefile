# RTL-to-signoff flow for the MAC4 example.  Needs config/local.csh (see config/local.example.csh).
# Each stage runs in its own directory:  make sim | syn | fm | pnr | rcx | sta | gls | drc | lvs | all
SH = csh -c 'source ../env.csh >& /dev/null; $(1)'

.PHONY: all sim syn fm pnr rcx sta gls drc lvs clean
all: sim syn fm pnr rcx sta gls drc lvs

sim:                       ## 1. RTL simulation
	cd sim  && csh run_rtl.csh
syn:                       ## 2. logic synthesis (DC)
	cd dc   && $(call SH,dc_shell -f dc.tcl >& dc_run.log)
fm:                        ## 3. RTL vs netlist equivalence (Formality)
	cd fm   && $(call SH,fm_shell -f fm.tcl >& fm_run.log) ; grep "FORMALITY RESULT" fm_run.log
pnr:                       ## 4. place, CTS, route (ICC2)
	cd icc2 && $(call SH,icc2_shell -f icc2.tcl >& icc2_run.log < /dev/null)
rcx:                       ## 5. parasitic extraction (StarRC)
	cd rcx  && csh run_starrc.csh
sta:                       ## 6. signoff STA (PrimeTime): setup @ slow, hold @ fast
	cd sta  && $(call SH,env MODE=setup pt_shell -f pt.tcl >& pt_setup.log < /dev/null)
	cd sta  && $(call SH,env MODE=hold  pt_shell -f pt.tcl >& pt_hold.log  < /dev/null)
gls:                       ## 7. gate-level simulation with the signoff SDF
	cd sim  && csh run_gls.csh setup 2.0 && csh run_gls.csh hold 2.0
drc:                       ## 8. physical verification: DRC (Calibre)
	cd verif && csh run_drc.csh
lvs:                       ## 9. physical verification: LVS (Calibre)  -- see docs, open item
	cd verif && csh run_lvs.csh
clean:
	rm -rf sim/xcelium*.d sim/*.cmd sim/*.log sim/*.vcd sim/*.cmd sim/*.history dc/WORK dc/MAC4.* dc/*.log dc/*.svf \
	       fm/*.log fm/FM_WORK fm/*.svf icc2/MAC4* icc2/*.log icc2/*.svf icc2/*_floorplan icc2/crte_* \
	       rcx/star rcx/*.spef rcx/*.log rcx/*.cmd rcx/layer.map sta/*.log sta/*.sdf sta/pt_* verif/drc verif/lvs
