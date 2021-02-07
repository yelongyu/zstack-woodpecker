#!/bin/sh
#set -x

#IP address of VIP for mnha2
vip=172.20.16.242

#IP address of management nodes for mnha2
#for one node env, just put same address for the 2 variables
mn1_ip=172.20.16.242
mn2_ip=172.20.16.242

#password for management nodes ssh access
password=password

#uuid for existing L3 management and public network
management_network_uuid=110b3b6e36bc4204983ddb32feaa034e
public_network_uuid=110b3b6e36bc4204983ddb32feaa034e

#uuid for a L2 VLAN
l2_vlan_uuid=4397059dc0e241c3af4ba6c14d49099a

#uuid for an existing instance offering
instance_offering_uuid=65f555ff5c6b469da057a047cb236fff

#uuid for an existing image
image_uuid=75e6be2f62944501a204b653859a9416

#uuid for an existing l3 network for vm creation - optional
#if no set, will create a l3 network
#l3_uuid=b68586f8656146288228a015ca82a625
l3_uuid=

#timeout for all the checks
TIMEOUT=1200

#set to 1 to delete all the test resources
#set to 0 to keep all the test resources
CLEAR_ENV=1

label=`echo $RANDOM`
customized_network=0

ret=0

rand(){ 
	min=$1  
	max=$(($2-$min+1))  
	num=$(cat /dev/urandom | head -n 10 | cksum | awk -F ' ' '{print $1}')  
	echo $(($num%$max+$min))  
}  

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

check_mariadb(){
	ssh $1 service mariadb status | grep -i running | grep -i -q active
	if [ $? -ne 0 ]; then
		echo "host $1 has mariadb in wrong state, please check"
		exit 1
	fi

	ssh $1 service mariadb status | grep -v "log\-error" | grep -q -i -w "\<error\>"
	if [ $? -eq 0 ]; then
		echo "host $1 has error found in mariadb, please check"
		exit 1
	fi

	echo "host $1 has mariadb working fine"
	
}

echo "copy ssh rsa keys to $mn1_ip"
[ -f /root/.ssh/id_rsa ] || gen_ssh_keys
auto_ssh_copy_id $password $mn1_ip

echo "copy ssh rsa keys to $mn2_ip"
[ -f /root/.ssh/id_rsa ] || gen_ssh_keys
auto_ssh_copy_id $password $mn2_ip

check_mariadb $mn1_ip
check_mariadb $mn2_ip

echo "check login with vip $vip"
curl -s -H "Content-Type: application/json" -X PUT -d '{"logInByAccount":{"accountName":"admin","password":"b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86"}}' http://$vip:8080/zstack/v1/accounts/login | grep -i -q error

ret=$?

if [ $ret -eq 0 ]; then
	echo "fail to login vip $vip"
	exit 1
else
	echo "successfully to login vip $vip"
fi

session=`curl -s -H "Content-Type: application/json" -X PUT -d '{"logInByAccount":{"accountName":"admin","password":"b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86"}}' http://$vip:8080/zstack/v1/accounts/login | awk -F"\"" '{print $6}'`

sleep 1

echo "check host list with vip $vip"

curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/hosts | grep -i -q error

ret=$?

if [ $ret -eq 0 ]; then
	echo "fail to list all the hosts with $vip"
	exit 1
else
	echo "successfully to list all the hosts with vip $vip"
fi

sleep 1

echo "check vminstance list with vip $vip"

curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/vm-instances | grep -i -q error

ret=$?

if [ $ret -eq 0 ]; then
	echo "fail to list all the vminstances with $vip"
	exit 1
else
	echo "successfully to list all the vminstances with vip $vip"
fi

sleep 1

echo "get imagestore with vip $vip"

curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/backup-storage/image-store | grep -i -q connected

ret=$?

if [ $ret -ne 0 ]; then
	echo "fail to get imagestore with $vip, try to check ceph"
	curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/backup-storage/ceph | grep -i -q connected
	if [ $? -ne 0 ]; then
		echo "fail to get imagestore and ceph with $vip, please check"
		exit 1
	else
		backup_store=`curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/backup-storage/ceph | awk -F"Connected" '{print $1}' | awk -F"backupStorageUuid\":\"" '{print $2}' | awk -F"\"" '{print $1}'`
		echo "successfully to get ceph backupstore with vip $vip"
	fi
else
	backup_store=`curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/backup-storage/image-store | awk -F"Connected" '{print $1}' | awk -F"uuid\":\"" '{print $2}' | awk -F"\"" '{print $1}'`
	echo "successfully to get imagestore with vip $vip"
