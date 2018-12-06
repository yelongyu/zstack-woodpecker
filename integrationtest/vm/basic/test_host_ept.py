'''

New Integration Test for host ept disable/enable

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
    host_state = host.state
    ept_status = host_ops.get_ept_status(host.managementIp, host.username, "password", host.sshPort)
    #Test ept changes under maintenance state
    if host_state != "Maintenance": 
        host_ops.change_host_state(host_uuid, "maintain")
        time.sleep(10)
    if ept_status == "enable":
        try:
            tag_ops.create_system_tag("HostVO", host_uuid, "pageTableExtensionDisabled")
            host_ops.change_host_state(host_uuid, "enable")
            time.sleep(60)
            status = host_ops.get_ept_status(host.managementIp, host.username, "password", host.sshPort)
            if status != "disable":
                test_util.test_fail('Fail to disable ept')
        except:
            test_util.test_fail('Exception catched when disabling ept') 
    else:
        try:
            cond = res_ops.gen_query_conditions('tag', '=', 'pageTableExtensionDisabled')
            cond = res_ops.gen_query_conditions('resourceUuid', '=', host_uuid, cond)
            tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0]
            if tag != None:
                tag_ops.delete_tag(tag.uuid)
                host_ops.change_host_state(host_uuid, "enable")
                time.sleep(60)
                status = host_ops.get_ept_status(host.managementIp, host.username, "password", host.sshPort)
                if status != "enable":
                    test_util.test_fail('Fail to enable ept')
        except:
            test_util.test_fail('Exception catched when enabling ept')

    #Enable ept
    cond = res_ops.gen_query_conditions('tag', '=', 'pageTableExtensionDisabled')
    cond = res_ops.gen_query_conditions('resourceUuid', '=', host_uuid, cond)
    tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    if tag != []:
        if host_state != "Maintenance":
            host_ops.change_host_state(host_uuid, "maintain")
            time.sleep(10)
        tag_ops.delete_tag(tag.uuid)
        host_ops.change_host_state(host_uuid, "enable")
        time.sleep(60)

    test_util.test_pass('EPT disable/enable Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    host_ops.change_host_state(host_uuid, "enable")
