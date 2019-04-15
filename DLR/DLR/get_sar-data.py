from subprocess import Popen, PIPE
import re
import sys
import os
import numpy as np
from collections import OrderedDict
import glob

sarstat_log_dir = '/home/ceph-user/sar-logs/'
list_of_files = glob.glob(sarstat_log_dir + '/*')
latest_file = max(list_of_files, key=os.path.getctime) 


raw_data = Popen(['tail', '-n', '80', latest_file],shell=False, stdout=PIPE)
data = raw_data.stdout.read().strip()
data= str(data)
#cpu+io
exp1 = r'(node[1-9]):( )+[0-9][0-9]:[0-9][0-9]:[0-9][0-9]( )+[AP][M]( )+[a][l][l]( )+(\d+\.\d+)( )+(\d+\.\d+)( )+(\d+\.\d+)( )+(\d+\.\d+)( )+(\d+\.\d+)( )+(\d+\.\d+)'
finds1 = re.findall(exp1, data)

new_data1 = []
for f in finds1:
    dat1 = []
    number1 = 0
    for d in f:
        if d.startswith('node'):
            number1 = d[-1]
        elif d != ' ':
            dat1.append(d)

    new_data1.append((number1, dat1))
new_data1 = sorted(new_data1, key=lambda t: t[0])

cpu_usage_list = []
io_wait_list = []

for k, v in new_data1:
    cpu1 = float(v[0])
    cpu2 = float(v[2])
    io = float(v[3])

    cpu_usage_list.append((cpu1 + cpu2)/100)
    io_wait_list.append(io/100)

cpu_usage_array = np.array(cpu_usage_list)
io_wait_array = np.array(io_wait_list)

#index_list=[]
#i=9
#while (i<=79):
#    index_list.append(i)
#    i=i+10

#print (index_list)

#for i in range (0,79):
#    if(i in index_list):
#        print (io_wait_list[i])
#        print ('\n')
#    else:
#        print (io_wait_list[i])
#print (cpu_usage_array)
#print (io_wait_list)


#mem
exp2= r'(node[1-9]):( )+[0-9][0-9]:[0-9][0-9]:[0-9][0-9]( )+[AP][M]( )+(\d+)( )+(\d+)( )+(\d+\.\d+)( )+(\d+)( )+(\d+)( )+(\d+)( )+(\d+\.\d+)( )+(\d+)( )+(\d+)( )+(\d+)'
finds2 = re.findall(exp2, data)
#print (finds)
new_data2 = []
for f in finds2:
    dat2 = []
    number2 = 0
    for d in f:
        if d.startswith('node'):
            number2 = d[-1]
        elif d != ' ':
            dat2.append(d)

    new_data2.append((number2, dat2))
new_data2 = sorted(new_data2, key=lambda t: t[0])

mem_usage_list = []

for k, v in new_data2:
    mem = float(v[6])
    mem_usage_list.append(mem/100)
    
#mem_usage_array = np.array(mem_usage_list)
#index_list=[]
#i=9
#while (i<=79):
#    index_list.append(i)
#    i=i+10
#
##print (index_list)
#
#for i in range (0,80):
#    if(i in index_list):
#        print (mem_usage_list[i])
#        print ('\n')
#    else:
#        print (mem_usage_list[i])
#print (mem_usage_array)

#net
exp3= r'(node[1-9]):( )+[0-9][0-9]:[0-9][0-9]:[0-9][0-9]( )+[AP][M]( )+[e][t][h][0]( )+(\d+\.\d+)( )+(\d+\.\d+)( )+(\d+\.\d+)( )+(\d+\.\d+)( )+(\d+\.\d+)( )+(\d+\.\d+)( )+(\d+\.\d+)( )+(\d+\.\d+)'
finds3 = re.findall(exp3, data)
#print (finds3)
new_data3 = []
for f in finds3:
    dat3 = []
    number3 = 0
    for d in f:
        if d.startswith('node'):
            number3 = d[-1]
        elif d != ' ':
            dat3.append(d)

    new_data3.append((number3, dat3))
new_data3 = sorted(new_data3, key=lambda t: t[0])

net_usage_list = []
total_net = 458752 #KB, assuming maximum network bandwidth = 3.5Gbps = 458752KBps or 19200 KB if we assume max network bandwidth = 150Mbps (50 threads in iperf)
for k, v in new_data3:
    rxkb = float(v[2])
    txkb = float(v[3])
    #print (rxkb, txkb)
    net = rxkb/total_net if rxkb > txkb else txkb/total_net
    net_usage_list.append(net)
print (net_usage_list)
#net_usage_array = np.array(net_usage_list)
#print (len(net_usage_list))
#index_list=[]
#i=9
#while (i<=79):
#    index_list.append(i)
#    i=i+10
#
##print (index_list)
#    
#for i in range (0,80):
#    if(i in index_list):
#        print (net_usage_list[i])
#        print ('\n')
#    else:
#        print (net_usage_list[i])   
#
##net
#sum_usage = 0.0
#avg_usage = 0.0
#for i in range (0,8):
#    sum_usage = sum_usage + net_usage_list[i]
#
#avg_usage = sum_usage / 8.0;
#print (avg_usage)
#
#delta = []
#for i in range (0,8):
#    delta.append((net_usage_list[i]-avg_usage)/net_usage_list[i])
#
#print (delta)
#cpu
sum_usage = 0.0
avg_usage = 0.0
for i in range (0,8):
    sum_usage = sum_usage + cpu_usage_list[i]

avg_usage = sum_usage / 8.0;
#print (avg_usage)

delta = []
for i in range (0,8):
    delta.append((cpu_usage_list[i]-avg_usage)/cpu_usage_list[i])

#print (delta)

##mem
#sum_usage = 0.0
#avg_usage = 0.0
#for i in range (0,8):
#    sum_usage = sum_usage + mem_usage_list[i]
#
#avg_usage = sum_usage / 8.0;
#print (avg_usage)
#
#delta = []
#for i in range (0,8):
#    delta.append((mem_usage_list[i]-avg_usage)/mem_usage_list[i])
#
#print (delta)

##io
#sum_usage = 0.0
#avg_usage = 0.0
#for i in range (0,8):
#    sum_usage = sum_usage + io_wait_list[i]
#
#avg_usage = sum_usage / 8.0;
#print (avg_usage)
#
#delta = []
#for i in range (0,8):
#    delta.append((io_wait_list[i]-avg_usage)/io_wait_list[i])
#
#print (delta)
#

#get_current affinity
node_num = 8
command = ['ceph', 'osd', 'tree']
p = Popen(command, stdout=PIPE)
text = p.stdout.read()
p.communicate()
p.wait()
affinity_list = []
n = 20
i = 0
# print (self.node_num)
while n < (20 + node_num * 10) and i < node_num:
    affinity_list.insert(i, text.split()[n])
    n = n + 10
    i = i + 1

#print (affinity_list)

for i in range (0,8):
    affinity_list[i] = float(affinity_list[i])

for i in range (0,8):
    if (affinity_list[i] - delta[i] >= 1.0):
        affinity_list[i] = 1.0
    elif (affinity_list[i] - delta[i] <= 0.0):
        affinity_list[i] = 0.1
    else:
        affinity_list[i] = affinity_list[i] - delta[i]

#print (affinity_list)

#for i in range(0,8):
#    p = Popen('ceph osd primary-affinity %d %f' % (i, affinity_list[i]), shell=True)
#    retcode = p.wait()
