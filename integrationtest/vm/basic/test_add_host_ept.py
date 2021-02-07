'''

New Integration Test for host ept disable/enable during add host

@author: Glody
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import time

def test():
    host = res_ops.query_resource(res_ops.HOST)[0]
    host_uuid = host.uuid
    password = "password"
    host_option = test_util.HostOption()
    host_option.set_cluster_uuid(host.clusterUuid)
    host_option.set_username(host.username)
    host_option.set_password(password)
    host_option.set_management_ip(host.managementIp)
    host_option.set_name(host.name)
    host_option.set_description(host.description)
    system_tag="pageTableExtensionDisabled"
    host_option.set_system_tags([system_tag])

    host_ops.delete_host(host_uuid)
    new_added_host = host_ops.add_kvm_host(host_option)
    time.sleep(60)
    status = host_ops.get_ept_status(host.managementIp, host.username, password, host.sshPort)
    if status != "disable":
         test_util.test_fail('Fail to add host with ept disabled')

    host_ops.delete_host(new_added_host.uuid)
    host_option.set_system_tags([])
    host_ops.add_kvm_host(host_option)
    time.sleep(60)
    status = host_ops.get_ept_status(host.managementIp, host.username, password, host.sshPort)
    if status != "enable":
         test_util.test_fail('Fail to add host with ept enabled')

    test_util.test_pass('Add Host with EPT disabled/enabled Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    host_ops.change_host_state(host_uuid, "enable")
