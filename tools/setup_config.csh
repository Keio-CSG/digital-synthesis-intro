#!/bin/csh -f
# Copy the lab's ready-made config files into config/.
#   csh tools/setup_config.csh <folder given by your supervisor or a senior student>
# Existing files in config/ are kept (a .bak copy is made first).
if ($#argv != 1) then
    echo "usage: csh tools/setup_config.csh <config folder>"
    exit 1
endif
set src = $argv[1]
set root = $0:h:h
if ("$root" == "$0:h" || "$root" == "") set root = .
foreach f (local.csh tech.tcl starrc_layer.map prep_drc.csh prep_lvs.csh render.json)
    if (! -e $src/$f) then
        echo "missing in $src: $f"
        exit 1
    endif
end
foreach f (local.csh tech.tcl starrc_layer.map prep_drc.csh prep_lvs.csh render.json)
    if (-e $root/config/$f) cp $root/config/$f $root/config/$f.bak
    cp $src/$f $root/config/$f
    echo "config/$f"
end
echo "done. try:  make sim"
