'''
zstacl_api_log auto delete test
1.get api_log delete threshold
2.mock log files(management-server-*.log.gz)
3.resize management-server.log, bigger than threshold(default 450MB)
4.zstack_ctl restart_node
5.check logs size
@author Zhaohao
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as conf_ops
import xml.etree.ElementTree as et 
import threading
import random
import time
import os

#get api_log delete threshold & AccumulatedFileSize from log4j2.xml
MN_IP = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
LOG4J2_TREE = et.ElementTree(file='/usr/local/zstacktest/apache-tomcat/webapps/zstack/WEB-INF/classes/log4j2.xml')
LOG_PATH = "/usr/local/zstacktest/apache-tomcat/logs/"
CLEAN_THRESHOLD_LIST = LOG4J2_TREE.getroot().findall('./Appenders/RollingFile/Policies/SizeBasedTriggeringPolicy')
api_threshold = CLEAN_THRESHOLD_LIST[1].attrib['size'].split(' ')
log_files_size = LOG4J2_TREE.getroot().findall('./Appenders/RollingFile/DefaultRolloverStrategy/Delete/IfFileName/IfAny/IfAccumulatedFileSize')[0].attrib['exceeds'].split(' ')
log_files_format = LOG4J2_TREE.getroot().findall('./Appenders/RollingFile/DefaultRolloverStrategy/Delete/IfFileName')[1].attrib['glob'].replace('*','.*')

def unit_to_int(unit):
    return 1024*1024 if unit=='MB' else 1024*1024*1024

def mock_log_files(api_log_size):
    mock_log_file_size = 40*1024*1024 #40MB
    mock_num = api_log_size/mock_log_file_size + 5
    cmd = 'for i in {1..%s}; do dd if=/dev/zero of=%szstack-api-%s-$i.log.gz bs=1M count=40; done' % (mock_num, LOG_PATH, time.time())
    test_lib.lib_execute_ssh_cmd(MN_IP, 'root', 'password', cmd)

def test():
    #1.get api_log delete threshold
    api_log_size_exceeds = int(log_files_size[0])* unit_to_int(log_files_size[1]) 
    #2.mock log files
    mock_log_files(api_log_size_exceeds) 
    #3.resize api-server.log
    threshold_size = int(api_threshold[0]) * unit_to_int(api_threshold[1])
    cmd = 'truncate -s +%s %szstack-api.log' % (threshold_size, LOG_PATH)
    test_lib.lib_execute_ssh_cmd(MN_IP, 'root', 'password', cmd)
    #4.restart_node
    cmd = 'zstack-ctl restart_node'
    test_lib.lib_execute_ssh_cmd(MN_IP, 'root', 'password', cmd, timeout = 300)
    #5.check
    cmd = "ls -l %s|grep %s|awk '{print $5}'" % (LOG_PATH, log_files_format)
    test_util.test_logger("@@DEBUG-log-files-format@@:%s" % log_files_format)
    log_size_list = test_lib.lib_execute_ssh_cmd(MN_IP, 'root', 'password', cmd).split('\n')
    test_util.test_logger("@@DEBUG@@:%s" % log_size_list)
    log_size_list.remove('')
    log_size_sum = sum(map(int, log_size_list))
    test_util.test_logger("@@DEBUG@@\n log_size_sum:{}\n api_log_size_exceeds:{}".format(log_size_sum, api_log_size_exceeds))
    if log_size_sum > api_log_size_exceeds:
        test_util.test_fail("Delete mn log check failed!\n log_size_sum:{}\n api_log_size_exceeds:{}".format(log_size_sum, api_log_size_exceeds))
    test_util.test_pass("pass")
    
def error_cleanup():
    pass
def env_recover():
    pass
