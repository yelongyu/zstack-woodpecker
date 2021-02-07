'''

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import time

test_stub = test_lib.lib_get_specific_stub()

test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    vm = test_stub.create_vm()
    test_obj_dict.add_vm(vm)
    vm.check()

    volume = test_stub.create_volume()
    test_obj_dict.add_volume(volume)
    volume.check()

    volume.attach(vm)
    volume.check()

    vm.stop()
    volume2 = test_stub.create_volume()
    test_obj_dict.add_volume(volume2)
    volume2.check()

    volume2.attach(vm)
    volume2.check()

    volume2.detach()
    volume2.check()

    volume2.attach(vm)
    volume2.check()

    vm.start()
    vm.check()
    time.sleep(60)

    volume.check()
    volume2.check()

    volume.detach()
    volume.check()
    volume2.check()

    volume.delete()
    volume.check()
    volume2.check()

    vm.destroy()
    volume2.check()

    volume2.delete()
    volume2.check()

    test_util.test_pass('Create Data Volume for stopped VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

