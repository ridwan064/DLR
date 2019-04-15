import subprocess

def start_cluster():
    subprocess.call("/home/ceph-user/scripts/start_cluster.sh",shell=True)
    return True
#start_cluster()    
