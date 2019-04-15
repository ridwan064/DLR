Node_Num=8
Total_Mem=4048288

import subprocess
import sys
import os
import numpy as np
from collections import OrderedDict
# affinity
def get_current_affinity():
    command = ['ceph','osd','tree']
    p = subprocess.Popen(command,stdout=subprocess.PIPE)
    text = p.stdout.read()
    retcode = p.wait()

    affinity_list = []
    #free_list = []
    node_list = ["1","2","4","5","6","7","8","9"]
    print (type(node_list))
    d = dict.fromkeys(node_list, 0)
    #print (type(OrderedDict(d)))
    n=20
    i=0
    while n<(20+Node_Num*10) and i<Node_Num:
        affinity_list.insert(i,text.split()[n])
        n=n+10
        i=i+1
    affinity_array=np.array(affinity_list)
    print (affinity_array)
    return affinity_array

get_current_affinity()
    #print (affinity_array)
