import numpy as np
import subprocess
import sys
import os 

#==================== You should modify here ====================#
jss_account   = "t541"
user_email    = "takase_y@s.okayama-u.ac.jp"
coderoot      = f"/home/{jss_account[0]}/{jss_account}/data/jss3_tools/example/SORA"
venv_base     = f"/ssd/{jss_account[0]}/{jss_account}/.src/lbs_sora/bin/activate"
#================================================================#
codename      = "get_hitmap_parallel_sora.py"
job_name      = "get_hitmap_parallel_sora"
bizcode       = "DU10503"
resource_unit = "SORA"
node          = 1
node_mem      = 28   # Unit: GiB, Upper limit=28GiB, Value when unspecified=28GiB
mpi_process   = 48   # Upper limit of number of process per node is 48
mode          = "debug" 

jobscript     = coderoot+"/"+"run_"+job_name+".pjm"

elapse        = "00:01:00" # When you use the `debug` mode you should requesgt <= 1800 == "00:30:00"
if mode == "debug":
    elapse    = "00:10:00"


script_contents = """#!/bin/zsh
#JX --bizcode {bizcode}
#JX -L rscunit={resource_unit}
#JX -L rscgrp={mode}
#JX -L elapse={elapse}
#JX -L node={node}
#JX -L node-mem={node_mem}Gi
#JX --mpi proc={mpi_process}
#JX -o {coderoot}/log/%n_%j.out
#JX -e {coderoot}/log/%n_%j.err
#JX --spath {coderoot}/log/%n_%j.stats
#JX -N {job_name}
#JX -m e
#JX --mail-list {user_email}
#JX -S
export OMP_NUM_THREADS=1

module purge
module load fjmpi-gcc/8.3.1
module load /opt/JX/modulefiles/aarch64/python/3.9.1
export LD_PRELOAD=/usr/lib/FJSVtcs/ple/lib64/libpmix.so

source {venv_base}
cd {coderoot}
mpiexec -n {mpi_process} python {codename}
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
