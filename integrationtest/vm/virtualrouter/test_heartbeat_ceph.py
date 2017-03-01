'''
Test for ceph connection when the heartbeat file is exist 

@author: Glody 
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
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.console_operations as cons_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstacklib.utils.ssh as ssh

_config_ = {
        'timeout' : 18000,
        'noparallel' : True
        }

def test():
    test_util.test_dsc('ceph reconnection check heartbeat test')
    if res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE):
        ps = res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE)[0]
    else:
        test_util.test_skip("No ceph primarystorage for test. Skip test")
    cond = res_ops.gen_query_conditions('uuid', '=', ps.uuid)
    for key in ps.__dict__:
        if key == "mons":
            mons_ops = ps.__dict__[key][0].__dict__
            for sub_key in mons_ops:
                if sub_key == "monUuid":
                    monUuid = mons_ops[sub_key]
                if sub_key == "hostname":
                    hostname = mons_ops[sub_key]
                if sub_key == "sshPort":
                    sshPort = mons_ops[sub_key]
                if sub_key == "sshUsername":
                    sshUsername = mons_ops[sub_key]
                if sub_key == "sshPassword":
                    sshPassword = mons_ops[sub_key]
    heartbeat_file_name = monUuid+"-this-is-a-test-image-with-long-name"

    ret = os.system("sshpass -p '%s' ssh %s rbd create %s --image-format 2 --size 1" %(sshPassword, hostname, heartbeat_file_name))
    return_name=os.system("sshpass -p '%s' ssh %s rbd ls |grep %s |grep %s" %(sshPassword, hostname, monUuid, heartbeat_file_name))
    if return_name == heartbeat_file_name: 
        print " Create heartbeat file %s success" %heartbeat_file_name

    reconnect_ret =  ps_ops.reconnect_primary_storage(ps.uuid)
    test_fail = 1
    for key in reconnect_ret.__dict__:
        if key == "status" and reconnect_ret[key] == "Connected":
            test_fail = 0
            test_util.test_pass("Reconnect status is %s"%reconnect_ret[key])
    if test_fail:
        test_util.test_fail("Reconnect to ceph ps failed")
