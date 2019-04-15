Node_Num=8
Total_Mem=4048288

import subprocess
import sys
import os
import numpy as np
from collections import OrderedDict
import glob

# affinity
command = ['ceph','osd','tree']
p = subprocess.Popen(command,stdout=subprocess.PIPE)
text = p.stdout.read()
retcode = p.wait()

affinity_list = []
#free_list = []
node_list = ["1","2","4","5","6","7","8","9"]
d = dict.fromkeys(node_list, 0)
#print (type(OrderedDict(d)))
n=20
i=0
while n<(20+Node_Num*10) and i<Node_Num:
    affinity_list.insert(i,text.split()[n])
    n=n+10
    i=i+1
affinity_array=np.array(affinity_list)
#print (affinity_array)

#get latest vmstat log file
list_of_files = glob.glob('/home/ceph-user/vmstat_logs/*') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)

#path=sys.argv[1]
##mem_usage
raw_data=subprocess.Popen(['tail','-n','8', latest_file], shell=False, stdout=subprocess.PIPE)
data = raw_data.stdout.read().strip()
#data=os.popen('tail -n 8 /home/ceph-user/vmstat_logs/test').read()
#data=subprocess.call(['tail','-n','8', path])
#free_array = np.empty([8])
mem_usage_list = []
i=0
j=4
my_dict={}
while i < 127 and j < 131:
    node_num=(((data.strip()).split()[i]).split('node')[1].strip(':'))
    mem_free=(int((data.strip()).split()[j]))
    my_dict[node_num]=mem_free
    i=i+18
    j=j+18

#print (my_dict)

for key in sorted(my_dict):
    mem_usage_list.append((1.0-(my_dict[key]/(Total_Mem*1.0))))

mem_usage_array=np.array(mem_usage_list)
#print (mem_usage_array)


##cpu_usage
cpu_usage_list = []
i=0
j=13
k=14
my_dict={}
while i < 127 and j < 141 and k < 142:
    node_num=(((data.strip()).split()[i]).split('node')[1].strip(':'))
    cpu_us=(int((data.strip()).split()[j]))
    cpu_sys=(int((data.strip()).split()[k]))
    my_dict[node_num]=cpu_us+cpu_sys
    i=i+18
    j=j+18
    k=k+18

#print (my_dict)

for key in sorted(my_dict):
    cpu_usage_list.append(my_dict[key]/100.0)

cpu_usage_array=np.array(cpu_usage_list)
#print (cpu_usage_array)

##io_wait
io_wait_list = []
i=0
j=16
my_dict={}
while i < 127 and j < 144:
    node_num=(((data.strip()).split()[i]).split('node')[1].strip(':'))
    io_wa=(int((data.strip()).split()[j]))
    my_dict[node_num]=io_wa
    i=i+18
    j=j+18

#print (my_dict)

for key in sorted(my_dict):
    io_wait_list.append(my_dict[key]/100.0)

io_wait_array=np.array(io_wait_list)
#print (io_wait_array)


obs=np.array([affinity_array,mem_usage_array,cpu_usage_array,io_wait_array])
print (np.transpose(obs))


