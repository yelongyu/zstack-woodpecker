'''

Test for volume

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import os
#import arm.test_stub as test_stub

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    global test_stub,test_obj_dict

    vm = test_stub.create_x86_vm()
    test_obj_dict.add_vm(vm)
    vm.check()

    volume = test_stub.create_volume()
    test_obj_dict.add_volume(volume)
    volume.check()

    volume.delete()
    volume.check()

    volume.recover()
    volume.check()

    volume.attach(vm)
    volume.check()

    bs_uuid = test_lib.lib_get_image_store_backup_storage().uuid
    volume_tem = volume.create_template([bs_uuid])
    test_obj_dict.add_image(volume_tem)

    volume.detach(vm.get_vm().uuid)
    volume.check()

    host_uuid=test_lib.lib_find_random_host_by_volume_uuid(volume.get_volume().uuid).uuid
    volume.migrate(host_uuid)
    volume.check()

    volume.delete()
    volume.check()

    volume.expunge()
    volume.check()
    # time.sleep(5)
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create VM Test Success')


# Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
