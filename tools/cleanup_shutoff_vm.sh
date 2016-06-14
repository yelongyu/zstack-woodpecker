#!/bin/bash
# Help to destroy all VMs and their storages in the system.

virsh list >/dev/null 2>&1
if [ $? -eq 0 ];then
    echo "This is KVM system. We are going to delete all VMs by virsh commands."
else
    echo "\`virsh list\` command failed. exit".
    #Should add more hypervisor supporting in the future.
fi

vm_lists=`virsh list --inactive|sed -n '3,$p'|sed '/^$/d' | awk '{print $2}'`

if [ -z "$vm_lists" ];then
    echo "No VMs are found. Exit. "
    exit 0
fi

for vm in $vm_lists;do
    echo " Destroy $vm ..."
    virsh destroy $vm >/dev/null 2>&1
    virsh undefine --remove-all-storage $vm >/dev/null 2>&1
done

echo "Finish VMs cleanup!"
