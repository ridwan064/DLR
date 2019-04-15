file_name1=cos_h
file_name=$file_name1$case
var=`date +%Y-%m-%d-%H:%M:%S`
eval j=($var)
#
new_fileName=$j.$file_name

echo "running vmstat..."
pdsh -w node1,node2,node4,node5,node6,node7,node8,node9 'vmstat 20 13' > /home/ceph-user/vmstat_logs/$new_fileName &

sleep 40

echo "running cosbench..."
pdsh -w cosbench 'cd /home/ceph-user/cos; sh cli.sh submit conf/workload2.xml' &


echo "running sysbench ..."
#2G,180
#pdsh -w node1,node2,node4,node5 'cd /home/ceph-user/fio-data;fio --name=randread --ioengine=libaio --iodepth=16 --rw=randread --bs=4k --direct=0 --size=2G --numjobs=4 --runtime=180 --group_reporting --output rados_seq_fio' &
#pdsh -w node1,node2,node4,node5 'sysbench --num-threads=64 --test=cpu --cpu-max-prime=200000 run --max-time=180s' &
pdsh -w node1,node2,node4,node5 'sysbench --test=memory --memory-total-size=800G --num-threads=256 --memory-oper=write run' &
