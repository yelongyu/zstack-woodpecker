'''
New Test For bill Operations
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.billing_operations as bill_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import threading
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def create_bill(price, resource_name, time_unit, resource_unit):
    test_util.test_logger('Create resource price')
    inv = bill_ops.create_resource_price(resource_name, time_unit, price, resource_unit).dateInLong
    return inv 

def query_resource_price(uuid = None, price = None, resource_name = None, time_unit = None, resource_unit = None):
    cond = []
    if uuid:
        cond = res_ops.gen_query_conditions('uuid', "=", uuid, cond)
    if price:
        cond = res_ops.gen_query_conditions('price', "=", price, cond)
    if resource_name:
        cond = res_ops.gen_query_conditions('resourceName', "=", resource_name, cond)
    if time_unit:
        cond = res_ops.gen_query_conditions('timeUnit', "=", time_unit, cond)
    if resource_unit:
        cond = res_ops.gen_query_conditions('resourceUnit', "=", resource_unit, cond)
    result = bill_ops.query_resource_price(cond)
    return result

def delete_price(price_uuid, delete_mode = None):
    test_util.test_logger('Delete resource price')
    result = bill_ops.delete_resource_price(price_uuid, delete_mode)
    return result

def create_vm(name, image_uuid, host_uuid, instance_offering_uuid, l3_uuid, session_uuid=None):
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_name(name)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_l3_uuids([l3_uuid])
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_stub.create_vm(vm_creation_option)
    return vm

def test():
    cond = res_ops.gen_query_conditions('system', '=',  'false')
    imageUuid = res_ops.query_resource_fields(res_ops.IMAGE, cond)[0].uuid
    cond = res_ops.gen_query_conditions('type', '=',  'UserVm')
    instanceOfferingUuid = res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING, cond)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=',  'public network')
    l3NetworkUuids = res_ops.query_resource_fields(res_ops.L3_NETWORK, cond)[0].uuid
    vm_name = 'vm-1'
    create_bill(1, "pubIpVmNicBandwidthIn", "s", "m")
    resourcePrices = query_resource_price()
    for resource_price in resourcePrices:
        delete_price(resource_price.uuid)

    ##parallel create bill
    counter = 0
    for i in range(0, 200):
        ipin = threading.Thread(target=create_bill, args=(i, "pubIpVmNicBandwidthIn", "s", "k"))
        ipout = threading.Thread(target=create_bill, args=(i, "pubIpVmNicBandwidthOut", "m", "m"))
        vipin = threading.Thread(target=create_bill, args=(i, "pubIpVipBandwidthIn", "h", "g"))
        vipout = threading.Thread(target=create_bill, args=(i, "pubIpVipBandwidthOut", "d", "m"))
        while threading.active_count() > 10:
            time.sleep(3)

        ipin.start()
        ipout.start()
        vipin.start()
        vipout.start()

    #Delete all price

    resourcePrices = query_resource_price()

    ##wait 15s for all prices created
    i = 0
    while len(resourcePrices) != 800:
        print len(resourcePrices)
        time.sleep(3)
        if i > 5:
            test_util.test_fail("Fail to create 800 prices")
        i = i + 1
        resourcePrices = query_resource_price()

    #Delete all price
    for resource_price in resourcePrices:
        delete_price(resource_price.uuid)

    ipin = threading.Thread(target=create_bill, args=(10, "pubIpVmNicBandwidthIn", "s", "m"))
    ipout = threading.Thread(target=create_bill, args=(10, "pubIpVmNicBandwidthOut", "s", "m"))
    vipin = threading.Thread(target=create_bill, args=(10, "pubIpVipBandwidthIn", "s", "m"))
    vipout = threading.Thread(target=create_bill, args=(10, "pubIpVipBandwidthOut", "s", "m"))
    ipin.start()
    ipout.start()
    vipin.start()
    vipout.start()


    net_bandwidth = 10*1024*1024
    vm = create_vm(vm_name, imageUuid, None,instanceOfferingUuid, l3NetworkUuids)
    vm_inv = vm.get_vm()
    vm_nic = test_lib.lib_get_vm_nic_by_l3(vm_inv, l3NetworkUuids)
    vm_ops.set_vm_nic_qos(vm_nic.uuid, outboundBandwidth = net_bandwidth, inboundBandwidth = net_bandwidth)
    cond = res_ops.gen_query_conditions('name', '=',  'admin')
    time.sleep(1)
    admin_uuid = res_ops.query_resource_fields(res_ops.ACCOUNT, cond)[0].uuid
    prices = bill_ops.calculate_account_spending(admin_uuid)
    if prices.total < 180:
        test_util.test_fail("test billing fail, bill is lesser than 180 after vm nic qos set")

    #Delete vm nic qos
    vm_ops.del_vm_nic_qos(vm_nic.uuid, "in")
    vm_ops.del_vm_nic_qos(vm_nic.uuid, "out")

    time.sleep(1)
    # Total cost should not grow up
    price1 = bill_ops.calculate_account_spending(admin_uuid)
    time.sleep(2)
    price2 = bill_ops.calculate_account_spending(admin_uuid)
    if price1.total != price2.total:
        test_util.test_fail("test billing fail, bill still grows up after deleting vm nic qos. price1 total: %s, price2 total: %s" % (price1.total, price2.total))

    #Delete vm nic resource price
    price_ipin = query_resource_price(resource_name = "pubIpVmNicBandwidthIn")[0]
    price_ipout = query_resource_price(resource_name = "pubIpVmNicBandwidthOut")[0]
    delete_price(price_ipin.uuid)
    delete_price(price_ipout.uuid)

    #make sure vm nic resource price has been deleted
    price_ipin = query_resource_price(resource_name = "pubIpVmNicBandwidthIn")
    price_ipout = query_resource_price(resource_name = "pubIpVmNicBandwidthOut")
    if len(price_ipin) > 0 or len(price_ipout)> 0:
        test_util.test_fail("Fail to clean vm nic resource price. length of pubIpVmNicBandwidthIn: %d, length of pubIpVmNicBandwidthOut: %d" %(len(price_ipin), len(price_ipout)))

    # price.total should be 0, after the prices are deleted
    prices = bill_ops.calculate_account_spending(admin_uuid)
    if prices.total != 0:
        test_util.test_fail("test billing fail, bill is not 0. Bill is: %s" % (prices.total))

    #create vip qos
    vip = test_stub.create_vip("test_vip_qos_price", l3NetworkUuids)
    vip_uuid = vip.get_vip().uuid
    vip_qos = net_ops.set_vip_qos(vip_uuid=vip_uuid, inboundBandwidth = net_bandwidth, outboundBandwidth = net_bandwidth)
    time.sleep(1)
    prices = bill_ops.calculate_account_spending(admin_uuid)
    if prices.total < 180:
        print prices.total
        test_util.test_fail("test billing fail, bill is lesser than 180 after vip qos set")
    #Delete vip qos
    net_ops.delete_vip_qos(vip_uuid)
    time.sleep(1)
    # Total cost should not grow up
    price1 = bill_ops.calculate_account_spending(admin_uuid)
    time.sleep(2)
    price2 = bill_ops.calculate_account_spending(admin_uuid)
    if price1.total != price2.total:
        test_util.test_fail("test billing fail, bill still grows up after deleting vip qos. price1 total: %s, price2 total: %s" % (price1.total, price2.total))

    #Delete vip resource price
    price_vipin = query_resource_price(resource_name = "pubIpVipBandwidthIn")[0]
    price_vipout = query_resource_price(resource_name = "pubIpVipBandwidthOut")[0]
    delete_price(price_vipin.uuid)
    delete_price(price_vipout.uuid)

    #make sure vm nic resource price has been deleted
    price_vipin = query_resource_price(resource_name = "pubIpVipBandwidthIn")
    price_vipout = query_resource_price(resource_name = "pubIpVipBandwidthOut")
    if len(price_vipin) > 0 or len(price_vipout)> 0:
        test_util.test_fail("Fail to clean vip resource price. length of pubIpVipBandwidthIn: %d, length of pubIpVipBandwidthOut: %d" %(len(price_vipin), len(price_vipout)))

    # price.total should be 0, after the prices are deleted
    prices = bill_ops.calculate_account_spending(admin_uuid)
    if prices.total != 0:
        test_util.test_fail("test billing fail, bill is not 0. Bill is: %s" % (prices.total))
    test_util.test_pass("test billing pass")

def error_cleanup():
    pass
