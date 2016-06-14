#!/bin/bash
zstack-cli LogInByAccount accountName=admin password=password
hosts=`zstack-cli QueryHost status=Connected|jq '.inventories[].uuid'`

for host in $hosts; do
	host_ip=`zstack-cli QueryHost uuid=$host status=Connected|jq '.inventories[].managementIp'`
	host_ip=`echo $host_ip|tr -d '"'`
	vm_uuids=`ssh $host_ip "virsh list|tail -n +3|awk '{print \\$2}'"`
	for vm_uuid in $vm_uuids; do
		vm=`zstack-cli QueryVmInstance uuid=$vm_uuid|jq '.inventories[].uuid'`
		[ -z $vm ] && echo invalid vm found in $host_ip: $vm_uuid
	done
done
zstack-cli LogOut
