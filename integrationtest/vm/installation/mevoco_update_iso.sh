#!/bin/bash
#set -x
mkdir -p /opt/zstack-dvd && cd /opt/

#wget -q –progress=TYPE  http://172.20.198.234/mirror/zstack_enterprise_iso_1.9/latest/ 2>/dev/null
wget -q –progress=TYPE  http://172.20.198.234/mirror/zstack_enterprise_iso_2.0/latest/ 2>/dev/null
sleep 3
latest_iso=$(cat index.html |awk -F '[><]' '/DVD/ {print $5}')
#wget -q –progress=TYPE  http://172.20.198.234/mirror/zstack_enterprise_iso_1.9/latest/$latest_iso 2>/dev/null
wget -q –progress=TYPE  http://172.20.198.234/mirror/zstack_enterprise_iso_2.0/latest/$latest_iso 2>/dev/null
rm -f index.html

wget http://cdn.zstack.io/product_downloads/scripts/zstack-upgrade 2>/dev/null
sleep 3
bash zstack-upgrade -r $latest_iso 2>/dev/null

zstack-ctl stop 2>/dev/null
sleep 20
yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev clean all 2>/dev/null
yum -y clean all 2>/dev/null
yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev update 2>/dev/null

#rm -f $latest_iso
#rm -f zstack-upgrade 
