#!/bin/bash
set -x
set -e
export PS4='+[#$LINENO ${FUNCNAME[1]}() $BASH_SOURCE] '

declare -a IP
IP[0]=$1
IP[1]=$2
IP[2]=$3
IP[3]=$4

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

auto_o2cb_init_cfg () {

    expect -c "set timeout -1;
                spawn ssh -l root ${1} o2cb.init configure
                expect *(y/n)*
                send y\r
                expect *\[o2cb\]*
                send \r 
                expect *\[ocfs2\]*
                send  zstackstorage\r
                expect *(>=7)*
                send 121\r
                expect *(>=5000)*
                send 30000\r
                expect *(>=1000)*
                send 5000\r
                expect *(>=2000)*
                send 4000\r
                expect eof
              "
}

wait_for_machine_boot_up() {
    count=0
    while true
    do
        ssh $1 pwd
        if [ $? -eq 0 ]; then
            break
        else
            if (( count > 180 )); then
               echo "ERR: wait 180s but machine still not alive"
               exit 1
            fi
        fi
        sleep 1
        let count++ 
        echo "already wait for ${count} sec."
    done
}

#yum --disablerepo=* --enablerepo=zstack-local install -y iptables-services >/dev/null 2>&1

echo " ${IP[0]} ocfs2-host1 ">>/etc/hosts
echo " ${IP[1]} ocfs2-host2 ">>/etc/hosts
echo " ${IP[2]} ocfs2-host3 ">>/etc/hosts
echo " ${IP[3]} ocfs2-host4 ">>/etc/hosts

cat /etc/hosts | sort -u >/etc/host-tmp
mv /etc/host-tmp /etc/hosts
sleep 2

[  -f /root/.ssh/id_rsa ] || gen_ssh_keys
auto_ssh_copy_id password ocfs2-host1
auto_ssh_copy_id password ocfs2-host2
auto_ssh_copy_id password ocfs2-host3
auto_ssh_copy_id password ocfs2-host4

scp /etc/hosts ocfs2-host1:/etc/hosts
scp /etc/hosts ocfs2-host2:/etc/hosts
scp /etc/hosts ocfs2-host3:/etc/hosts
scp /etc/hosts ocfs2-host4:/etc/hosts

ssh  ocfs2-host1 hostnamectl set-hostname ocfs2-host1 && export HOSTNAME=ocfs2-host1
ssh  ocfs2-host2 hostnamectl set-hostname ocfs2-host2 && export HOSTNAME=ocfs2-host2
ssh  ocfs2-host3 hostnamectl set-hostname ocfs2-host3 && export HOSTNAME=ocfs2-host3
ssh  ocfs2-host4 hostnamectl set-hostname ocfs2-host4 && export HOSTNAME=ocfs2-host4

ssh ${IP[0]} 'yum --disablerepo=* --enablerepo=zstack-local install -y iptables-services >/dev/null 2>&1'
ssh ${IP[0]} 'test -f /etc/sysconfig/iptables && sed -i "/COMMIT$/d" /etc/sysconfig/iptables'
ssh ${IP[0]} 'echo "-A INPUT -s 172.20.0.0/16 -j ACCEPT" >>/etc/sysconfig/iptables'
ssh ${IP[0]} 'echo "COMMIT" >>/etc/sysconfig/iptables'
ssh ${IP[0]} 'service iptables restart'

ssh ${IP[1]} 'yum --disablerepo=* --enablerepo=zstack-local install -y iptables-services >/dev/null 2>&1'
ssh ${IP[1]} 'test -f /etc/sysconfig/iptables && sed -i "/COMMIT$/d" /etc/sysconfig/iptables'
ssh ${IP[1]} 'echo "-A INPUT -s 172.20.0.0/16 -j ACCEPT" >>/etc/sysconfig/iptables'
ssh ${IP[1]} 'echo "COMMIT" >>/etc/sysconfig/iptables'
ssh ${IP[1]} 'service iptables restart'

ssh ${IP[2]} 'yum --disablerepo=* --enablerepo=zstack-local install -y iptables-services >/dev/null 2>&1'
ssh ${IP[2]} 'test -f /etc/sysconfig/iptables && sed -i "/COMMIT$/d" /etc/sysconfig/iptables'
ssh ${IP[2]} 'echo "-A INPUT -s 172.20.0.0/16 -j ACCEPT" >>/etc/sysconfig/iptables'
ssh ${IP[2]} 'echo "COMMIT" >>/etc/sysconfig/iptables'
ssh ${IP[2]} 'service iptables restart'

