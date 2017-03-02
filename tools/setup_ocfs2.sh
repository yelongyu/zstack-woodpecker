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

yum --disablerepo=* --enablerepo=zstack-local install -y iptables-services >/dev/null 2>&1
HOST_IP=`ip addr show eth0 | sed -n '3p' | awk '{print $2}' | awk -F / '{print $1}'`

ssh ${HOST_IP} 'echo "-A INPUT -s 172.20.0.0/16 -j ACCEPT" >>/etc/sysconfig/iptables'
ssh ${HOST_IP} 'echo "COMMIT" >>/etc/sysconfig/iptables'
ssh ${HOST_IP} 'service iptables restart'

if [ "${OCFS2_ONE_NODE}" != "yes" ]; then
    ssh ${IP[0]} 'echo "-A INPUT -s 172.20.0.0/16 -j ACCEPT" >>/etc/sysconfig/iptables'
    ssh ${IP[0]} 'echo "COMMIT" >>/etc/sysconfig/iptables'
    ssh ${IP[0]} 'service iptables restart'
    
    ssh ${IP[1]} 'echo "-A INPUT -s 172.20.0.0/16 -j ACCEPT" >>/etc/sysconfig/iptables'
    ssh ${IP[1]} 'echo "COMMIT" >>/etc/sysconfig/iptables'
    ssh ${IP[1]} 'service iptables restart'
fi

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
exit 0

#ssh ocfs2-host1 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
#if [ "${OCFS2_ONE_NODE}" != "yes" ]; then 
#    ssh ocfs2-host2 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
#    ssh ocfs2-host3 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
#fi
#
#ssh ocfs2-host1 "systemctl disable firewalld; systemctl stop firewalld"
#if [ "${OCFS2_ONE_NODE}" != "yes" ]; then 
#    ssh ocfs2-host2 "systemctl disable firewalld; systemctl stop firewalld"
#    ssh ocfs2-host3 "systemctl disable firewalld; systemctl stop firewalld"
#fi
#
#ssh ocfs2-host1 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
#if [ "${OCFS2_ONE_NODE}" != "yes" ]; then 
#    ssh ocfs2-host2 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
#    ssh ocfs2-host3 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
#fi

ssh $HOST_IP "yum -y --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 update"
ssh $HOST_IP "yum --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 \
install kernel-uek kernel-uek-devel kernel-uek-doc kernel-uek-firmware \
dtrace-modules ocfs2-tools ocfs2-tools-devel iscsi-initiator-utils \
device-mapper-multipath device-mapper-multipath-sysvinit
"
ssh $HOST_IP 'grub2-set-default "CentOS Linux (4.1.12-37.2.2.el7uek.x86_64) 7 (Core)"'
ssh $HOST_IP 'reboot'
echo "wait 120s for reboot to switch kernel"
sleep 120

ssh $HOST_IP 'uname -a|grep el7uek' || exit 1
ssh $HOST_IP 'modprobe dm-multipath'
ssh $HOST_IP 'modprobe dm-round-robin' 
ssh $HOST_IP 'service multipathd start'
ssh $HOST_IP 'mpathconf --enable'
ssh $HOST_IP 'multipath -ll'
ssh $HOST_IP 'mkdir -p /dlm'

ssh $HOST_IP 'mkdir -p /dlm'
ssh ${IP[0]} 'mkdir -p /dlm'
ssh ${IP[1]} 'mkdir -p /dlm'

ssh $HOST_IP 'o2cb add-cluster zstackstorage'
ssh $HOST_IP "o2cb add-node zstackstorage ocfs2-host1 --ip ${HOST_IP}"
ssh $HOST_IP "o2cb add-node zstackstorage ocfs2-host1 --ip ${IP[0]}"
ssh $HOST_IP "o2cb add-node zstackstorage ocfs2-host1 --ip ${IP[1]}"

ssh $HOST_IP "o2cb heartbeat-mode zstackstorage local"

#todo: check the .conf is valid
ssh $HOST_IP "cat /etc/ocfs2/cluster.conf"

#todo use expect to populate the fields
ssh $HOST_IP "o2cb.init configure"

ssh $HOST_IP "systemctl enable o2cb.service"
ssh $HOST_IP "systemctl enable ocfs2.service"
ssh $HOST_IP "o2cb.init online"
ssh $HOST_IP "o2cb.init status"
ssh $HOST_IP "echo 'kernel.panic = 30' >>/etc/sysctl.conf"
ssh $HOST_IP "echo 'kernel.panic_on_oops = 1' >>/etc/sysctl.conf"
ssh $HOST_IP "sysctl -p"

ssh ${IP[0]} "mkdir -p /etc/ocfs2/"
ssh $HOST_IP "scp /etc/ocfs2/cluster.conf ocfs2-host2:/etc/ocfs2/"
ssh $HOST_IP "scp /etc/sysconfig/o2cb ocfs2-host2:/etc/sysconfig/"
ssh ${IP[0]} "systemctl start o2cb.service"
ssh ${IP[0]} "o2cb.init status"

ssh ${IP[0]} "systemctl enable o2cb.service"
ssh ${IP[0]} "systemctl enable ocfs2.service"
ssh ${IP[0]} "o2cb.init online"
ssh ${IP[1]} "mkdir -p /etc/ocfs2/"
ssh $HOST_IP "scp /etc/ocfs2/cluster.conf ocfs2-host3:/etc/ocfs2/"
ssh $HOST_IP "scp /etc/sysconfig/o2cb ocfs2-host3:/etc/sysconfig/"
ssh ${IP[0]} "o2cb.init start"
ssh ${IP[1]} "o2cb.init status"

ssh ${IP[1]} "systemctl enable o2cb.service"
ssh ${IP[1]} "systemctl enable ocfs2.service"
ssh ${IP[1]} "o2cb.init online"

ssh $HOST_IP "mkfs.ocfs2 --cluster-stack=o2cb -C 256K -J size=128M -N 16 -L ocfs2-disk1 --cluster-name=zstackstorage --fs-feature-level=default -T vmstore /dev/sda mkfs.ocfs2 1.8.6"
ssh $HOST_IP "mkdir -p /opt/smp/disk1/"
ssh $HOST_IP "mount.ocfs2 /dev/sda /opt/smp/disk1/"

ssh ${IP[0]} "mkdir -p /opt/smp/disk1/"
ssh ${IP[0]} "mount.ocfs2 /dev/sda /opt/smp/disk1/"

ssh ${IP[1]} "mkdir -p /opt/smp/disk1/"
ssh ${IP[1]} "mount.ocfs2 /dev/sda /opt/smp/disk1/"

