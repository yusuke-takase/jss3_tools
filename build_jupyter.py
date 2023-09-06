""" This function starts a jupyter server on RURI based on the prepared singularity environment, and outputs standard ssh commands required for port forwarding in combination with the assigned node ID and the specified port.
"""
import subprocess
import sys
import time
import re
import os

bizcode     = "DU10503"
jss_account = "t541"
vnode       = 1
vnode_core  = 1
vnode_mem   = 24          # unit: GiB
elapse      = "12:00:00"   # hh:mm:ss
jobname     = "jupyter"
port        = "7123" 

pjm = """#!/bin/zsh
#JX --bizcode {bizcode}
#JX -L rscunit=RURI
#JX -L vnode={vnode}
#JX -L vnode-core={vnode_core}
#JX -L vnode-mem={vnode_mem}Gi
#JX -L elapse={elapse}
#JX -L jobenv=singularity
#JX -o /data/{jss_account[0]}/{jss_account}/.log/jupyter/%n_%j.out
#JX -e /data/{jss_account[0]}/{jss_account}/.log/jupyter/%n_%j.err
#JX --spath /data/{jss_account[0]}/{jss_account}/.log/%n_%j.stats
#JX -N {jobname}
#JX -S

cd /home/{jss_account[0]}/{jss_account}
module load singularity
singularity run /data/{jss_account[0]}/{jss_account}/.src/singularity/ubuntu_20.04_jupyter_edit.sif jupyter lab --ip=0.0.0.0 --no-browser"""


base_path = f"/data/{jss_account[0]}/{jss_account}/.log"
if not os.path.exists(base_path):
    os.makedirs(base_path)
    if not os.path.exists(base_path+"/jupyter"):
        os.makedirs(base_path+"/jupyter")

pjm         = pjm.format(**locals())
jobscript   = f"/home/{jss_account[0]}/{jss_account}/.jupyter/pjm_jupyter.sh"
f           = open(jobscript, "wt")
f.write(pjm)
f.close()

process = subprocess.Popen("jxsub "+jobscript, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(stdout_data, stderr_data) = process.communicate()
print("\033[1mThe job-script to build the jupyter was submitted:\033[0m")
print(stdout_data.decode('utf-8'))

# Extract job IDs using regular expressions
job_id  = re.search(r'Job (\d+)', stdout_data.decode('utf-8')).group(1)

# Run jxstat command and replace <jobid> to get results
status  = subprocess.check_output(["jxstat", "-S", job_id]).decode().strip()
# Pick up NODE ID
matches = re.findall(r'^.*NODE ID.*$', status, re.MULTILINE)
match   = re.search(r':\s*([a-zA-Z0-9]+)$', matches[-1])
i       = 0
print("[Try {}] NODE ID: {}".format(i, match))
while match is None:
	i += 1
	time.sleep(0.5)
	status  = subprocess.check_output(["jxstat", "-S", job_id]).decode().strip()
	matches = re.findall(r'^.*NODE ID.*$', status, re.MULTILINE)
	match   = re.search(r':\s*([a-zA-Z0-9]+)$', matches[-1])
	print("[Try {}] NODE ID: {}".format(i, match))

node_id = match.group(1)
sshcmd  = f"ssh toki -L {port}:{node_id}.jss.in-jaxa:{port}"
print("\033[1mReconnect by:\033[0m")
print(sshcmd)

os.remove(jobscript)
