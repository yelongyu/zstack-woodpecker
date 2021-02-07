import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops

import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.account_operations as acc_ops


@auther: fangxiao


test_stub = test_lib.lib_get_test_stub()


def test():
	
	test_util.test_dsc("create vpc vrouter")
	vr = test_stub.create_vpc_vrouter('test_reconnection')
	
	test_util.test_dsc("attach vpc l3 to vpc vrouter")
	test_stub.attach_l3_to_vpc_vr(vr, test_stub.L3_SYSTEM_NAME_LIST)
	
	test_util.test_dsc("get the vip of the vpc router")
	conf = res_ops.gen_query_conditions('name','=','vip-for-test_reconnection')
	
	vip = res_ops.query_resource(res_ops.VIP,conf)[0]
	
	
	test_util.test_dsc("set qos")	
	net_ops.set_vip_qos(vip.uuid,1024*8*1024,1024*8*1024)
	
	test_util.test_dsc("reconnect the vpc router")
	vr.reconnect()
	
	
	vr.destroy()
	
	test_stub.remove_all_vpc_vrouter()

def env_recover():
	test_stub.remove_all_vpc_vrouter()
