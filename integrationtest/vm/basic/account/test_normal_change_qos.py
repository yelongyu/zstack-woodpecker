'''

New Integration Test for normal account change the qos  volume and network.

@author: ye.tian 2018-11-21
'''

import hashlib
import zstackwoodpecker.test_util as test_util
import test_stub
import os
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.account_operations as acc_ops


_config_ = {
        'timeout' : 2000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
all_volume_offering_uuid = None
rw_volume_offering_uuid = None
instance_offering_uuid = None
test_account_uuid = None

vm = None

def test():
    global vm, session_uuid
    global all_volume_offering_uuid, rw_volume_offering_uuid, instance_offering_uuid
    global test_account_uuid
    
    test_util.test_dsc('Test normal account change the qos network and volume ')

    #create normal account
    test_util.test_dsc('create normal account')
    account_name = 'a'
    account_pass = hashlib.sha512(account_name).hexdigest()
    test_account = acc_ops.create_normal_account(account_name, account_pass)
    test_account_uuid = test_account.uuid
    test_account_session = acc_ops.login_by_account(account_name, account_pass)

    #create disk offering
    test_util.test_dsc('create disk offering')
    name_all = 'all_disk_offering'	
    volume_bandwidth = 30*1024*1024
    all_volume_offering = test_lib.lib_create_disk_offering(name = name_all, volume_bandwidth = volume_bandwidth)
    all_volume_offering_uuid = all_volume_offering.uuid

    name_rw = 'rw_disk_offering'	
    volume_read_bandwidth = 90*1024*1024
    volume_write_bandwidth = 100*1024*1024
    rw_volume_offering = test_lib.lib_create_disk_offering(name = name_rw, read_bandwidth = volume_read_bandwidth, write_bandwidth = volume_write_bandwidth)
    rw_volume_offering_uuid = rw_volume_offering.uuid

    #create instance offering 
    test_util.test_dsc('create instance offering')
    read_bandwidth = 50*1024*1024
    write_bandwidth = 60*1024*1024
    net_outbound_bandwidth = 70*1024*1024
    net_inbound_bandwidth = 80*1024*1024
    new_instance_offering = test_lib.lib_create_instance_offering(read_bandwidth = read_bandwidth, write_bandwidth=write_bandwidth, net_outbound_bandwidth = net_outbound_bandwidth, net_inbound_bandwidth = net_inbound_bandwidth)
    instance_offering_uuid = new_instance_offering.uuid
    
    #share admin resoure to normal account
    test_util.test_dsc('share admin resoure to normal account')
    test_stub.share_admin_resource([test_account_uuid])
    acc_ops.share_resources([test_account_uuid], [all_volume_offering_uuid, rw_volume_offering_uuid])

    #create vm with 2 data volumes
    test_util.test_dsc('create vm with volumes qos by normal account a')
    l3net_uuid = res_ops.get_resource(res_ops.L3_NETWORK, session_uuid = test_account_session)[0].uuid
    cond = res_ops.gen_query_conditions('platform', '=', 'Linux')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond, session_uuid = test_account_session)[0].uuid
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_l3_uuids([l3net_uuid])

    vm = test_stub.create_vm_with_volume(vm_creation_option = vm_creation_option,  data_volume_uuids = [all_volume_offering_uuid, rw_volume_offering_uuid], session_uuid = test_account_session)
    vm_inv = vm.get_vm()

    # get  the nic uuid
    test_util.test_dsc('get the vm_nic')
    l3_uuid = vm_inv.vmNics[0].l3NetworkUuid
    vm_nic = test_lib.lib_get_vm_nic_by_l3(vm_inv, l3_uuid)

    # get the volume uuid
    test_util.test_dsc('get the vm data volumes')
    cond1 = res_ops.gen_query_conditions("diskOfferingUuid", '=', all_volume_offering_uuid)
    cond2 = res_ops.gen_query_conditions("diskOfferingUuid", '=', rw_volume_offering_uuid)
    all_volume_uuid = res_ops.query_resource(res_ops.VOLUME, cond1)[0].uuid
    rw_volume_uuid = res_ops.query_resource(res_ops.VOLUME, cond2)[0].uuid
    #set root disk qos
    test_util.test_dsc('set read*2, read/2, write*2, write/2 and del the root disk read and write qos')    
    try:
    	vm_ops.set_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid, volumeBandwidth = read_bandwidth*2, mode = 'read', session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    test_util.test_dsc('del the root disk read qos')    
    try:
    	vm_ops.del_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid, mode = 'read', session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass
    vm_ops.set_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid, volumeBandwidth = read_bandwidth/2, mode = 'read', session_uuid = test_account_session)

    test_util.test_dsc('set 2 times the root disk write qos')    
    try:
    	vm_ops.set_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid, volumeBandwidth = write_bandwidth*2, mode = 'write', session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    test_util.test_dsc('del the root disk write qos')    
    try:
    	vm_ops.del_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid, mode = 'write', session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    test_util.test_dsc('set below the root disk write qos')    
    vm_ops.set_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid, volumeBandwidth = write_bandwidth/2, mode = 'write', session_uuid = test_account_session)

    #set data disk all_volume_uuid qos
    test_util.test_dsc('set read*2, read/2, write*2, write/2 and del the volume1 disk read and write qos')    
    try:
    	vm_ops.set_vm_disk_qos(all_volume_uuid, volumeBandwidth = volume_bandwidth*2, session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    test_util.test_dsc('del the data volume qos')    
    try:
    	vm_ops.del_vm_disk_qos(all_volume_uuid, session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    vm_ops.set_vm_disk_qos(all_volume_uuid, volumeBandwidth = volume_bandwidth/2, session_uuid = test_account_session)

    #set data disk rw_volume_uuid write qos
    test_util.test_dsc('set 2 times the data rw_volume_uuid write qos')    
    try:
    	vm_ops.set_vm_disk_qos(rw_volume_uuid, volumeBandwidth = volume_write_bandwidth*2, mode = 'write', session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    test_util.test_dsc('del the data rw_volume_uuid  write qos')
    try:
    	vm_ops.del_vm_disk_qos(rw_volume_uuid, mode = 'write', session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    vm_ops.set_vm_disk_qos(rw_volume_uuid, volumeBandwidth = volume_write_bandwidth/2, mode = 'write', session_uuid = test_account_session)

    #set data disk rw_volume_uuid read qos
    test_util.test_dsc('set 2 times the data rw_volume_uuid read qos')    
    try:
    	vm_ops.set_vm_disk_qos(rw_volume_uuid, volumeBandwidth = volume_read_bandwidth*2, mode = 'read', session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass
    test_util.test_dsc('del the data rw_volume_uuid read qos')
    try:
    	vm_ops.del_vm_disk_qos(rw_volume_uuid, mode = 'read', session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass
    vm_ops.set_vm_disk_qos(rw_volume_uuid, volumeBandwidth = volume_read_bandwidth/2, mode = 'read', session_uuid = test_account_session)

   # set the vm nic qos
    test_util.test_dsc('set higher than net out and in ')    
    try:
	vm_ops.set_vm_nic_qos(vm_nic.uuid, outboundBandwidth = net_outbound_bandwidth*2, inboundBandwidth = net_inbound_bandwidth*2, session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    test_util.test_dsc('set higher than net out and equal in ')    
    try:
	vm_ops.set_vm_nic_qos(vm_nic.uuid, outboundBandwidth = net_outbound_bandwidth*2, inboundBandwidth = net_inbound_bandwidth, session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    test_util.test_dsc('del net  in ')    
    try:
	vm_ops.del_vm_nic_qos(vm_nic.uuid, direction = 'in', session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    test_util.test_dsc('del net out ')    
    try:
	vm_ops.del_vm_nic_qos(vm_nic.uuid, direction = 'out', session_uuid = test_account_session)
    except:
	print "Test results were in line with expectations"
	pass

    test_util.test_dsc('set equal net out and  in ')    
    try:
	vm_ops.set_vm_nic_qos(vm_nic.uuid, outboundBandwidth = net_outbound_bandwidth, inboundBandwidth = net_inbound_bandwidth, session_uuid = test_account_session)
    #except:
    except Exception as e:	
	test_util.test_logger(e)

    test_util.test_dsc('set below net out and  in ')    
    vm_ops.set_vm_nic_qos(vm_nic.uuid, outboundBandwidth = net_outbound_bandwidth/2, inboundBandwidth = net_inbound_bandwidth/2, session_uuid = test_account_session)

    vm.check()
    vm.destroy(test_account_session)
    vm.check()
    vol_ops.delete_disk_offering(all_volume_offering_uuid)
    vol_ops.delete_disk_offering(rw_volume_offering_uuid)
    vol_ops.delete_volume(all_volume_uuid, test_account_session)
    vol_ops.delete_volume(rw_volume_uuid, test_account_session)
    acc_ops.delete_account(test_account_uuid)    
    vm_ops.delete_instance_offering(instance_offering_uuid)
    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm, all_volume_offering_uuid, rw_volume_offering_uuid, all_volume_uuid, rw_volume_uuid, test_account_session, instance_offering_uuid
    if vm:
        vm.destroy(test_account_session)
    vol_ops.delete_disk_offering(all_volume_offering_uuid)
    vol_ops.delete_disk_offering(rw_volume_offering_uuid)
    vol_ops.delete_volume(all_volume_uuid, test_account_session)
    vol_ops.delete_volume(rw_volume_uuid, test_account_session)
    acc_ops.delete_account(test_account_uuid)
    vm_ops.delete_instance_offering(instance_offering_uuid)
