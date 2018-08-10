'''
Generate collectd data for vm/host

@author: jiajun
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import zstacklib.utils.shell as shell
import threading
import time
import os

test_stub = test_lib.lib_get_test_stub()

services = ['influxdb', 'prometheus']
#services = ['zstack']
COLLECTD_CONF_DIR = '/tmp/zstack/collectd'
PROMETHEUSE_HOSTS_DIR = '/usr/local/zstacktest/prometheus/discovery/hosts/'
COLLECTD_LISTION_PORT = 35826
COLLECTD_WEB_PORT = 55826

HOST_DISKS = ['vda']
HOST_NICS = ['eth0']
VM_DISKS = ['vda']
VM_NICS = ['vnic1.0']

def test():

    for name in services:
        if not test_lib.lib_check_pid(name):
            test_util.test_fail("No %s process available" % name)

    collectdFile = ''
    list_port = COLLECTD_LISTION_PORT
    web_port = COLLECTD_WEB_PORT

    hosts = res_ops.query_resource_fields(res_ops.HOST)

    if not os.path.exists(COLLECTD_CONF_DIR):
        file_path = os.path.join(COLLECTD_CONF_DIR, 'modules')
        os.makedirs(COLLECTD_CONF_DIR, 0755)
        shell.call('cp -r %s/integrationtest/vm/simulator/collectd_modules \
                   %s' % (os.environ.get('woodpecker_root_path'), file_path))
    else:
        for i in os.listdir(COLLECTD_CONF_DIR):
            file_path = os.path.join(COLLECTD_CONF_DIR, i)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                if os.path.basename(file_path) == 'modules':
                    test_util.test_logger('modules %s already there' % file_path)
                else:
                    test_util.test_logger('no moudles folder found under %s\
                            , go to create and copy modules' % COLLECTD_CONF_DIR)
                    shell.call('cp -r %s/integrationtest/vm/simulator/collectd_modules \
                            %s' % (os.environ.get('woodpecker_root_path'), file_path))

    if not os.path.exists(PROMETHEUSE_HOSTS_DIR):
        os.makedirs(PROMETHEUSE_HOSTS_DIR, 0755)
    else:
        for i in os.listdir(PROMETHEUSE_HOSTS_DIR):
            file_path = os.path.join(PROMETHEUSE_HOSTS_DIR, i)
            os.remove(file_path)

    for i in range(0, len(hosts)):
        collectdFile = test_stub.generate_collectd_conf(hosts[i], COLLECTD_CONF_DIR, list_port, HOST_DISKS, HOST_NICS, VM_DISKS, VM_NICS)

        thread_1 = threading.Thread(target=test_stub.collectd_trigger, args=(collectdFile,))
        thread_2 = threading.Thread(target=test_stub.collectd_trigger, args=(collectdFile,))
        thread_3 = threading.Thread(target=test_stub.collectd_exporter_trigger, args=(list_port, web_port))
        #while threading.active_count() > 10:
        time.sleep(2)
        thread_1.setDaemon(True)
        thread_2.setDaemon(True)
        thread_3.setDaemon(True)
        thread_1.start()
        thread_2.start()
        thread_3.start()

        test_stub.prometheus_conf_generate(hosts[i], web_port, '127.0.0.1')

        list_port += 1
        web_port += 1

    test_util.test_pass('Successfully generate collectd data for prometheus')

def error_cleanup():
    pass
