#/bin/bash
path=$1
rm -rf /etc/yum.repos.d/zstack-aliyun-yum.repo
cp $path /etc/yum.repos.d/zstack-aliyun-yum.repo
yum install -y fio stress iperf --enablerepo=ali* --nogpgcheck
