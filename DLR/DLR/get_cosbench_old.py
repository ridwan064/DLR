from selenium import webdriver
from bs4 import BeautifulSoup
import numpy as np
import subprocess


def get_cosbench(url):
    driver = webdriver.PhantomJS(executable_path='/usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
    driver.get(url) 
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    tag_list= (soup.find_all('td'))
    numbers = [d.text.encode('utf-8') for d in tag_list]
    
    #read_response time
    rd_rt=numbers[11].strip().split()[0] #unit is in ms
    #bandwidth unit is in MB/s 
    if numbers[14].strip().split()[1]=='KB/S':
        rd_bw=(float(numbers[14].strip().split()[0])/1000.0)
    else:
        rd_bw=numbers[14].strip().split()[0]
    
    wr_rt=numbers[19].strip().split()[0]

    if numbers[22].strip().split()[1]=='KB/S':
        wr_bw=(float(numbers[22].strip().split()[0])/1000.0)
    else:
        wr_bw=numbers[22].strip().split()[0]
    #wr_bw=numbers[22].strip().split()[0]

    cos_data=np.array([rd_rt,rd_bw,wr_rt,wr_bw])

    print (cos_data)


jobID = subprocess.check_output(['/home/ceph-user/scripts/get_cosbench_jobID.sh'])
cosbench_url='http://129.114.33.85:19088/controller/workload.html?id='+jobID
get_cosbench(cosbench_url)
