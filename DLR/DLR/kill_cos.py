from subprocess import Popen, PIPE

def check_cos():
    cosbench_info_command = "pdsh -w cosbench 'sh /home/ceph-user/cos/cli.sh info'"
    p3 = Popen(cosbench_info_command, stdout=PIPE, shell=True)
    text = p3.stdout.read().strip()
    job_id = text.splitlines()[5].strip().split(":")[1].strip().split()[0].strip()

    if job_id != "Total":
        #cosbench_kill_cmd = "pdsh -w cosbench 'sh /home/ceph-user/cos/cli.sh cancel {}'".format(job_id)
        #print('Killing Cosbench Job: {}'.format(job_id))
        #print('Killing Cosbench with cmd: {}'.format(cosbench_kill_cmd))
        #Popen(cosbench_kill_cmd, shell=True)
        #print('Killed Cosbench Job: {}'.format(job_id))
        print("Running")
    else:
        print("Ended")
        


check_cos()

