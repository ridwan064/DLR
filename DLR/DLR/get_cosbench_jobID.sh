#!/bin/bash

#get the latest folder from cosbench archive
var=$(pdsh -w cosbench 'cd ~/cos/archive; echo $(ls -dt w*/ | head -1)')
echo $var
#parse to extract only the job id
job_name=${var##*:}
job_id=${job_name%*/}
echo ${job_id%-*}

 
