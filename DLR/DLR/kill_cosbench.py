from subprocess import Popen, PIPE
import re
cosbench_info_command = "pdsh -w cosbench 'sh /home/ceph-user/cos/cli.sh info'"
p3 = Popen(cosbench_info_command, stdout=PIPE, shell=True)
text = p3.stdout.read().strip()
text = str(text).strip()
p3.communicate()
p3.wait()
# print (text)
# job_id = text.splitlines()[5].strip().split(":")[1].strip().split()[0].strip()
wexp = r': (w[0-9]+)'
finds = re.findall(wexp, text)
found_job = len(finds) != 0
if found_job:
    print("jobs found ", len(finds))
    for job_id in finds:
        cosbench_kill_cmd = "pdsh -w cosbench 'sh /home/ceph-user/cos/cli.sh cancel {}'".format(job_id)
        print('Killing Cosbench Job: {}'.format(job_id))
        print('Killing Cosbench with cmd: {}'.format(cosbench_kill_cmd))
        p4 = Popen(cosbench_kill_cmd, shell=True)
        p4.communicate()
        p4.wait()
        print('Killed Cosbench Job: {}'.format(job_id))
else:
    print("All set no cosbench Job is running..")
