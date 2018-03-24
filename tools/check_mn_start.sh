#!/bin/bash

# This script can only be executed in MN host.

MN_LOG=$(zstack-ctl status|grep management-server.log|awk -F: '{ print $2}'|tr -d ' ')

keys=`cat <<EOF
create ThreadFacade with max thread number
use RabbitMQ server IPs
Plugin system has been initialized successfully
Management node: managementNode.* starts successfully
EOF`


cnt=1
while read line
do
    #echo $line
    cat $MN_LOG|grep "$line" >/tmp/mn_filtered.log
    ret=$?
    if [ $ret -ne 0 -a $cnt -le 3 ];then
        echo "@@@NOT FIND MANDATORY KEY IN MN LOG@@@->KEY= "${line}
        exit 1
    elif [ $ret -ne 0 -a $cnt -gt 3 ];then
        echo "@@@NOT FIND ADDITIONAL KEY IN MN LOG@@@->KEY= "${line}
    else
        echo "@@@FIND KEY IN MN LOG@@@->KEY= "${line}
    fi
    let cnt=cnt+1
done <<< "$keys"

exit 0
