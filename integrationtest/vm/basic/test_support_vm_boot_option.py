'''

New Integration Test for Support VM boot option.

@author: Mirabel
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.shell as shell
import os
import time
import zstackwoodpecker.operations.account_operations as acc_ops
from vncdotool import api

test_stub = test_lib.lib_get_specific_stub()

vm = None

def test():
    global vm

    import signal
    def handler(signum, frame):
        raise Exception()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(30)
    boot_option_picture = os.environ.get('bootOptionPicture')

    vm = test_stub.create_vm()
    console = test_lib.lib_get_vm_console_address(vm.get_vm().uuid)
    test_util.test_logger('[vm:] %s console is on %s:%s' % (vm.get_vm().uuid, console.hostIp, console.port))
    display = str(int(console.port)-5900)

    client = api.connect(console.hostIp+":"+display)
    time.sleep(2)
    client.keyPress('esc')
    #client.captureRegion('/root/boot.png',0,100,600,600)
    client.expectRegion(boot_option_picture,0,100)
    test_util.test_logger('[vm:] %s support boot option' % (vm.get_vm().uuid))
#    except:
#        test_util.test_fail('[vm:] %s is expected to support boot option' % (vm.get_vm().uuid))

    vm.destroy()

    test_util.test_pass('Support VM Boot Option Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()

