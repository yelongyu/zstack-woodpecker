import zstackwoodpecker.operations.baremetal_operations as bare_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import os

def test():
    pxe_servers = res_ops.query_resource(res_ops.PXE_SERVER)
    if pxe_servers != None:
        for pxe in pxe_servers:
            bare_ops.delete_pxe(pxe.uuid)
    test_stub.create_pxe()
    test_util.test_pass('Create PXE Test Success')

def error_cleanup():
    pass

