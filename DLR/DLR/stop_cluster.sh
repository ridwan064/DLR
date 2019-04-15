#sleep 180
pdsh -w node1,node2,node4,node5 'pkill -9 sysbench'
pdsh -w node1,node2,node4,node5,node6,node7,node8,node9 'pkill -9 vmstat'
sleep 30

echo "dropping cache..."
pdsh -w cosbench,admin,node1,node2,node4,node5,node6,node7,node8,node9 'sync && echo 3 | sudo tee /proc/sys/vm/drop_caches'
sleep 10
echo "done"
