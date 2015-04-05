'''

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

vm = None

def test():
    global vm
    vm = test_lib.lib_create_vm()
    vm.check()

    vm.destroy()
    test_util.test_pass('Create random VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
