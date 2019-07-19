'''
 ReloadElaboration with wrong errorcode type
 regex: "elaboration code must be number!"
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.errorcode_operations as errc_ops
from apibinding.api import ApiError
import sys
reload(sys)
sys.setdefaultencoding('utf8')

test_stub = test_lib.lib_get_test_stub()
regex = "elaboration code must be number!" 

path = '/usr/local/zstacktest/apache-tomcat/webapps/zstack/WEB-INF/classes/errorElaborations/Account.json'
cmd_alter = "cp {0} /tmp/bak;sed -i 's/\"code\": \"/& a/g' {0}".format(path)
cmd_revert = "mv --force /tmp/bak {0}".format(path)
mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName

check_message = None
check_message_list = errc_ops.get_elaborations(category = 'Elaboration')
def test():
    test_stub.check_elaboration_properties()
    for message in check_message_list:
        if regex == message.regex:
            check_message =  message.message_cn.encode('utf8')
            break
    test_util.test_logger('@@@@DEBUG@@@@: %s' % check_message)
    #reload elaboration with wrong errorcode type
    try:
        test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd_alter)
        errc_ops.reload_elaboration()
    except ApiError as e:
        #ascii->unicode->utf8
        err_msg = str([e]).decode('unicode-escape').encode('utf8')
        #err_msg = str([e])
        test_util.test_logger('@@@%s@@@%s@@@' % (check_message, err_msg))
        if check_message in err_msg or err_msg in check_message:
            test_util.test_pass("regex check pass,check_message:%s" % check_message)
        else:
            test_util.test_fail('@@DEBUG@@\n TEST FAILED\n %s' % err_msg)
    finally:
        test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd_revert) 
    
def error_cleanup():
    pass
