from subprocess import Popen
#create-pools
#pg_num=8
#for i in range(1,101):
#    p = Popen('ceph osd pool create mycontainers%d %d' % (i,pg_num), shell=True)
#    retcode = p.wait()

#delete-pools
#for i in range (1,101):
#    q = Popen('ceph osd pool delete mycontainers%d mycontainers%d --yes-i-really-really-mean-it' % (i,i), shell=True)
#    retcode = q.wait()

#delete-pools
rep_size=3
for i in range (1,101):
    q = Popen('ceph osd pool set mycontainers%d size %d' % (i,rep_size), shell=True)
    retcode = q.wait()

