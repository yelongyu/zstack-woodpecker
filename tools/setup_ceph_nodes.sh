#!/bin/bash
set -x
export PS4='+[#$LINENO ${FUNCNAME[0]}() $BASH_SOURCE] '

#declare -a IP
#IP[0]=$1
#IP[1]=$2

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

yum --disablerepo=* --enablerepo=zstack-local,ceph-hammer -y install ceph ceph-deploy ntp expect>/dev/null 2>&1
HOST_IP=`ip addr show eth0 | sed -n '3p' | awk '{print $2}' | awk -F / '{print $1}'`

echo " $HOST_IP ceph-1 ">>/etc/hosts
#echo " ${IP[0]} ceph-2 ">>/etc/hosts
#echo " ${IP[1]} ceph-3 ">>/etc/hosts
cat /etc/hosts | sort -u >/etc/host-tmp
mv /etc/host-tmp /etc/hosts
sleep 2

[  -f /root/.ssh/id_rsa ] || gen_ssh_keys
auto_ssh_copy_id password ceph-1
#auto_ssh_copy_id password ceph-2
#auto_ssh_copy_id password ceph-3

scp /etc/hosts ceph-1:/etc/hosts
#scp /etc/hosts ceph-2:/etc/hosts
#scp /etc/hosts ceph-3:/etc/hosts

ssh  ceph-1 hostnamectl set-hostname ceph-1 && export HOSTNAME=ceph-1
#ssh  ceph-2 hostnamectl set-hostname ceph-2 && export HOSTNAME=ceph-2
#ssh  ceph-3 hostnamectl set-hostname ceph-3 && export HOSTNAME=ceph-3

#ssh  ceph-2 yum --disablerepo=* --enablerepo=zstack-local,ceph-hammer -y install ceph ceph-deploy ntp expect>/dev/null 2>&1
#ssh  ceph-3 yum --disablerepo=* --enablerepo=zstack-local,ceph-hammer -y install ceph ceph-deploy ntp expect>/dev/null 2>&1

ssh ceph-1 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
#ssh ceph-2 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"
#ssh ceph-3 "iptables -F && service iptables save && systemctl restart ntpd && systemctl enable ntpd.service"

ssh ceph-1 "systemctl disable firewalld; systemctl stop firewalld"
#ssh ceph-2 "systemctl disable firewalld; systemctl stop firewalld"
#ssh ceph-3 "systemctl disable firewalld; systemctl stop firewalld"

ssh ceph-1 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
#ssh ceph-2 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"
#ssh ceph-3 "sed -i s'/SELINUX=enforcing/SELINUX=disabled'/g /etc/sysconfig/selinux"



ceph-deploy new ceph-1
cat >> ceph.conf << EOF
osd_pool_default_size = 1
osd_pool_default_min_size = 1
osd_pool_default_pg_num = 128
osd_pool_default_pgp_num = 128
osd_max_backfills = 1
osd_recovery_max_active = 1
osd crush update on start = 0
rbd_default_format = 2
debug_ms = 0
debug_osd = 0
osd_recovery_max_single_start = 1
filestore_max_sync_interval = 15
filestore_min_sync_interval = 10
filestore_queue_max_ops = 65536
filestore_queue_max_bytes = 536870912
filestore_queue_committing_max_bytes = 536870912
filestore_queue_committing_max_ops = 65536
filestore_wbthrottle_xfs_bytes_start_flusher = 419430400
filestore_wbthrottle_xfs_bytes_hard_limit = 4194304000
filestore_wbthrottle_xfs_ios_start_flusher = 5000
filestore_wbthrottle_xfs_ios_hard_limit = 50000
filestore_wbthrottle_xfs_inodes_start_flusher = 5000
filestore_wbthrottle_xfs_inodes_hard_limit = 50000
journal_max_write_bytes = 1073714824
journal_max_write_entries = 5000
journal_queue_max_ops = 65536
journal_queue_max_bytes = 536870912
osd_client_message_cap = 65536
osd_client_message_size_cap = 524288000
ms_dispatch_throttle_bytes = 536870912
filestore_fd_cache_size = 4096
osd_op_threads = 10
osd_disk_threads = 2
filestore_op_threads = 6
osd_client_op_priority = 100
osd_recovery_op_priority = 5
osd crush chooseleaf type = 0
EOF

for I in `seq 3`; do
	ceph-deploy --overwrite-conf mon create ceph-1
	sleep 3
	ceph-deploy --overwrite-conf config push ceph-1
	sleep 3
	ceph-deploy gatherkeys ceph-1
	sleep 3
	ceph-deploy --overwrite-conf osd create ceph-1:/dev/vdb
	ceph-deploy --overwrite-conf osd activate \
	ceph-1:/dev/vdb1:/dev/vdb2
	
	ceph-deploy --overwrite-conf config push ceph-1
	
	ceph osd crush add-bucket ceph-1 host
	
	ceph osd crush move ceph-1 root=default
	ceph osd crush create-or-move osd.0 1.0 host=ceph-1 root=default
	
	ceph -s | grep '1 osds: 1 up, 1 in'
	if [ $? -eq 0 ]; then
		break
	fi
done
