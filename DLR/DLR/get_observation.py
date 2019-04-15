from subprocess import Popen, PIPE
import re
import sys
import os
import numpy as np
from collections import OrderedDict
import glob

def get_SAR_all_nodes(self):
    affinity_array = self.get_affinities()
    #get latest SAR log file
    sarstat_log_dir = '/home/ceph-user/sar-logs/'
    list_of_files = glob.glob(sarstat_log_dir + '/*')
    latest_file = max(list_of_files, key=os.path.getctime) 
    
    #get the last 80 lines for 8 nodes
    raw_data = Popen(['tail', '-n', '80', latest_file],shell=False, stdout=PIPE)
    data = raw_data.stdout.read().strip()
    data= str(data)
    
    #cpu+io data parsing
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
    
    
    #mem data parsing
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
    
    mem_usage_array = np.array(mem_usage_list)
    
    #network data parsing
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
    
    net_usage_array = np.array(net_usage_list)
    obs = np.array([affinity_array, cpu_usage_array, mem_usage_array, net_usage_array, io_wait_array]).T
    return obs
