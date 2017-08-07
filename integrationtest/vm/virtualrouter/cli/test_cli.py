'''
New Integration Test for cli basic operation

@author: Lei Liu
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstacklib.utils.ssh as ssh
import json
import os


def test():

    test_util.test_dsc('Create test vm and check')
    mn_ip = os.environ.get('node1Name')
    nodeUserName = os.environ.get('nodeUserName')
    nodePassword = os.environ.get('nodePassword')
    ssh.make_ssh_no_password(mn_ip, nodeUserName, nodePassword)

    #Query image
    image_name = os.environ.get('imageName_s')
    cmd = "zstack-cli LogInByAccount accountName=admin password=password;" 
    fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
    cmd = 'zstack-cli QueryImage fields=uuid name="' + image_name  + '"'
    fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
    test_out = fo.read()
    query_result = json.loads(test_out)
    test_util.test_logger(query_result)
    image_uuid = str(query_result['inventories'][0]['uuid'])

    #Query l3
    l3_1_name = os.environ.get('l3PublicNetworkName')
    test_util.test_logger(l3_1_name)
    cmd = "zstack-cli LogInByAccount accountName=admin password=password;" 
    fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
    cmd = '"zstack-cli QueryL3Network fields=uuid name=\'' + l3_1_name + '\'"'
    test_util.test_logger(cmd)
    fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
    test_err = fe.read()
    test_out = fo.read()
    query_result = json.loads(test_out)
    test_util.test_logger(query_result)
    #l3_1_uuid = str(query_result['inventories'][0]['uuid'])
    l3_1_uuid = test_lib.lib_get_l3_by_name(l3_1_name).uuid

    #Query instanceOffering
    cmd = "zstack-cli QueryInstanceOffering fields=uuid"
    fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
    test_out = fo.read()

    query_result = json.loads(test_out)
    test_util.test_logger(query_result)

    instance_offering_uuid = str(query_result['inventories'][0]['uuid'])


    test_util.test_logger('CLI query')
    cmd = "zstack-cli LogInByAccount accountName=admin password=password;\
           zstack-cli QueryHost"
    fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
    testout = fo.read()
    query_result = json.loads(test_out)
    test_util.test_logger(query_result)
    cmd = "zstack-cli LogInByAccount accountName=admin password=password;\
           zstack-cli CreateVmInstance instanceOfferingUuid=" + instance_offering_uuid \
           + " l3NetworkUuids=" + l3_1_uuid \
           + " imageUuid=" + image_uuid + " name=VM1" \
           + " description='Thisisatestvm.\\\nShouldsuccessfullycreateaVM'"

    test_util.test_logger(cmd)
    fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
    textOut = fo.read()
    test_util.test_logger(textOut)
    fo.close
    fi.close
    fe.close

#Will be called only if exception happens in test().
def error_cleanup():
    global ps_uuid
    if ps_uuid != None:
        ps_ops.change_primary_storage_state(ps_uuid, 'enable')
    global host_uuid
    if host_uuid != None:
        host_ops.reconnect_host(host_uuid)
    global vr_uuid
    if vr_uuid != None:
        vm_ops.reconnect_vr(vr_uuid)
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