fi

sleep 1

echo "get zoneuuid from public network $public_network_uuid"

curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/l3-networks/$public_network_uuid | grep -i -q zoneuuid
if [ $? -eq 0 ]; then
	zoneuuid=`curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/l3-networks/$public_network_uuid | awk -F"zoneUuid\":\"" '{print $2}' | awk -F"\"" '{print $1}'`
	echo "successfully get zoneuuid $zoneuuid from public network $public_network_uuid"
else
	echo "fail to get zoneuuid from public network $public_network_uuid"
	exit 1
fi

sleep 1

if [ -z $l3_uuid ]; then
	customized_network=1
	echo "upload imagetemplate to backupstorage with vip $vip"
	
	vrouter_template_name=vrouter-template-"$label"
	vrouter_template_uuid=`uuidgen | sed 's/-//g'`
	
	curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X POST -d '{"params":{"name":"'"$vrouter_template_name"'","url":"http://192.168.200.100/mirror/diskimages/zstack-vrouter-latest.qcow2","mediaType":"RootVolumeTemplate","system":true,"format":"qcow2","platform":"Linux","backupStorageUuids":["'"$backup_store"'"],"resourceUuid":"'"$vrouter_template_uuid"'"}}' http://$vip:8080/zstack/v1/images > /dev/null 2>&1
	
	i=0
	
	while [ $i -lt $TIMEOUT ]
	do
		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/images/$vrouter_template_uuid | grep -q -i ready
		ret=$?
		if [ $ret -eq 0 ]; then
			echo ""
			echo "Image $vrouter_template_uuid is ready on backupstorage $backup_store through $vip after $i seconds"
			break
		fi
	
		i=$((i+1))
		echo -ne "."
		sleep 1
	done
	
	if [ $ret -ne 0 ]; then
		echo "Image $vrouter_template_uuid is not ready in $TIMEOUT seconds on backupstorage $backup_store through $vip"
		exit 1
	fi
	
	sleep 1
	
	echo "create virtual router with public network $public_network_uuid and management network $management_network_uuid"
	
	vrouter_name=vrouter-"$label"
	
	curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X POST -d '{"params":{"zoneUuid":"'"$zoneuuid"'","managementNetworkUuid":"'"$management_network_uuid"'","imageUuid":"'"$vrouter_template_uuid"'","publicNetworkUuid":"'"$public_network_uuid"'","isDefault":true,"name":"'"$vrouter_name"'","cpuNum":2.0,"memorySize":1073741824,"type":"VirtualRouter","systemTags":["vrouter"]}}' http://$vip:8080/zstack/v1/instance-offerings/virtual-routers > /dev/null 2>&1
	
	i=0
	
	while [ $i -lt $TIMEOUT ]
	do
		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/instance-offerings/virtual-routers | grep -i -q $vrouter_name
		ret=$?
	
		if [ $ret -eq 0 ]; then
			vrouter_uuid=`curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/instance-offerings/virtual-routers | awk -F"\",\"name\":\"$vrouter_name" '{print $1}' | awk -F"uuid\":\"" '{print $NF}'`
			echo ""
			echo "successfully to create virtual router $vrouter_uuid with public network $public_network_uuid and management network $management_network_uuid"
			break
		fi
	
		i=$((i+1))
		echo -ne "."
		sleep 1
	done
	
	if [ $ret -ne 0 ]; then
		echo "fail to create virtual router with public network $public_network_uuid and management network $management_network_uuid in $TIMEOUT seconds"
		exit 1
	fi
	
	sleep 1
	
	echo "create VPC with virtual router $vrouter_uuid"
	
	vpc_name=vpc-"$label"
	
	curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X POST -d '{"params":{"name":"'"$vpc_name"'","virtualRouterOfferingUuid":"'"$vrouter_uuid"'","description":"vpc for test"}}' http://$vip:8080/zstack/v1/vpc/virtual-routers > /dev/null 2>&1
	
	i=0
	
	while [ $i -lt $TIMEOUT ]
	do
		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/vm-instances?"q=name="$vpc_name | grep -i -q running > /dev/null 2>&1
		ret=$?
		if [ $ret -eq 0 ]; then
			echo ""
			echo "successfully create VPC with virtual router $vrouter_uuid after $i seconds"
			break
		fi
	
		i=$((i+1))
		echo -ne "."
		sleep 1
	done
	
	if [ $ret -ne 0 ]; then
		echo "fail to create VPC with virtual router $vrouter_uuid in $TIMEOUT seconds"
		exit 1
	fi
	
	sleep 1
	
	echo "create VPC network with vlan $l2_vlan_uuid"
	vpc_l3_name=vpc-l3-"$label"
	
	curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X POST -d '{"params":{"name":"'"$vpc_l3_name"'","type":"L3VpcNetwork","l2NetworkUuid":"'"$l2_vlan_uuid"'","category":"Private","system":false}}' http://$vip:8080/zstack/v1/l3-networks > /dev/null 2>&1
	
	i=0
	while [ $i -lt $TIMEOUT ]
	do
		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/l3-networks | grep -i -q $vpc_l3_name > /dev/null 2>&1
		ret=$?
		if [ $ret -eq 0 ]; then
			echo ""
			echo "successfully create VPC network with vlan $l2_vlan_uuid after $i seconds"
			break
		fi
	
		i=$((i+1))
		echo -ne "."
		sleep 1
	done
	
	if [ $ret -ne 0 ]; then
		echo "fail to create VPC network with vlan $l2_vlan_uuid in $TIMEOUT seconds"
		exit 1
	fi

	sleep 1
	
	l3_uuid=`curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/l3-networks | awk -F"\",\"name\":\"$vpc_l3_name" '{print $1}' | awk -F"\"" '{print $NF}'`
	vpc_instance_uuid=`curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/vm-instances?"q=name="$vpc_name | awk -F"\",\"name\":\"$vpc_name" '{print $1}' | awk -F"\"" '{print $NF}'`
	ip_range_name=ip-range-"$label"
	ip_range=`rand 0 255`
	
	echo "attach VPC l3 network $l3_uuid to vpc router $vpc_name with vpc uuid $vpc_instance_uuid"
	
	curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X POST -d '{"params":{"name":"'"$ip_range_name"'","startIp":"132.'"$ip_range"'.152.123","endIp":"132.'"$ip_range"'.152.150","netmask":"255.255.255.0","gateway":"132.'"$ip_range"'.152.1"}}' http://$vip:8080/zstack/v1/l3-networks/$l3_uuid/ip-ranges > /dev/null 2>&1
	sleep 1
	curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X POST -d '{"params":{}}' http://$vip:8080/zstack/v1/vm-instances/$vpc_instance_uuid/l3-networks/$l3_uuid > /dev/null 2>&1
	
	i=0
	while [ $i -lt $TIMEOUT ]
	do
		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/vm-instances?"q=name="$vpc_name | grep -i -q $l3_uuid > /dev/null 2>&1
		ret=$?
		if [ $ret -eq 0 ]; then
			echo ""
			echo "successfully attach VPC l3 network to vpc roter $vpc_name after $i seconds"
			break
		fi
	
		i=$((i+1))
		echo -ne "."
		sleep 1
	done
	
	if [ $ret -ne 0 ]; then
		echo "fail to attach VPC l3 network to vpc router $vpc_name with vpc uuid $vpc_instance_uuid in $TIMEOUT seconds"
		exit 1
	fi

