

import subprocess
#get running job id
command = ['pdsh','-w','cosbench','sh', 'cos/cli.sh', 'info']
p = subprocess.Popen(command,stdout=subprocess.PIPE)
text = p.stdout.read().strip()
job_id=text.splitlines()[5].strip().split(":")[1].strip()
print (job_id.strip())

if job_id != "Total":
    subprocess.Popen(['pdsh','-w','cosbench','sh', 'cos/cli.sh', 'cancel', job_id], shell=False)
else:
    print ("No cosbench job is running")
