'''

New Integration test for testing vm backup for mini

@author: Pengtao.zhang
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_kvm_host as test_kvm_host
import zstackwoodpecker.header.host as host_header
import zstacklib.utils.linux as linux


vm = None
test_stub = test_lib.lib_get_test_stub()

def back_up(vm_obj):
     global backup
     bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
     backup_option = test_util.BackupOption()
     backup_option.set_name("test_compare")
     backup_option.set_volume_uuid(test_lib.lib_get_root_volume(vm_obj.get_vm()).uuid)
     backup_option.set_backupStorage_uuid(bs.uuid)
     backup = vol_ops.create_backup(backup_option)
     return backup

def test():
    global vm
    vm_cpu = 1
    vm_memory = 1073741824 #1G
    cond = res_ops.gen_query_conditions('name', '=', 'ttylinux')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    l3_network_uuid = res_ops.query_resource(res_ops.L3_NETWORK)[0].uuid
    vm = test_stub.create_mini_vm([l3_network_uuid], image_uuid, cpu_num = vm_cpu, memory_size = vm_memory)
    vm.check()
    backup_uuid = back_up(vm).uuid
    test_util.test_logger('Backup VM Test Success')

    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid
    vol_ops.delete_volume_backup([bs_uuid], backup_uuid)
    test_util.test_logger('Delete VM backup Test Success')
  
    vm.destroy()
    test_util.test_pass(' VM backup Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
