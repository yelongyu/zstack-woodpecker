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
import time
import os


def test():

    test_util.test_dsc('Create test vm and check')
    mn_ip = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']
    test_util.test_dsc("wait 10s for start")
    nodeUserName = os.environ.get('nodeUserName')
    nodePassword = os.environ.get('nodePassword')
    ssh.make_ssh_no_password(mn_ip, nodeUserName, nodePassword)

    #Query image
    image_name = os.environ.get('imageName_s')
    for i in range(0, 4):
        time.sleep(10)
        try:
            cmd = "zstack-cli LogInByAccount accountName=admin password=password;"
            fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
            cmd = 'zstack-cli QueryImage fields=uuid name="' + image_name  + '"'
            fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
            test_util.test_logger('ssh ' + mn_ip + ' ' + cmd)
            test_out = fo.read()
            query_result = json.loads(test_out)
            break
        except Exception as e:
            test_util.test_logger(str(e))
            test_util.test_logger('fail to query image retry: ' + str(i))
    test_util.test_logger(query_result)
    image_uuid = str(query_result['inventories'][0]['uuid'])

    #Query l3
    l3_1_name = os.environ.get('l3PublicNetworkName')
    test_util.test_logger(l3_1_name)
    for i in range(0, 4):
        try:
            cmd = "zstack-cli LogInByAccount accountName=admin password=password;"
            fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
            cmd = '"zstack-cli QueryL3Network fields=uuid name=\'' + l3_1_name + '\'"'
            test_util.test_logger(cmd)
            fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
            test_err = fe.read()
            test_out = fo.read()
            query_result = json.loads(test_out)
            break
        except Exception as e:
            test_util.test_logger(str(e))
            test_util.test_logger('fail to query l3network retry: ' + str(i))
        time.sleep(2)
    test_util.test_logger(query_result)
    #l3_1_uuid = str(query_result['inventories'][0]['uuid'])
    l3_1_uuid = test_lib.lib_get_l3_by_name(l3_1_name).uuid

    #Query instanceOffering
    for i in range(0, 4):
        try:
            cmd = "zstack-cli QueryInstanceOffering fields=uuid"
            fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
            test_out = fo.read()

            query_result = json.loads(test_out)
            test_util.test_logger(query_result)
            break
        except Exception as e:
            test_util.test_logger(str(e))
            test_util.test_logger('fail to query l3network retry: ' + str(i))
        time.sleep(2)

    instance_offering_uuid = str(query_result['inventories'][0]['uuid'])

    for i in range(0, 4):
        try:
            test_util.test_logger('CLI query')
            cmd = "zstack-cli LogInByAccount accountName=admin password=password;\
                   zstack-cli QueryHost"
            fi, fo, fe = os.popen3('ssh ' + mn_ip + ' ' + cmd )
            testout = fo.read()
            query_result = json.loads(test_out)
            test_util.test_logger(query_result)
            break
        except Exception as e:
            test_util.test_logger(str(e))
            test_util.test_logger('fail to query l3network retry: ' + str(i))
        time.sleep(2)
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
    test_lib.lib_error_cleanup(test_obj_dict)
