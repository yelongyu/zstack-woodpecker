'''

New Integration test for checking host active profile

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.header.host as host_header
import zstacklib.utils.ssh as ssh

_config_ = {
        'timeout' : 600,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Check host active profile')
    conditions = res_ops.gen_query_conditions('state', '=', host_header.ENABLED)
    conditions = res_ops.gen_query_conditions('status', '=', host_header.CONNECTED, conditions)
    all_hosts = res_ops.query_resource(res_ops.HOST, conditions)
    if len(all_hosts) < 1:
        test_util.test_skip('Not available host to check')

    command = '/usr/sbin/tuned-adm active'
    for host in all_hosts:
        eout = ''
        if host.sshPort != None:
            (ret, out, eout) = ssh.execute(command, host.managementIp, host.username, host.password, port=host.sshPort)
	else:
            (ret, out, eout) = ssh.execute(command, host.managementIp, host.username, host.password)
         
        if out.find('virtual-host') < 0:
            test_util.test_fail('host not tuned to virtual-host mode')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
