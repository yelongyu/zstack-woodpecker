'''

Integration Test Teardown case

@author: Youyk
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import time

def test():
    vms = res_ops.query_resource(res_ops.VM_INSTANCE)
    for vm in vms:
        try:
            vm_ops.destroy_vm(vm.uuid)
        except:
            pass

    time.sleep(1)
    volumes = res_ops.query_resource(res_ops.VOLUME)
    for volume in volumes:
        try:
            vol_ops.delete_volume(volume.uuid)
        except:
            pass

