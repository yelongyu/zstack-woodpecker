'''

New Integration Test for VM vga mode.

@author: quarkonics
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.test_util as test_util
from vncdotool import api
from PIL import Image

_config_ = {
        'timeout' : 600,
        'noparallel' : False
        }

test_stub = test_lib.lib_get_test_stub()
vm = None
default_mode = None

def test():
    global vm
    global default_mode
#    default_mode = conf_ops.get_global_config_value('kvm', 'videoType')
    default_mode = conf_ops.change_global_config('vm', 'videoType', 'qxl')
    vm = test_stub.create_sg_vm()
    console = test_lib.lib_get_vm_console_address(vm.get_vm().uuid)
    test_util.test_logger('[vm:] %s console is on %s:%s' % (vm.get_vm().uuid, console.hostIp, console.port))
    display = str(int(console.port)-5900)
    vm.check()
    vm_mode = test_lib.lib_get_vm_video_type(vm.get_vm())
    if vm_mode != 'qxl':
        test_util.test_fail('VM is expected to work in qxl mode instead of %s' % (vm_mode))
    client = api.connect(console.hostIp+":"+display)
    client.captureScreen('tmp.png')
    image = Image.open('tmp.png')
    if image.width != 720 or image.height != 400:
        test_util.test_fail("VM is expected to work in 720x400 while its %sx%s" % (image.width, image.height))
    box = image.getbbox()
    if box != (0, 18, 403, 79) and box != (0, 18, 403, 80):
        test_util.test_fail("VM is expected to display text in area (0, 18, 403, 79) while it's actually: (%s, %s, %s, %s)" % (box[0], box[1], box[2], box[3]))

    test_util.test_logger('[vm:] change vga mode to vga=794 which is 1280x1024')
    cmd = 'sed -i "s/115200$/115200 vga=794/g" /boot/grub2/grub.cfg'
    test_lib.lib_execute_command_in_vm(vm.get_vm(), cmd)
    vm.reboot()
    vm.check()
    client = api.connect(console.hostIp+":"+display)
    client.captureScreen('tmp.png')
    image = Image.open('tmp.png')
    if image.width != 1280 or image.height != 1024:
        test_util.test_fail("VM is expected to work in 1280x1024 while its %sx%s" % (image.width, image.height))
    box = image.getbbox()
    if box != (0, 18, 359, 79) and box != (0, 18, 359, 80):
        test_util.test_fail("VM is expected to display text in area (0, 18, 359, 79) while it's actually: (%s, %s, %s, %s)" % (box[0], box[1], box[2], box[3]))

    test_util.test_logger('[vm:] change vga mode to vga=907 which is 2560x1600')
    cmd = 'sed -i "s/vga=794/vga=907/g" /boot/grub2/grub.cfg'
    test_lib.lib_execute_command_in_vm(vm.get_vm(), cmd)
    vm.reboot()
    vm.check()
    client = api.connect(console.hostIp+":"+display)
    client.captureScreen('tmp.png')
    image = Image.open('tmp.png')
    if image.width != 2560 or image.height != 1600:
        test_util.test_fail("VM is expected to work in 2560x1600 while its %sx%s" % (image.width, image.height))
    box = image.getbbox()
    if box != (0, 18, 359, 79) and box != (0, 18, 359, 80):
        test_util.test_fail("VM is expected to display text in area (0, 18, 359, 79) while it's actually: (%s, %s, %s, %s)" % (box[0], box[1], box[2], box[3]))

    vm.destroy()
    vm.check()
    conf_ops.change_global_config('vm', 'videoType', default_mode)
    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    conf_ops.change_global_config('vm', 'videoType', default_mode)
    global vm
    if vm:
        vm.destroy()
