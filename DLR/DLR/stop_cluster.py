import subprocess

def stop_cluster():
    subprocess.call("/home/ceph-user/scripts/stop_cluster.sh",shell=True)
    return True