fi

sleep 1

echo "create vminstance with l3 network $l3_uuid , instanceoffering $instance_offering_uuid , image $image_uuid"
vminstance_name=vm-"$label"

curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X POST -d '{"params":{"name":"'"$vminstance_name"'","instanceOfferingUuid":"'"$instance_offering_uuid"'","imageUuid":"'"$image_uuid"'","l3NetworkUuids":["'"$l3_uuid"'"],"strategy":"InstantStart"}}' http://$vip:8080/zstack/v1/vm-instances > /dev/null 2>&1

i=0
while [ $i -lt $TIMEOUT ]
do
	curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/vm-instances?"q=name="$vminstance_name | grep -i -q running > /dev/null 2>&1
	ret=$?
	if [ $ret -eq 0 ]; then
		echo ""
		echo "successfully create vminstance $vminstance_name with l3 network $l3_uuid , instanceoffering $instance_offering_uuid , image $image_uuid after $i seconds"
		break
	fi

	i=$((i+1))
	echo -ne "."
	sleep 1
done

if [ $ret -ne 0 ]; then
	echo "fail to create vminstance $vminstance_name with l3 network $l3_uuid , instanceoffering $instance_offering_uuid , image $image_uuid in $TIMEOUT seconds"
	exit 1
fi

sleep 1

echo "check zwatch vm cpu idle data is changing"

tmp1=`mktemp`
tmp2=`mktemp`
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/VM\&"metricName"=CPUIdleUtilization > $tmp1
sleep 5
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/VM\&"metricName"=CPUIdleUtilization > $tmp2

