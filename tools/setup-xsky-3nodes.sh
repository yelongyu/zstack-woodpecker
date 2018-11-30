#!/usr/bin/bash
set -x
export PS4='+[#$LINENO ${FUNCNAME[0]}() $BASH_SOURCE] '

declare -a IP
IP[0]=$1
IP[1]=$2
IP[2]=$3
#cd /tmp
wget http://192.168.200.100/mirror/pengtao/cluster.json
#wget http://192.168.200.100/mirror/pengtao/sds-installer-3.2.14.3_Zstack_WithLicense.tar.gz
wget http://192.168.200.100/mirror/pengtao/oem-x-ebs-basic-installer-3.2.15.1_RTMVersion_ZStack_WithLicense.tar.gz
tar zxvf oem-x-ebs-basic-installer-3.2.15.1_RTMVersion_ZStack_WithLicense.tar.gz

sed -i "s/10.0.0.x/${IP[0]}/" tools/ansible/hosts
sed -i "s/10.0.1.x/${IP[1]}/" tools/ansible/hosts
sed "4 i${IP[2]}" -i tools/ansible/hosts
sed -i 's/passwd/password/' tools/ansible/hosts
sed -i 's/set_hostname: false/set_hostname: true/' tools/ansible/group_vars/nodes
sed '10 idisable_firewalld: true' -i tools/ansible/group_vars/nodes
#sed -i 's/hostname_prefix: sds/hostname_prefix: ceph/' tools/ansible/group_vars/nodes
sed -i "s/172.20.196.210/${IP[0]}/g" cluster.json
sed -i "s/172.20.195.198/${IP[1]}/g" cluster.json
sed -i "s/172.20.198.209/${IP[2]}/g" cluster.json

sshpass -p password  ssh root@${IP[1]} "rm -f /root/.ssh/id_rsa*"
sshpass -p password  ssh root@${IP[2]} "rm -f /root/.ssh/id_rsa*"
sshpass -p password  ssh root@${IP[0]} "rm -f /root/.ssh/id_rsa*"
#sshpass -p password ssh root@172.20.195.153 "ls /root"
[ ! -f /root/.ssh/id_rsa ] && ssh-keygen -q -t rsa -N "" -f /root/.ssh/id_rsa
sleep 2

cd tools
bash prepare.sh -i ansible/hosts
if [ $? -eq 0 ];then
	sleep 1
        cd ..
        bash install.sh ${IP[0]}
        if [ $? -eq 0 ];then
		sleep 1
                init_admin_token=`cat /etc/xms/initial-admin-token`
                sds-formation -f cluster.json -t $init_admin_token
                if [ $? -ne 0 ];then
                        echo "setup cluster failed"
                fi
        else
                echo "Install xsky failed"
        fi
else
        echo "Prepare setup environment failed"
fi