ssh ${IP[3]} 'yum --disablerepo=* --enablerepo=zstack-local install -y iptables-services >/dev/null 2>&1'
ssh ${IP[3]} 'test -f /etc/sysconfig/iptables && sed -i "/COMMIT$/d" /etc/sysconfig/iptables'
ssh ${IP[3]} 'echo "-A INPUT -s 172.20.0.0/16 -j ACCEPT" >>/etc/sysconfig/iptables'
ssh ${IP[3]} 'echo "COMMIT" >>/etc/sysconfig/iptables'
ssh ${IP[3]} 'service iptables restart'

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

set +e
ssh ${IP[0]} "yum -y --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 update"
ssh ${IP[0]} "yum -y --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 \
install kernel-uek kernel-uek-devel kernel-uek-doc kernel-uek-firmware \
dtrace-modules ocfs2-tools ocfs2-tools-devel iscsi-initiator-utils \
device-mapper-multipath device-mapper-multipath-sysvinit
"
ssh ${IP[0]} 'grub2-set-default "CentOS Linux (4.1.12-37.2.2.el7uek.x86_64) 7 (Core)"'
ssh ${IP[0]} reboot &

ssh ${IP[1]} "yum -y --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 update"
ssh ${IP[1]} "yum -y --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 \
install kernel-uek kernel-uek-devel kernel-uek-doc kernel-uek-firmware \
dtrace-modules ocfs2-tools ocfs2-tools-devel iscsi-initiator-utils \
device-mapper-multipath device-mapper-multipath-sysvinit
"
ssh ${IP[1]} 'grub2-set-default "CentOS Linux (4.1.12-37.2.2.el7uek.x86_64) 7 (Core)"'
ssh ${IP[1]} reboot &

ssh ${IP[2]} "yum -y --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 update"
ssh ${IP[2]} "yum -y --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 \
install kernel-uek kernel-uek-devel kernel-uek-doc kernel-uek-firmware \
dtrace-modules ocfs2-tools ocfs2-tools-devel iscsi-initiator-utils \
device-mapper-multipath device-mapper-multipath-sysvinit
"
ssh ${IP[2]} 'grub2-set-default "CentOS Linux (4.1.12-37.2.2.el7uek.x86_64) 7 (Core)"'
ssh ${IP[2]} reboot &

ssh ${IP[3]} "yum -y --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 update"
ssh ${IP[3]} "yum -y --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 \
install kernel-uek kernel-uek-devel kernel-uek-doc kernel-uek-firmware \
dtrace-modules ocfs2-tools ocfs2-tools-devel iscsi-initiator-utils \
device-mapper-multipath device-mapper-multipath-sysvinit
"
ssh ${IP[3]} 'grub2-set-default "CentOS Linux (4.1.12-37.2.2.el7uek.x86_64) 7 (Core)"'
ssh ${IP[3]} reboot &

echo "wait for reboot to switch kernel"
wait_for_machine_boot_up ${IP[0]}
wait_for_machine_boot_up ${IP[1]}
wait_for_machine_boot_up ${IP[2]}
wait_for_machine_boot_up ${IP[3]}

set -e
ssh ${IP[0]} 'uname -a|grep el7uek' || exit 1
ssh ${IP[1]} 'uname -a|grep el7uek' || exit 1
ssh ${IP[2]} 'uname -a|grep el7uek' || exit 1
ssh ${IP[3]} 'uname -a|grep el7uek' || exit 1

ssh ${IP[0]} 'modprobe dm-multipath'
ssh ${IP[0]} 'modprobe dm-round-robin' 
ssh ${IP[0]} 'service multipathd start'
ssh ${IP[0]} 'mpathconf --enable'
ssh ${IP[0]} 'multipath -ll'

ssh ${IP[0]} 'mkdir -p /dlm'
ssh ${IP[1]} 'mkdir -p /dlm'
ssh ${IP[2]} 'mkdir -p /dlm'
ssh ${IP[3]} 'mkdir -p /dlm'

