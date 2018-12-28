'''

New Integration Test for License.
@Antony  Weijiang

'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import os
import time
import datetime
import uuid
import json
import urllib2

test_stub = test_lib.lib_get_test_stub()
ding_url = "https://oapi.dingtalk.com/robot/send?access_token=d4a90949d4e4a0b1dc0dbb57989a58480795d67b82fb86ce848b801602cabe76"
def sendMsg_to_Ding():
	header = {
			"Content-Type": "application/json",
			"Charset": "UTF-8"
		}
	data = {
                        "at": {
                                "isAtAll": True
                                },
			"msgtype": "text",
			"text": {
					"content": "1.zstack global config  has changed on  latest nightly test.\n\
2.need to doulbe confirm ui if has change example :Garbled words\n\
3.antony(weijiang),you should double confirm with developer and then fix this issue."
				}
		}
	sendData = json.dumps(data)
	sendData = sendData.encode("utf-8")
	request = urllib2.Request(url=ding_url, data=sendData, headers=header)
	opener = urllib2.urlopen(request)
	test_util.test_logger(opener.read())

def environment(management_ip):
	test_lib.lib_execute_ssh_cmd(management_ip, 'root', 'password', 'zstack-cli LogInByAccount accountName=admin password=password', 180)
	output_result = test_lib.lib_execute_ssh_cmd(management_ip, 'root', 'password', 'zstack-cli  GetLicenseInfo  | grep -i "licensetype" | awk -F ":" \'{print $2}\' | cut -d"\\""  -f2', 180)
        if output_result.strip() == "Community":
                default_name="/home/default_Community"
                if os.path.isfile(default_name):
                        return default_name
                else:
                        test_util.test_fail("can not find default global config: default_Community in /home directory")
        elif output_result.strip() == "Paid":
                default_name = "/home/default_Paid"
                if os.path.isfile(default_name):
                        return default_name
                else:
                        test_util.test_fail("can not find default global config: default_Paid in /home directory")
        else:
                test_util.test_skip("skip global config case.because of Testing only covers community and enterprise")

def check(file1_path,file2_path):
	output_result=test_stub.execute_shell_in_process_stdout('diff %s %s' %(file1_path,file2_path),'/tmp/%s' % uuid.uuid1().get_hex())
	if output_result[0] != 0:
		if output_result[1].strip():
			sendMsg_to_Ding()
			test_util.test_fail("global config has changes ,more detalis as follow\n %s" %(output_result[1]))

def verify_config(management_ip):
	tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
	test_util.test_logger("%s" %(tmp_file))
	test_lib.lib_execute_ssh_cmd(management_ip, 'root', 'password', 'zstack-cli LogInByAccount accountName=admin password=password', 180)
	test_lib.lib_execute_ssh_cmd(management_ip,'root','password','zstack-cli QueryGlobalConfig sortBy=name > %s' %(tmp_file), 180)
	default_path=environment(management_ip)
	test_util.test_logger("default global config path:%s" %(default_path))

	test_util.test_logger("check two file diff:%s, %s" %(default_path,tmp_file))
	check(default_path,tmp_file)

def test():
	test_util.test_logger('start query global config')
	mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
	test_util.test_logger("%s" %(mn_ip))
	
	test_util.test_logger('Test Community Environment')
	test_stub.reload_default_license()
	verify_config(mn_ip)
	test_util.test_logger('Check Global Config with Commuity Environment pass')
	
	test_util.test_logger('Test Paid Environment')
	test_util.test_logger('Load Prepaid license with 1 day and 1 CPU')
	file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '1', 'Prepaid', '1', '')
	test_stub.load_license(file_path)
	verify_config(mn_ip)	
	test_util.test_logger('Check Global Config with Paid Environment pass')
	test_util.test_pass('Check Global Config Pass')


def error_cleanup():
	test_lib.lib_error_cleanup(test_obj_dict)

