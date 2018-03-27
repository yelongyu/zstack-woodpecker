#!/bin/bash

# This script can only be executed in MN host.

MN_LOG=$(zstack-ctl status|grep management-server.log|awk -F: '{ print $2}'|tr -d ' ')

#Original Checker Points:
#create ThreadFacade with max thread number
#use RabbitMQ server IPs
#Plugin system has been initialized successfully
#Management node: managementNode.* starts successfully

keys=`cat <<EOF
use RabbitMQ server IPs
Plugin system has been initialized successfully
Management node: managementNode.* starts successfully
EOF`

reboot_key=$(last reboot|head -n 1|awk '{print $7,$8}') #26 13:42
auto_find_reboot_line_num(){
    machine_start_time=$1
    min=$(echo $reboot_key|awk '{print $2}'|cut -d: -f1)
    sec=$(echo $reboot_key|awk '{print $2}'|cut -d: -f2)
    day=$(echo $reboot_key|awk '{print $1}')
    for i in `seq 5`
    do
        let min_sec_raw_cnt=min*60+sec
        let min_sec_raw_cnt=min_sec_raw_cnt+1
        let min=min_sec_raw_cnt/60
        let sec=min_sec_raw_cnt%60
        grep "$day $min:$sec" $MN_LOG >/dev/null
        if [ $? -eq 0 ];then
            #echo "$day $min:$sec"
            line_num=$(grep "$day $min:$sec" $MN_LOG -n|head -n 1|cut -d: -f1)
            echo $line_num
            exit 0
        fi
    done
    echo ""
    exit 1
}
reboot_line_num=$(auto_find_reboot_line_num $reboot_key)

cnt=1
while read line
do
    #echo $line
    tail -n +$reboot_line_num $MN_LOG|grep "$line" >/tmp/mn_filtered.log
    ret=$?
    if [ $ret -ne 0 -a $cnt -le 2 ];then
        echo "@@@NOT FIND MANDATORY KEY IN MN LOG@@@->KEY= "${line}
        exit 1
    elif [ $ret -ne 0 -a $cnt -gt 2 ];then
        echo "@@@NOT FIND ADDITIONAL KEY IN MN LOG@@@->KEY= "${line}
    else
        echo "@@@FIND KEY IN MN LOG@@@->KEY= "${line}
    fi
    let cnt=cnt+1
done <<< "$keys"

exit 0