diff $tmp1 $tmp2 > /dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "VM CPU idle data is same after 5 seconds, please check"
	exit 1
else
	echo "VM CPU idle is passed"
fi

rm -rf $tmp1 $tmp2

echo "check zwatch vm disk read data is changing"

tmp1=`mktemp`
tmp2=`mktemp`
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/VM\&"metricName"=DiskReadOps > $tmp1
sleep 5
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/VM\&"metricName"=DiskReadOps > $tmp2

diff $tmp1 $tmp2 > /dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "VM Disk read data is same after 5 seconds, please check"
	exit 1
else
	echo "VM Disk read is passed"
fi

rm -rf $tmp1 $tmp2

echo "check zwatch vm disk write data is changing"

tmp1=`mktemp`
tmp2=`mktemp`
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/VM\&"metricName"=DiskWriteOps > $tmp1
sleep 5
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/VM\&"metricName"=DiskWriteOps > $tmp2

diff $tmp1 $tmp2 > /dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "VM Disk write data is same after 5 seconds, please check"
	exit 1
else
	echo "VM Disk write is passed"
fi

rm -rf $tmp1 $tmp2

echo "check zwatch vm nic in packets data is changing"

tmp1=`mktemp`
tmp2=`mktemp`
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/VM\&"metricName"=NetworkInPackets > $tmp1
sleep 5
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/VM\&"metricName"=NetworkInPackets > $tmp2

diff $tmp1 $tmp2 > /dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "VM nic in packets data is same after 5 seconds, please check"
	exit 1
else
	echo "VM nic in packets data is passed"
fi

rm -rf $tmp1 $tmp2

echo "check zwatch hosts nic in packets data is changing"

tmp1=`mktemp`
tmp2=`mktemp`
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/Host\&"metricName"=NetworkInPackets > $tmp1
sleep 5
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/Host\&"metricName"=NetworkInPackets > $tmp2

diff $tmp1 $tmp2 > /dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "Hosts nic in packets data is same after 5 seconds, please check"
	exit 1
else
	echo "Hosts nic in packets data is passed"
fi

rm -rf $tmp1 $tmp2

echo "check zwatch hosts cpu idle data is changing"

tmp1=`mktemp`
tmp2=`mktemp`
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/Host\&"metricName"=CPUIdleUtilization > $tmp1
sleep 5
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/Host\&"metricName"=CPUIdleUtilization > $tmp2

diff $tmp1 $tmp2 > /dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "Hosts CPU idle data is same after 5 seconds, please check"
	exit 1
else
	echo "Hosts CPU idle is passed"
fi

rm -rf $tmp1 $tmp2

echo "check zwatch hosts disk read data is changing"

tmp1=`mktemp`
tmp2=`mktemp`
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/Host\&"metricName"=DiskReadOps > $tmp1
sleep 5
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/Host\&"metricName"=DiskReadOps > $tmp2

diff $tmp1 $tmp2 > /dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "Hosts Disk read data is same after 5 seconds, please check"
	exit 1
else
	echo "Hosts Disk read is passed"
fi

rm -rf $tmp1 $tmp2

echo "check zwatch hosts disk write data is changing"

tmp1=`mktemp`
tmp2=`mktemp`
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/Host\&"metricName"=DiskWriteOps > $tmp1
sleep 5
curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/zwatch/metrics?"namespace"=ZStack/Host\&"metricName"=DiskWriteOps > $tmp2

diff $tmp1 $tmp2 > /dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "Hosts Disk write data is same after 5 seconds, please check"
	exit 1
else
	echo "Hosts Disk write is passed"
fi

rm -rf $tmp1 $tmp2

sleep 1

