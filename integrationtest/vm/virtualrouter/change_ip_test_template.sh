#!/bin/bash

node_ip="TemplateNodeIP"
original_ip="TemplateOriginalIP"
test_ip="TemplateTestIP"

# ping node ip with original ip
ping_result=`ping $node_ip -c 4`
if [[ $ping_result =~ "4 received" ]]; then
    echo "ping node id with original ip">/home/ip_spoofing_result
else
    echo "fail to ping node id with original ip">/home/ip_spoofing_result
    exit 0
fi

# change original ip to test ip
ifconfig eth0 $test_ip
ifconfig_result=`ifconfig`
if [[ $ifconfig_result =~ $test_ip ]]; then
    echo "change original ip to test ip">/home/ip_spoofing_result
else
    echo "fail to change original ip to test ip">home/ip_spoofing_result
    exit 0
fi 

# ping node ip with test ip
ping_result=`ping $node_ip -c 4`
if [[ $ping_result =~ "0 received" ]]; then
    echo "ping node ip with test ip">/home/ip_spoofing_result
else
    echo "fail to ping node ip with test ip">/home/ip_spoofing_result
    exit 0
fi

# reover ip to original ip 
ifconfig eth0 $original_ip
ifconfig_result=`ifconfig`
if [[ $ifconfig_result =~ $original_ip ]]; then
    echo "1">/home/ip_spoofing_result
else
    echo "fail to recover ip to original ip">home/ip_spoofing_result
    exit 0
fi
