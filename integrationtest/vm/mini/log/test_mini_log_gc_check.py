'''
log delete global config check
1.get global config (name=log.delete.accumulatedFileSize) default value & check
2.get threshold from log4j2.xml & check
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

def unit_to_int(unit):
    return 1024*1024 if unit=='MB' else 1024*1024*1024

def test():
    #get mn_log delete threshold & AccumulatedFileSize from log4j2.xml
    MN_IP = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    cmd = "sshpass -p password scp root@{}:/usr/local/zstacktest/apache-tomcat/webapps/zstack/WEB-INF/classes/log4j2.xml /tmp/".format(MN_IP)
    os.system(cmd)
    LOG4J2_TREE = et.ElementTree(file='/tmp/log4j2.xml')
    LOG_PATH = "/usr/local/zstacktest/apache-tomcat/logs/"
    log_files_size = LOG4J2_TREE.getroot().findall('./Appenders/RollingFile/DefaultRolloverStrategy/Delete/IfFileName/IfAny/IfAccumulatedFileSize')[0].attrib['exceeds'].split(' ')
    test_util.test_logger("@DEBUG-exceeds:%s@" % log_files_size)
    log_files_format = LOG4J2_TREE.getroot().findall('./Appenders/RollingFile/DefaultRolloverStrategy/Delete/IfFileName')[0].attrib['glob'].replace('*', '.*')
    
    #1.get global config value(unit==GB) & check
    gc_conf_size = int(conf_ops.get_global_config_value("managementServer","log.delete.accumulatedFileSize")) * 1024 * 1024 * 1024
    if gc_conf_size <= 0:
        test_util.test_fail("Global config default value check Failed!\n default_value:%s" % gc_conf_size)
    #2.get threshold from log4j2.xml & check 
    mn_log_size_exceeds = int(log_files_size[0])* unit_to_int(log_files_size[1]) 
    if gc_conf_size <= mn_log_size_exceeds:
        test_util.test_fail("AccumulatedFileSize check failed!\n mn_log_size_exceeds:{}\n log.delete.accumulatedFileSize:{}".format(mn_log_size_exceeds, gc_conf_size))
    test_util.test_pass("pass")
    
def error_cleanup():
    pass
def env_recover():
    pass
