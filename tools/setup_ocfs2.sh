#!/bin/bash
set -x
set -e
export PS4='+[#$LINENO ${FUNCNAME[0]}() $BASH_SOURCE] '

declare -a IP
IP[0]=$1
IP[1]=$2

if [ "$1" == "" ]; then
    OCFS2_ONE_NODE=yes
fi

auto_ssh_copy_id () {

    expect -c "set timeout -1;
                spawn ssh-copy-id $2;
                expect {
                    *(yes/no)* {send -- yes\r;exp_continue;}
                    *assword:* {send -- $1\r;exp_continue;}
                    eof        {exit 0;}
                }";
}

gen_ssh_keys(){
    ssh-keygen -q -t rsa -N "" -f /root/.ssh/id_rsa
    cat /root/.ssh/id_rsa.pub > /root/.ssh/authorized_keys
    chmod go-rwx /root/.ssh/authorized_keys
}

#yum --disablerepo=* --enablerepo=zstack-local install -y iptables-services >/dev/null 2>&1
#yum --disablerepo=* --enablerepo=zstack-local,ceph-hammer -y install ceph ceph-deploy ntp expect>/dev/null 2>&1
HOST_IP=`ip addr show eth0 | sed -n '3p' | awk '{print $2}' | awk -F / '{print $1}'`

echo " $HOST_IP ocfs2-host1 ">>/etc/hosts
if [ "${OCFS2_ONE_NODE}" != "yes" ]; then
    echo " ${IP[0]} ocfs2-host2 ">>/etc/hosts
    echo " ${IP[1]} ocfs2-host3 ">>/etc/hosts
fi
cat /etc/hosts | sort -u >/etc/host-tmp
mv /etc/host-tmp /etc/hosts
sleep 2

[  -f /root/.ssh/id_rsa ] || gen_ssh_keys
auto_ssh_copy_id password ocfs2-host1
if [ "${OCFS2_ONE_NODE}" != "yes" ]; then
    auto_ssh_copy_id password ocfs2-host2
    auto_ssh_copy_id password ocfs2-host3
fi

scp /etc/hosts ocfs2-host1:/etc/hosts
if [ "${OCFS2_ONE_NODE}" != "yes" ]; then
    scp /etc/hosts ocfs2-host2:/etc/hosts
    scp /etc/hosts ocfs2-host3:/etc/hosts
fi

ssh  ocfs2-host1 hostnamectl set-hostname ocfs2-host1 && export HOSTNAME=ocfs2-host1
if [ "${OCFS2_ONE_NODE}" != "yes" ]; then
    ssh  ocfs2-host2 hostnamectl set-hostname ocfs2-host2 && export HOSTNAME=ocfs2-host2
    ssh  ocfs2-host3 hostnamectl set-hostname ocfs2-host3 && export HOSTNAME=ocfs2-host3
fi

ssh ocfs2-host1 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
if [ "${OCFS2_ONE_NODE}" != "yes" ]; then 
    ssh ocfs2-host2 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
    ssh ocfs2-host3 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
fi

ssh ocfs2-host1 "systemctl disable firewalld; systemctl stop firewalld"
if [ "${OCFS2_ONE_NODE}" != "yes" ]; then 
    ssh ocfs2-host2 "systemctl disable firewalld; systemctl stop firewalld"
    ssh ocfs2-host3 "systemctl disable firewalld; systemctl stop firewalld"
fi

ssh ocfs2-host1 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
if [ "${OCFS2_ONE_NODE}" != "yes" ]; then 
    ssh ocfs2-host2 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
    ssh ocfs2-host3 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
fi



set +e
for I in `seq 3`; do
done
