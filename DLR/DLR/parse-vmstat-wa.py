import collections
import re
import sys
from collections import OrderedDict
from datetime import datetime
from itertools import islice
from subprocess import call
from array import *

#val=sys.argv
#index=int(val[1])

fout1 = open("/home/ceph-user/logs/data1",'w');
fout2 = open("/home/ceph-user/logs/data2",'w');
fout4 = open("/home/ceph-user/logs/data4",'w');
fout5 = open("/home/ceph-user/logs/data5",'w');
fout6 = open("/home/ceph-user/logs/data6",'w');
fout7 = open("/home/ceph-user/logs/data7",'w');
fout8 = open("/home/ceph-user/logs/data8",'w');
fout9 = open("/home/ceph-user/logs/data9",'w');

with open(r"/home/ceph-user/vmstat_logs/2017-10-24-07:17:11.cos_h.0","r") as f:
    lines_after_112 = f.readlines()[32:]
    
    M=0
    N = 1
    summ=0.0
    while(N<231):    # 48+6=54
        lines_gen = islice(lines_after_112, M,N)
        #print (lines_gen)
        
                        
        for i, line in enumerate(lines_gen):
            #print (line)
            node=line.split()[0].split(':',1)[0].split('node')[1]
            
            wa=0
            
                                
                            
            if i == 0:
                
                #wa=line.split( )[4]
                wa=line.split( )[16]
                if node=="1" and wa!='' :
                    fout1.write(str(wa)+"\n") 
                if node=="2" and  wa!='' :
                    fout2.write(str(wa)+"\n")                            
                if node=="4" and  wa!='' :
                    fout4.write(str(wa)+"\n")            
                if node=="5" and  wa!='' :
                    fout5.write(str(wa)+"\n")            
                if node=="6" and  wa!='' :
                    fout6.write(str(wa)+"\n")        
                if node=="7" and  wa!='' :
                    fout7.write(str(wa)+"\n")
                if node=="8" and  wa!='' :
                    fout8.write(str(wa)+"\n")
                if node=="9" and  wa!='' :
                    fout9.write(str(wa)+"\n")
                  
        
                    
                

        M=M+1    
        N=N+1 
        
   