if [ $CLEAR_ENV -eq 1 ]; then
	echo "start to clear test environment"
	echo "try to delete the vm instance $vminstance_name"

	vminstance_uuid=`curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/vm-instances?"q=name="$vminstance_name | awk -F"uuid\":\"" '{print $2}' | awk -F"\"" '{print $1}'`

	curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X DELETE http://$vip:8080/zstack/v1/vm-instances/$vminstance_uuid?deleteMode=Permissive | grep -i -q error > /dev/null 2>&1

	ret=$?
	
	if [ $ret -eq 0 ]; then
		echo "fail to delete vminstance $vminstance_uuid"
		exit 1
	else
		echo "successfully to delete vminstance $vminstance_uuid"
	fi

	sleep 1

	echo "try to expunge the vm instance $vminstance_name"

	curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X PUT -d '{"expungeVmInstance":{}}' http://$vip:8080/zstack/v1/vm-instances/$vminstance_uuid/actions > /dev/null 2>&1

	i=0

	while [ $i -lt $TIMEOUT ]
	do
		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/vm-instances?"q=name="$vminstance_name | grep -i -q $vminstance_name > /dev/null 2>&1
		ret=$?
		if [ $ret -eq 0 ]; then
			echo ""
			echo "successfully expunge vminstance $vminstance_name after $i seconds"
			break
		fi
	
		i=$((i+1))
		echo -ne "."
		sleep 1
	done
	
	if [ $ret -ne 0 ]; then
		echo "fail to expunge vminstance $vminstance_name in $TIMEOUT seconds"
		exit 1
	fi

	if [ $customized_network -eq 1 ]; then
		echo "try to delete l3 network $l3_uuid"
		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X DELETE http://$vip:8080/zstack/v1/l3-networks/$l3_uuid?deleteMode=Permissive

		i=0

		while [ $i -lt $TIMEOUT ]
		do
			curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/l3-networks | grep -i -q $l3_uuid > /dev/null 2>&1
			ret=$?
			if [ $ret -ne 0 ]; then
				echo ""
				echo "successfully delete VPC network $l3_uuid after $i seconds"
				break
			fi
		
			i=$((i+1))
			echo -ne "."
			sleep 1
		done
		
		if [ $ret -eq 0 ]; then
			echo "fail to delete VPC network $l3_uuid in $TIMEOUT seconds"
			exit 1
		fi

		sleep 1

		echo "try to delete VPC virtual router $vpc_name"
	
		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X DELETE http://$vip:8080/zstack/v1/vm-instances/$vpc_instance_uuid > /dev/null 2>&1
	
		i=0
	
		while [ $i -lt $TIMEOUT ]
		do
			curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/vm-instances?"q=name="$vpc_name | grep -i -q $vpc_name > /dev/null 2>&1
			ret=$?
			if [ $ret -ne 0 ]; then
				echo ""
				echo "successfully delete VPC virtual router $vpc_name after $i seconds"
				break
			fi
		
			i=$((i+1))
			echo -ne "."
			sleep 1
		done
		
		if [ $ret -eq 0 ]; then
			echo "fail to delete VPC virtual router $vpc_name in $TIMEOUT seconds"
			exit 1
		fi

		sleep 1
	
		echo "try to delete virtual router instance offering $vrouter_name"
		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X DELETE http://$vip:8080/zstack/v1/instance-offerings/$vrouter_uuid > /dev/null 2>&1
	
		i=0
	
		while [ $i -lt $TIMEOUT ]
		do
			curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/instance-offerings/virtual-routers | grep -i -q $vrouter_name > /dev/null 2>&1
			ret=$?
		
			if [ $ret -ne 0 ]; then
				echo ""
				echo "successfully to delete virtual router instance offering $vrouter_name after $i seconds"
				break
			fi
		
			i=$((i+1))
			echo -ne "."
			sleep 1
		done
		
		if [ $ret -eq 0 ]; then
			echo "fail to delete virtual router instance offering $vrouter_name in $TIMEOUT seconds"
			exit 1
		fi

		sleep 1

		echo "try to delete imagetemplate $vrouter_template_name"
	
		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X DELETE http://$vip:8080/zstack/v1/images/$vrouter_template_uuid?backupStorageUuids=$backup_store&deleteMode=Permissive

		sleep 1

		curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X PUT -d '{"expungeImage":{"backupStorageUuids":["'"$backup_store"'"]}}' http://$vip:8080/zstack/v1/images/$vrouter_template_uuid/actions

		i=0
		
		while [ $i -lt $TIMEOUT ]
		do
			curl -s -H "Content-Type: application/json" -H "Authorization: OAuth $session" -X GET http://$vip:8080/zstack/v1/images/$vrouter_template_uuid | grep -q -i $vrouter_template_uuid > /dev/null 2>&1
			ret=$?
			if [ $ret -ne 0 ]; then
				echo ""
				echo "successfully delete Image $vrouter_template_uuid after $i seconds"
				break
			fi
		
			i=$((i+1))
			echo -ne "."
			sleep 1
		done
		
		if [ $ret -eq 0 ]; then
			echo "fail to delete Image $vrouter_template_uuid in $TIMEOUT on backupstorage $backup_store"
			exit 1
		fi
	fi

	echo "successfully clean up the test env"

fi

echo "zstack service check passed!"
