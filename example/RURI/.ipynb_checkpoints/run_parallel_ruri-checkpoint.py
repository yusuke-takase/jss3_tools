import numpy as np
import subprocess
import sys
import os 

#==================== You should modify here ====================#
jss_account = "t541"
user_email  = "takase_y@s.okayama-u.ac.jp"
coderoot    = f"/home/{jss_account[0]}/{jss_account}/data/jss3_tools/example/RURI"
conda_base  = f"/ssd/{jss_account[0]}/{jss_account}/.src/anaconda3/etc/profile.d/conda.sh"
#================================================================#
lbsim_code  = "get_hitmap_parallel_ruri.py"
job_name    = "get_hitmap_parallel_ruri"
bizcode     = "DU10503"
vnode       = 1
vnode_core  = 2   # Maxmum of the RURI: 36 cores
vnode_mem   = 8   # Unit: GiB
mode        = "debug" 
jobscript   = coderoot + "/" + "run_"+job_name+".pjm"

elapse      = "00:01:00" # When you use the `debug` mode you should requesgt <= 1800 == "00:30:00"
if mode == "debug":
    elapse  = "00:10:00"


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
mpiexec -n {vnode_core} python {lbsim_code}
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