ssh ${IP[0]} 'rm -rf /etc/ocfs2/cluster.conf'
ssh ${IP[0]} 'o2cb add-cluster zstackstorage'
ssh ${IP[0]} "o2cb add-node zstackstorage ocfs2-host1 --ip ${IP[0]}"
ssh ${IP[0]} "o2cb add-node zstackstorage ocfs2-host2 --ip ${IP[1]}"
ssh ${IP[0]} "o2cb add-node zstackstorage ocfs2-host3 --ip ${IP[2]}"
ssh ${IP[0]} "o2cb add-node zstackstorage ocfs2-host4 --ip ${IP[3]}"

ssh ${IP[0]} "o2cb heartbeat-mode zstackstorage local"

#todo: check the .conf is valid
ssh ${IP[0]} "cat /etc/ocfs2/cluster.conf"

#todo use expect to populate the fields
#ssh ${IP[0]} "o2cb.init configure"
auto_o2cb_init_cfg ${IP[0]}

ssh ${IP[0]} "systemctl enable o2cb.service"
ssh ${IP[0]} "systemctl enable ocfs2.service"
ssh ${IP[0]} "o2cb.init online"
ssh ${IP[0]} "o2cb.init status"
ssh ${IP[0]} "echo 'kernel.panic = 30' >>/etc/sysctl.conf"
ssh ${IP[0]} "echo 'kernel.panic_on_oops = 1' >>/etc/sysctl.conf"
ssh ${IP[0]} "sysctl -p"

scp ${IP[0]}:/etc/ocfs2/cluster.conf /tmp/cluster.conf
scp ${IP[0]}:/etc/sysconfig/o2cb /tmp/o2cb

ssh ${IP[1]} "mkdir -p /etc/ocfs2/"
scp /tmp/cluster.conf ocfs2-host2:/etc/ocfs2/
scp /tmp/o2cb ocfs2-host2:/etc/sysconfig/
#ssh ${IP[1]} "systemctl start o2cb.service"
ssh ${IP[1]} "o2cb.init status"
ssh ${IP[1]} "systemctl enable o2cb.service"
ssh ${IP[1]} "systemctl enable ocfs2.service"
ssh ${IP[1]} "o2cb.init online"
#ssh ${IP[1]} "o2cb.init start"

ssh ${IP[2]} "mkdir -p /etc/ocfs2/"
scp /tmp/cluster.conf ocfs2-host3:/etc/ocfs2/
scp /tmp/o2cb ocfs2-host3:/etc/sysconfig/
ssh ${IP[2]} "o2cb.init status"
ssh ${IP[2]} "systemctl enable o2cb.service"
ssh ${IP[2]} "systemctl enable ocfs2.service"
ssh ${IP[2]} "o2cb.init online"

ssh ${IP[3]} "mkdir -p /etc/ocfs2/"
scp /tmp/cluster.conf ocfs2-host4:/etc/ocfs2/
scp /tmp/o2cb ocfs2-host4:/etc/sysconfig/
ssh ${IP[3]} "o2cb.init status"
ssh ${IP[3]} "systemctl enable o2cb.service"
ssh ${IP[3]} "systemctl enable ocfs2.service"
ssh ${IP[3]} "o2cb.init online"


if [ -n "$SMP_URL" ]; then
    OCFS2_MNT_POINT=$SMP_URL
else
    OCFS2_MNT_POINT="/opt/smp/disk1/"
fi
ssh ${IP[0]} "mkfs.ocfs2 --cluster-stack=o2cb -C 256K -J size=128M -N 16 -L ocfs2-disk1 --cluster-name=zstackstorage --fs-feature-level=default -T vmstore /dev/sda"
ssh ${IP[0]} "mkdir -p ${OCFS2_MNT_POINT}"
ssh ${IP[0]} "mount.ocfs2 /dev/sda ${OCFS2_MNT_POINT}"

ssh ${IP[1]} "mkdir -p ${OCFS2_MNT_POINT}"
ssh ${IP[1]} "mount.ocfs2 /dev/sda ${OCFS2_MNT_POINT}"

ssh ${IP[2]} "mkdir -p ${OCFS2_MNT_POINT}"
ssh ${IP[2]} "mount.ocfs2 /dev/sda ${OCFS2_MNT_POINT}"

ssh ${IP[3]} "mkdir -p ${OCFS2_MNT_POINT}"
ssh ${IP[3]} "mount.ocfs2 /dev/sda ${OCFS2_MNT_POINT}"
