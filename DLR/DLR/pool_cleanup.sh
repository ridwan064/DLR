echo "running rados cleanup..."
rados -p mycontainers1 cleanup --prefix my
sleep 5
echo "running rados cleanup..."
rados -p mycontainers2 cleanup --prefix my
sleep 10
echo "done with rados cleanup..."
rados df
#ceph osd primary-affinity 0 1.0
#ceph osd primary-affinity 1 1.0
#ceph osd primary-affinity 2 1.0
#ceph osd primary-affinity 3 1.0
#ceph osd primary-affinity 4 1.0
#ceph osd primary-affinity 5 1.0
#ceph osd primary-affinity 6 1.0
#ceph osd primary-affinity 7 1.0
