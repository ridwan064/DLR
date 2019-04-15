i=2
while [ "$i" -lt 5 ]
do

file_name1=cos_h
file_name=$file_name1$case
var=`date +%Y-%m-%d-%H:%M:%S`
eval j=($var)
#
new_fileName=$j.$file_name.$i
#
##iostat
#echo "running iostat..."
#pdsh -w node1,node2,node4,node5,node6,node7,node8,node9 'iostat -x 20 13' > /home/ceph-user/iostat_logs/$new_fileName &
echo "running vmstat..."
pdsh -w node1,node2,node4,node5,node6,node7,node8,node9 'vmstat 30 15' > /home/ceph-user/vmstat_logs/$new_fileName &


#
sleep 40
echo "running cosbench..."
pdsh -w cosbench 'cd /home/ceph-user/cos; sh cli.sh submit conf/workload2.xml' &

/home/ceph-user/scripts/run_get_cosbench_data.sh &

echo "running sysbench ..."
#2G,180
#pdsh -w node1,node2,node4,node5 'cd /home/ceph-user/fio-data;fio --name=randread --ioengine=libaio --iodepth=16 --rw=randread --bs=4k --direct=0 --size=2G --numjobs=4 --runtime=180 --group_reporting --output rados_seq_fio' &
#pdsh -w node1,node2,node4,node5 'sysbench --num-threads=64 --test=cpu --cpu-max-prime=200000 run --max-time=180s' &
pdsh -w node1,node2,node4,node5 'sysbench --test=memory --memory-total-size=1000G --num-threads=1 --memory-oper=write run' &
sleep 300
#sleep 180

python3 /home/ceph-user/scripts/interact.py
/home/ceph-user/scripts/pool_cleanup.sh

#pdsh -w node1,node2,node4,node5 'pkill -9 sysbench'
#pdsh -w node1,node2,node4,node5 'pkill -9 fio'
#pdsh -w node1,node2,node4,node5,node6,node7,node8,node9 'pkill -9 vmstat'
#sleep 30

#echo "dropping cache..."
#pdsh -w cosbench,admin,node1,node2,node4,node5,node6,node7,node8,node9 'sync && echo 3 | sudo tee /proc/sys/vm/drop_caches'
sleep 60

echo "done with case cos+h+sys ..."

i=`expr $i + 1`

done

