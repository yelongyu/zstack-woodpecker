'''
test for checking if vm exist in newly add vcenter
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import test_stub
import os


vcenter1_name = "VCENTER1"
vcenter1_domain_name = "172.20.76.251"
vcenter1_username = "administrator@vsphere.local"
vcenter1_password = "Testing%123"

vcenter_uuid = None

def shadow_create_vm():
    """
    This function is to execute a create vm on another remote woodpecker, 
    which also attached the same vcenter.
    """

    shadow_vm_ip = os.environ.get('serverIp2')
    cmd = "cd /home/%s/zstack-woodpecker/dailytest/ && python ./zstest.py -c vcenter/remote_vm_create.py" %(shadow_vm_ip)
    ret, output, stderr = ssh.execute(cmd, shadow_vm_ip, "root", "password", False, 22)
    if ret != 0:
        test_util.test_fail("remote create vm failed: output:%s; stderr:%s" %(output, stderr))


def shadow_delete_vm():
    """
    This function is to execute a delete the vm named "vm-crt-via-rmt-mevoco" on another remote woodpecker, 
    which also attached the same vcenter.
    """

    shadow_vm_ip = os.environ.get('serverIp2')
    cmd = "cd /home/%s/zstack-woodpecker/dailytest/ && python ./zstest.py -c vcenter/remote_vm_delete.py" %(shadow_vm_ip)
    ret, output, stderr = ssh.execute(cmd, shadow_vm_ip, "root", "password", False, 22)
    if ret != 0:
        test_util.test_fail("remote delete vm 'vm-crt-via-rmt-mevoco' failed: output:%s; stderr:%s" %(output, stderr))


def shadow_start_vm():
    """
    this function is to execute a start vm on another remote woodpecker, 
    which also attached the same vcenter.
    """

    shadow_vm_ip = os.environ.get('serverip2')
    cmd = "cd /home/%s/zstack-woodpecker/dailytest/ && python ./zstest.py -c vcenter/remote_vm_start.py" %(shadow_vm_ip)
    ret, output, stderr = ssh.execute(cmd, shadow_vm_ip, "root", "password", false, 22)
    if ret != 0:
        test_util.test_fail("remote start vm failed: output:%s; stderr:%s" %(output, stderr))


def shadow_stop_vm():
    """
    this function is to execute a stop vm on another remote woodpecker, 
    which also attached the same vcenter.
    """

    shadow_vm_ip = os.environ.get('serverip2')
    cmd = "cd /home/%s/zstack-woodpecker/dailytest/ && python ./zstest.py -c vcenter/remote_vm_stop.py" %(shadow_vm_ip)
    ret, output, stderr = ssh.execute(cmd, shadow_vm_ip, "root", "password", false, 22)
    if ret != 0:
        test_util.test_fail("remote stop vm failed: output:%s; stderr:%s" %(output, stderr))



vm_name = "vm-crt-via-rmt-mevoco"

def test():
    global vcenter_uuid

    #add vcenter senario1:
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid = inv.uuid

    if vcenter_uuid == None:
        test_util.test_fail("vcenter_uuid is None")


    shadow_create_vm()
    vm_cond = res_ops.gen_query_conditions("name", '=', vm_name)
    vm_uuid = res_ops.query_resource_fields(res_ops.VM_INSTANCE, vm_cond, None, fields=['uuid'])[0].uuid
    if not vm_uuid:
        test_util.test_fail("vcenter sync create vm failed.")


    shadow_start_vm()
    vm_cond = res_ops.gen_query_conditions("name", '=', vm_name)
    vm_state = res_ops.query_resource_fields(res_ops.VM_INSTANCE, vm_cond, None, fields=['state'])[0].state
    if vm_state != "Running":
        test_util.test_fail("vcenter sync vm start failed.")


    shadow_stop_vm()
    vm_cond = res_ops.gen_query_conditions("name", '=', vm_name)
    vm_state = res_ops.query_resource_fields(res_ops.VM_INSTANCE, vm_cond, None, fields=['uuid'])[0].state
    if vm_state != "Stopped":
        test_util.test_fail("vcenter sync vm stop failed.")



    shadow_delete_vm()


    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("vcenter sync start and stop vm test passed.")



def error_cleanup():
    global vcenter_uuid

    shadow_delete_vm()
    if vcenter_uuid:
        vct_ops.delete_vcenter(vcenter_uuid)
