# -*- coding: UTF-8 -*-
'''
New Test For datavolume price with systemtags life cycle
@author Zhaohao
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.billing_operations as bill_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import threading
import json
import random
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None
billing_resource = 'datavolume'
offset_unit_dict=['sec','min','hou','day','week','month','year']
time_unit_dict=['s','m','h','d','w','mon']
resource_unit_dict={"M":1024 * float(1024), "G":1024**2 * float(1024), "T":1024**3 * float(1024)}

#systemtags config
#cond = res_ops.gen_query_conditions('type', '=', 'ceph')
ps_uuid = res_ops.query_resource_fields(res_ops.CEPH_PRIMARY_STORAGE)[0].uuid
data_pool_name = 'test-pool-Data-1-' + ps_uuid
price_systemtags_json = json.dumps({"priceUserConfig":{"priceKeyName":"highSpeedDisk"}})
price_system_tags = ["priceUserConfig::%s" % price_systemtags_json,]

def test():
    global price
    #1.create data volume price with systemtags
    bill_datavolume = test_lib.DataVolumeBilling()
    time_unit = random.choice(time_unit_dict)
    price = str(random.randint(0,9999))
    resource_unit = random.choice(resource_unit_dict.keys())
    bill_datavolume.set_timeUnit(time_unit)
    bill_datavolume.set_price(price)
    bill_datavolume.set_resourceUnit(resource_unit)
    bill_datavolume.set_price_system_tags(price_system_tags)
    test_util.test_logger("create data volume price with systemtags")
    price = bill_datavolume.create_resource_type()
    if not price:
        test_util.test_fail("fail: create datavolume price")
    else:
        test_util.test_logger("success: create datavolume price %s" % price.uuid)

    #2.query data volume price
    cond = res_ops.gen_query_conditions('uuid', '=', price.uuid)
    price_query = bill_ops.query_resource_price(cond)[0]
    if price_query.uuid == price.uuid:
        test_util.test_logger("success: query datavolume price %s" % price_query.uuid)
    else:
        test_util.test_fail("fail: query datavolume price %s" % price.uuid)
    
    #3.delete data volume price
    delete_result = bill_ops.delete_resource_price(price.uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', price.uuid)
    #delete check,because delete API always return success
    delete_check = bill_ops.query_resource_price(cond)
    if delete_check:
        test_util.test_fail("fail: delete datavolume price %s" % price.uuid)
    else:
        test_util.test_logger("success: delete datavolume price %s" % price_query.uuid)

def error_cleanup():
    resourcePrices = test_lib.query_resource_price()
    if resourcePrices:
        for resourceprice in resourcePrices:
            test_lib.delete_price(resourceprice.uuid)

def env_recover():
    resourcePrices = test_lib.query_resource_price()
    if resourcePrices:
        for resourceprice in resourcePrices:
            test_lib.delete_price(resourceprice.uuid)
