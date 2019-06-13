'''
Test for auto reconnect vr

@author: quarkonics
'''

import os
import time
import commands
#import sys

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
DefaultFalseDict = test_lib.DefaultFalseDict

_config_ = {
        'timeout' : 360,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
case_flavor = dict(stop_virtualrouter_agent=             DefaultFalseDict(virtualrouter=True, vrouter=False, kill=False),
                   kill_virtualrouter_agent=             DefaultFalseDict(virtualrouter=True, vrouter=False, kill=True),
                   kill_vrouter_agent=             DefaultFalseDict(virtualrouter=False, vrouter=True, kill=True),
                   )


def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc('vr auto reconnection check test')

    l3_1_name = os.environ.get('l3VlanNetworkName1')
    l3_1 = test_lib.lib_get_l3_by_name(l3_1_name)
    if not l3_1:
        test_util.test_skip('No network for vr auto reconnect test')

    #create VRs.
    vrs = test_lib.lib_find_vr_by_l3_uuid(l3_1.uuid)
    if not vrs:
        image_name = os.environ.get('imageName_net')
        vm = test_stub.create_vr_vm('vm_for_vr', 'imageName_net', 'l3VlanNetworkName1')
        vm.destroy()
        vrs = test_lib.lib_find_vr_by_l3_uuid(l3_1.uuid)
        if len(vrs) < 1:
            test_util.test_skip('VR is required for testing')
        else:
            vr1 = vrs[0]
    else:
        vr1 = vrs[0]

    resource_type = res_ops.VIRTUALROUTER_VM
    if flavor['virtualrouter']:
        if vr1.applianceVmType != "VirtualRouter":
            test_util.test_skip('No network for vr auto reconnect test')

    if flavor['vrouter']:
        if vr1.applianceVmType != "vrouter":
            test_util.test_skip('No network for vr auto reconnect test')

    test_lib.lib_install_testagent_to_vr_with_vr_vm(vr1)
    test_util.test_logger("kill vr agent on vr %s" % (vr1.uuid))
    if flavor['virtualrouter']:
        if flavor['kill']:
            cmd = "pkill -9 -f 'from virtualrouter import virtualrouterdaemon'"
        else:
            cmd = "service zstack-virtualrouter stop"
    elif flavor['vrouter']:
        if flavor['kill']:
            cmd = "pkill -9 -f '/opt/vyatta/sbin/zvr -i'"
    #    else:
    #        cmd = "service zstack-imagestorebackupstorage stop"

    vr_ip = test_lib.lib_find_vr_pub_ip(vr1)
    if test_lib.lib_execute_sh_cmd_by_agent(vr_ip, cmd) == False:
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, vr_ip))

    test_util.test_logger("vr %s is expected to disconnect and start reconnect automatically" % (vr1.uuid))
    conditions = res_ops.gen_query_conditions('uuid', '=', vr1.uuid)
    count = 0
    while count < 24:
        vr = res_ops.query_resource(resource_type, conditions)[0]
        if vr.status == "Connecting":
            break

        time.sleep(5)
        count += 1

    if vr.status != "Connecting":
        test_util.test_fail("vr %s is not disconnect and start reconnect automatically in 120 seconds" % (vr1.uuid))

    test_util.test_logger("vr %s is expected to reconnect success automatically" % (vr1.uuid))
    count = 0
    while count < 24:
        vr = res_ops.query_resource(resource_type, conditions)[0]
        if vr.status == "Connected":
            break

        time.sleep(5)
        count += 1

    if vr.status != "Connected":
        test_util.test_fail("vr %s not reconnect success automatically in 120 seconds" % (vr.uuid))

    test_util.test_pass("Auto reconnect backup storage pass")
