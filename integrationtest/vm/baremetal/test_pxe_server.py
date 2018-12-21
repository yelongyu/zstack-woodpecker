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
    test_util.test_dsc('Check if another pxe server created')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    pxe_servers = res_ops.query_resource(res_ops.PXE_SERVER)
    if pxe_servers != None:
        for pxe in pxe_servers:
            baremetal_ops.delete_pxe(pxe.uuid)

    test_util.test_dsc('Create pxe server and stop/start it')
    [pxe_ip, interface] = test_stub.get_pxe_info()
    pxe_uuid = test_stub.create_pxe(dhcp_interface = interface, hostname = pxe_ip, zoneUuid = zone_uuid).uuid
    #baremetal_operations.attach_pxe_to_cluster(pxe_uuid, baremetal_cluster_uuid)

    pxe = res_ops.query_resource(res_ops.PXE_SERVER)[0]
    if pxe == None:
        test_util.test_fail('Create PXE Server Failed')
    baremetal_ops.stop_pxe(pxe_uuid)
    pxe = res_ops.query_resource(res_ops.PXE_SERVER)[0]
    if pxe.state != "Disabled":
        test_util.test_fail('Disable PXE Server Failed, PXE state: %s' %pxe.status)
    baremetal_ops.start_pxe(pxe_uuid)
    pxe = res_ops.query_resource(res_ops.PXE_SERVER)[0]
    if pxe.state != "Enabled":
        test_util.test_fail('Enable PXE Server Failed, PXE state: %s' %pxe.status)

    baremetal_ops.delete_pxe(pxe_uuid)
    test_util.test_pass('Test PXE Server Success')

def error_cleanup():
    global pxe_uuid
    if pxe_uuid != None:
        baremetal_ops.delete_pxe(pxe_uuid)

