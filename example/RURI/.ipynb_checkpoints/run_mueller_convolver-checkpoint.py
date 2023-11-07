import numpy as np
import subprocess
import sys
import os 

#==================== You should modify here ====================#
jss_account = "n339"
user_email  = "nagano_y@s.okayama-u.ac.jp"
coderoot    = f"/home/{jss_account[0]}/{jss_account}/data/e2e_sim/scripts"
conda_base  = f"/ssd/{jss_account[0]}/{jss_account}/.src/anaconda3/etc/profile.d/conda.sh"
#================================================================#
lbsim_code  = "test_mueller_convolver.py"
job_name    = "test_mueller_convolver"
bizcode     = "DU10503"
vnode       = 1
vnode_core  = 36   # Maxmum of the RURI: 36 cores
vnode_mem   = 50   # Unit: GiB
mode        = "debug" 
#mode        = "default" 
jobscript   = coderoot + "/" + "run_"+job_name+".pjm"

elapse      = "00:50:00" # When you use the `debug` mode you should requesgt <= 1800 == "00:30:00"
if mode == "debug":
    elapse  = "00:10:00"
    
nthreads = 0 # Controlling threads parallelisation in the Mueller convolver, At =0 it is the maximum number of threads possible

script_contents = """#!/bin/zsh
#JX --bizcode {bizcode}
#JX -L rscunit=RURI
#JX -L rscgrp={mode}
#JX -L elapse={elapse}
#JX -L vnode={vnode}
#JX -L vnode-core={vnode_core}
#JX -L vnode-mem={vnode_mem}Gi

#JX -o {coderoot}/log/%n_%j.out
#JX -e {coderoot}/log/%n_%j.err
#JX --spath {coderoot}/log/%n_%j.stats
#JX -N {job_name}
#JX -m e
#JX --mail-list {user_email}
#JX -S
#export OMP_NUM_THREADS=1

module load intel
source {conda_base}
conda activate lbs_env

cd {coderoot}
python {lbsim_code} {nthreads} {vnode} {vnode_core} {vnode_mem}
"""

script_contents = script_contents.format(**locals())
f = open(jobscript, "wt")
f.write(script_contents)
f.close()

process = subprocess.Popen("jxsub "+jobscript, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(stdout_data, stderr_data) = process.communicate()

#print useful information
print("out: "+str(stdout_data).split('b\'')[1][:-3])
print("err: "+str(stderr_data).split('b\'')[1][:-3])
print('')
os.remove(jobscript)