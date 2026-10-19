# Usage (from the repo root or any stage directory):  source ../env.csh
# Finds config/local.csh by walking up from the current directory.
set cwd_ = `pwd`
while ( ! -e $cwd_/config/local.csh && "$cwd_" != "" )
    set cwd_ = $cwd_:h
end
if (-e $cwd_/config/local.csh) then
    setenv COURSE_ROOT $cwd_
    source $COURSE_ROOT/config/local.csh
else
    echo "config/local.csh missing: copy config/local.example.csh and fill it in."
endif
unset cwd_
