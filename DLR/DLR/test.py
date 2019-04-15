import subprocess
#answer = subprocess.check_output(['./get_cosbench_jobID.sh'])
#url='http://129.114.33.85:19088/controller/workload.html?id='+answer
#print (url.strip())


import glob
import os

list_of_files = glob.glob('/home/ceph-user/vmstat_logs/*') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
#print (latest_file.split("/")[4])

raw_data=subprocess.Popen(['tail','-n','8', latest_file], shell=False, stdout=subprocess.PIPE)
data = raw_data.stdout.read().strip()


print data
