'''
  attach 2 L2network with same nic name to a cluster
  regex: "There has been a l2Network[uuid:%s, name:%s] attached to cluster[uuid:%s] that has physical interface[eth0]. Failed to attach l2Network[uuid:%s]"
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.errorcode_operations as errc_ops
import zstackwoodpecker.operations.net_operations as net_ops
from apibinding.api import ApiError
import sys
reload(sys)
sys.setdefaultencoding('utf8')

test_stub = test_lib.lib_get_test_stub()
regex = "There has been a l2Network[uuid:%s, name:%s] attached to cluster[uuid:%s] that has physical interface[eth0]. Failed to attach l2Network[uuid:%s]"

check_message = None
check_message_list = errc_ops.get_elaborations(category = 'L2Network')

l2_uuid = None
def test():
    global l2_uuid
    test_stub.check_elaboration_properties()
    for message in check_message_list:
        if regex == message.regex:
            check_message =  message.message_cn.encode('utf8')
            break
    test_util.test_logger('@@@@DEBUG@@@@: %s' % check_message)
    #create L2 & attach to cluster
    nic_name = res_ops.query_resource(res_ops.L2_NETWORK)[0].physicalInterface
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    l2_name = 'L2_test' 
    try:
        l2_uuid = net_ops.create_l2_novlan(l2_name, nic_name, zone_uuid).inventory.uuid
        net_ops.attach_l2(l2_uuid, cluster_uuid)
    except ApiError as e:
        #ascii->unicode->utf8
        err_msg = str([e]).decode('unicode-escape').encode('utf8')
        test_util.test_logger('@@@%s@@@%s@@@' % (check_message, err_msg))
        if check_message in err_msg or err_msg in check_message:
            test_util.test_pass("regex check pass,check_message:%s" % check_message)
        else:
            test_util.test_fail('@@DEBUG@@\n TEST FAILED\n %s' % err_msg)

def error_cleanup():
    net_ops.delete_l2(l2_uuid)
