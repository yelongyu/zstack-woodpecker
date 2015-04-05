'''

Integration Test Teardown case

@author: Youyk
'''

import zstackwoodpecker.setup_actions as setup_actions
from zstackwoodpecker import test_util
from zstackwoodpecker import clean_util
from zstacklib.utils import linux
from zstacklib.utils import http
import zstackwoodpecker.test_lib as test_lib
from zstacktestagent.plugins import host as host_plugin
from zstacktestagent import testagent

def test():
    clean_util.cleanup_all_vms_violently()
    clean_util.cleanup_none_vm_volumes_violently()
    clean_util.umount_all_primary_storages_violently()
    clean_util.cleanup_backup_storage()
    test_lib.setup_plan.stop_node()
    #linux.remove_vlan_eth("eth0", 10)
    #linux.remove_vlan_eth("eth0", 11)
    cmd = host_plugin.DeleteVlanDeviceCmd()
    cmd.vlan_ethname = 'eth0.10'
    
    hosts = test_lib.lib_get_all_hosts_from_plan()
    if type(hosts) != type([]):
        hosts = [hosts]
    for host in hosts:
        http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.DELETE_VLAN_DEVICE_PATH), cmd)

    cmd.vlan_ethname = 'eth0.11'
    for host in hosts:
        http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.DELETE_VLAN_DEVICE_PATH), cmd)

    test_lib.lib_cleanup_host_ip_dict()
    test_util.test_pass('VirtualRouter Teardown Success')
