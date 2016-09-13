'''

New Integration Test for enabled nested virt

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib


def test():
    host = test_lib.lib_get_all_hosts_from_plan()[0]
    cmd = 'cat /sys/module/kvm_intel/parameters/nested'
    cmd_out = test_lib.lib_execute_ssh_cmd(host.managementIp_, host.username_, host.password_, cmd, 180)
    if 'Y' not in cmd_out:
        test_util.test_fail('nested virt not enabled')

    cmd = 'cat /etc/modprobe.d/kvm-nested.conf'
    cmd_out = test_lib.lib_execute_ssh_cmd(host.managementIp_, host.username_, host.password_, cmd, 180)
    if 'options kvm_intel nested=1' not in cmd_out:
        test_util.test_fail('nested virt not enabled in /etc/modprobe.d/kvm_nested.conf')

    test_util.test_pass('Enable nested virt Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_util.test_logger('no clean up needed')
