'''
Test pxe server operations

@author: Glody
'''
import zstackwoodpecker.operations.baremetal_operations as baremetal_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub

pxe_uuid = None
def test():
    global pxe_uuid
    pxe_servers = res_ops.query_resource(res_ops.PXE_SERVER)
    if pxe_servers != None:
        for pxe in pxe_servers:
            baremetal_ops.delete_pxe(pxe.uuid)
    pxe_option = test_util.PxeOption() 
    pxe_option.set_name('pxe_server')
    pxe_option.set_dhcp_interface('zsn0')
    pxe_uuid = baremetal_ops.create_pxe(pxe_option).uuid
    cond = res_ops.gen_query_conditions('uuid', '=', pxe_uuid)
    pxe = res_ops.query_resource(res_ops.PXE_SERVER, cond)[0]
    if pxe == None:
        test_util.test_fail('Create PXE Server Failed')
    baremetal_ops.stop_pxe(pxe_uuid)
    pxe = res_ops.query_resource(res_ops.PXE_SERVER, cond)[0]
    if pxe.status != "Stopped":
        test_util.test_fail('Stop PXE Server Failed')
    baremetal_ops.start_pxe(pxe_uuid)
    baremetal_ops.delete_pxe(pxe_uuid)
    test_util.test_pass('Test PXE Server Success')

def error_cleanup():
    global pxe_uuid
    if pxe_uuid != None:
        baremetal_ops.delete_pxe(pxe_uuid)

