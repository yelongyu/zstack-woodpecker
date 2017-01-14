#!/bin/bash
#set -x
mkdir -p /opt/zstack-dvd && cd /opt/

wget -q –progress=TYPE  http://172.20.198.234/mirror/mevoco_iso/latest/ 2>/dev/null
sleep 3
latest_iso=$(cat index.html |awk -F '[><]' '/DVD/ {print $5}')
wget -q –progress=TYPE  http://172.20.198.234/mirror/mevoco_iso/latest/$latest_iso 2>/dev/null
rm -f index.html

wget http://www.mevoco.com/downloads/scripts/zstack-repo-upgrade.sh 2>/dev/null
sleep 3
bash zstack-repo-upgrade.sh $latest_iso 2>/dev/null

zstack-ctl stop 2>/dev/null
sleep 20
yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev clean all 2>/dev/null
yum -y clean all 2>/dev/null
yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev update 2>/dev/null

rm -f $latest_iso
rm -f zstack-repo-upgrade.sh
