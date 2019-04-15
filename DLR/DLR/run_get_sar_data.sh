j=0
while [ $j -le 9 ]
do
        python3 /home/ceph-user/scripts/get_sar-data.py
        sleep 30
        j=`expr $j + 1`
done

