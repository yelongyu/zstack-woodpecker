'''

New Integration Test for Set VM console password when creating VM.

@author: Mirabel
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstacklib.utils.shell as shell
import test_stub
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.resource_operations as res_ops
from vncdotool import api

vm = None
password1='111111'
password2='123456'

def test():
    global vm
    session_uuid = None
    instance_offering_uuid = res_ops.get_resource(res_ops.INSTANCE_OFFERING, session_uuid)[0].uuid
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond, session_uuid)[0].uuid
    l3net_uuid = res_ops.get_resource(res_ops.L3_NETWORK, session_uuid)[0].uuid
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_l3_uuids([l3net_uuid])
    vm_creation_option.set_console_password(password1)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    vm.check()
    console = test_lib.lib_get_vm_console_address(vm.get_vm().uuid)
    test_util.test_logger('[vm:] %s console is on %s:%s' % (vm.get_vm().uuid, console.hostIp, console.port))
    display = str(int(console.port)-5900)
    try:
        client = api.connect(console.hostIp+":"+display)
        client.keyPress('k')
        test_util.test_fail('[vm:] %s console on %s:%s is connectable without password' % (vm.get_vm().uuid, console.hostIp, console.port))
    except:
        test_util.test_logger('[vm:] %s console on %s:%s is not connectable without password' % (vm.get_vm().uuid, console.hostIp, console.port))

    try:
        client = api.connect(console.hostIp+":"+display, password1)
        client.keyPress('k')
        test_util.test_logger('[vm:] %s console on %s:%s is connectable with password %s' % (vm.get_vm().uuid, console.hostIp, console.port, password1))
    except:
        test_util.test_fail('[vm:] %s console on %s:%s is not connectable with password %s' % (vm.get_vm().uuid, console.hostIp, console.port, password1))

    test_lib.lib_set_vm_console_password(vm.get_vm().uuid, password2)
    test_util.test_logger('set [vm:] %s console with password %s' % (vm.get_vm().uuid, password2))
    vm.reboot()

    try:
        client = api.connect(console.hostIp+":"+display, password2)
        client.keyPress('k')
        test_util.test_logger('[vm:] %s console on %s:%s is connectable with password %s' % (vm.get_vm().uuid, console.hostIp, console.port, password2))
    except:
        test_util.test_fail('[vm:] %s console on %s:%s is not connectable with password %s' % (vm.get_vm().uuid, console.hostIp, console.port, password2))

    import signal
    def handler(signum, frame):
        raise Exception()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(30)

    try:
        client = api.connect(console.hostIp+":"+display, password1)
        client.keyPress('k')
        test_util.test_fail('[vm:] %s console on %s:%s is connectable with password %s' % (vm.get_vm().uuid, console.hostIp, console.port, password1))
    except:
        test_util.test_logger('[vm:] %s console on %s:%s is not connectable with password %s' % (vm.get_vm().uuid, console.hostIp, console.port, password1))

    vm.destroy()

    test_util.test_pass('Set VM Console Password Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
