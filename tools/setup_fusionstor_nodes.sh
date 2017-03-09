#!/bin/bash
set -x
set -e
export PS4='+[#$LINENO ${FUNCNAME[0]}() $BASH_SOURCE] '

declare -a IP
FUSIONSTOR_BIN_URL=$1
FUSIONSTOR=`basename ${FUSIONSTOR_BIN_URL}`
IP[0]=$2
IP[1]=$3
IP[2]=$4

if [ "$3" == "" ]; then
    FUSIONSTOR_ONE_NODE=yes
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

yum --disablerepo=* --enablerepo=zstack-local -y install  ntp expect>/dev/null 2>&1
yum --disablerepo=* --enablerepo=zstack-local install -y iptables-services >/dev/null 2>&1
#HOST_IP=`ip addr show eth0 | sed -n '3p' | awk '{print $2}' | awk -F / '{print $1}'`
cp $FUSIONSTOR_BIN_URL .

echo " ${IP[0]} fusionstor-1 ">>/etc/hosts
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ]; then
    echo " ${IP[1]} fusionstor-2 ">>/etc/hosts
    echo " ${IP[2]} fusionstor-3 ">>/etc/hosts
fi

cat /etc/hosts | sort -u >/etc/host-tmp
mv /etc/host-tmp /etc/hosts

sleep 2

[  -f /root/.ssh/id_rsa ] || gen_ssh_keys
auto_ssh_copy_id password fusionstor-1
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ]; then
    auto_ssh_copy_id password fusionstor-2
    auto_ssh_copy_id password fusionstor-3
fi

scp /etc/hosts fusionstor-1:/etc/hosts
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ]; then
    scp /etc/hosts fusionstor-2:/etc/hosts
    scp /etc/hosts fusionstor-3:/etc/hosts
fi

ssh  fusionstor-1 hostnamectl set-hostname fusionstor-1 && export HOSTNAME=fusionstor-1
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ]; then
    ssh  fusionstor-2 hostnamectl set-hostname fusionstor-2 && export HOSTNAME=fusionstor-2
    ssh  fusionstor-3 hostnamectl set-hostname fusionstor-3 && export HOSTNAME=fusionstor-3
fi

ssh  fusionstor-1 yum --disablerepo=* --enablerepo=zstack-local -y install ntp expect>/dev/null 2>&1
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ]; then 
    ssh  fusionstor-2 yum --disablerepo=* --enablerepo=zstack-local -y install ntp expect>/dev/null 2>&1
    ssh  fusionstor-3 yum --disablerepo=* --enablerepo=zstack-local -y install ntp expect>/dev/null 2>&1
fi

ssh  fusionstor-1 yum --disablerepo=* --enablerepo=zstack-local,ceph-hammer -y install iptables-services>/dev/null 2>&1
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ]; then 
    ssh  fusionstor-2 yum --disablerepo=* --enablerepo=zstack-local,ceph-hammer -y install iptables-services>/dev/null 2>&1
    ssh  fusionstor-3 yum --disablerepo=* --enablerepo=zstack-local,ceph-hammer -y install iptables-services>/dev/null 2>&1
fi


ssh fusionstor-1 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ]; then 
    ssh fusionstor-2 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
    ssh fusionstor-3 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
fi

ssh fusionstor-1 "systemctl disable firewalld; systemctl stop firewalld"
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ]; then 
    ssh fusionstor-2 "systemctl disable firewalld; systemctl stop firewalld"
    ssh fusionstor-3 "systemctl disable firewalld; systemctl stop firewalld"
fi

ssh fusionstor-1 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ]; then 
    ssh fusionstor-2 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
    ssh fusionstor-3 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
fi

scp $FUSIONSTOR fusionstor-1:/root/SS100-fusionstor-install-0.4.0.bin
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ];then
    scp $FUSIONSTOR fusionstor-2:/root/SS100-fusionstor-install-0.4.0.bin
    scp $FUSIONSTOR fusionstor-3:/root/SS100-fusionstor-install-0.4.0.bin
fi

ssh fusionstor-1 "bash /root/SS100-fusionstor-install-0.4.0.bin"
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ];then
    ssh fusionstor-2 "bash /root/SS100-fusionstor-install-0.4.0.bin"
    ssh fusionstor-3 "bash /root/SS100-fusionstor-install-0.4.0.bin"

fi
mv /opt/fusionstack/etc/lich.conf /opt/
cat >> /opt/fusionstack/etc/lich.conf << EOF
globals {
    clustername fusionstack;
    nbd         1;
    nohosts    on;
    sheepdog   off;
    solomode   on;
    hsm    on;
    networks {
        172.20.0.1/16;
    }
}
chunk {
    disk_keep 10G;
}
EOF
scp /opt/fusionstack/etc/lich.conf fusionstor-1:/opt/fusionstack/etc/lich.conf
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ];then
    scp /opt/fusionstack/etc/lich.conf fusionstor-2:/opt/fusionstack/etc/lich.conf
    scp /opt/fusionstack/etc/lich.conf fusionstor-3:/opt/fusionstack/etc/lich.conf
fi

scp  /etc/hosts fusionstor-1:/opt/fusionstack/etc/hosts.conf
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ];then
    scp  /etc/hosts fusionstor-2:/opt/fusionstack/etc/hosts.conf
    scp  /etc/hosts fusionstor-3:/opt/fusionstack/etc/hosts.conf
fi

if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ];then
    ssh fusionstor-1 "echo \"\n\" | /opt/fusionstack/lich/bin/lich prep ${IP[0]} ${IP[1]} ${IP[2]}"
    ssh fusionstor-1 "/opt/fusionstack/lich/bin/lich create ${IP[0]} ${IP[1]} ${IP[2]}"
else
    ssh fusionstor-1 "echo \"\n\" | /opt/fusionstack/lich/bin/lich prep ${IP[0]}"
    ssh fusionstor-1 "/opt/fusionstack/lich/bin/lich create ${IP[0]}"
fi


ssh fusionstor-1 "lich list;lich.node --disk_list;lich.node --disk_add /dev/vdb /dev/vdc /dev/vdd --force"
if [ "${FUSIONSTOR_ONE_NODE}" != "yes" ];then
    ssh fusionstor-2 "lich list;lich.node --disk_list;lich.node --disk_add /dev/vdb /dev/vdc /dev/vdd --force"
    ssh fusionstor-3 "lich list;lich.node --disk_list;lich.node --disk_add /dev/vdb /dev/vdc /dev/vdd --force"
fi

ssh fusionstor-1 "lich stat"
if [ $? -ne 0 ];then
    exit 1
fi
