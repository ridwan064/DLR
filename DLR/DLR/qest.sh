

#output=$((python3 /home/ceph-user/scripts/get_cosbench_data.py) 2> &1)

#while true
#do
#output=`python /home/ceph-user/scripts/kill_cos.py`
#zero="Nai"
#if [ $output == $zero ]; then
#echo "found"
#break
#fi
#done
#
#
##A="$(cut -d'l' -f2 <<<"$output")"
##echo $A

(echo "first one"; sleep 4; echo "second") &
