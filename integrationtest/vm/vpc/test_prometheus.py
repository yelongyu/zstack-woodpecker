'''
New Integration Test for test prometheus.
Test step:
    1.Create a vr vm and a vpc vrouter
    2.Check prometheus config file and prometheus data
    3.Reconnect hosts and check again
    4.Restart mn node and check again

@author: chenyuan.xu
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import apibinding.inventory as inventory
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
host_ip = None
mn_ip = None
host_uuid = None

def check_host_prometheus_conf():
    global host_ip
    global host_uuid
    global mn_ip

    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
#    host_list = test_stub.get_sce_hosts(test_lib.all_scenario_config, test_lib.scenario_file)
    host_list = test_lib.lib_get_all_hosts_from_plan()
    cmd = 'yum install -y jq --nogpgcheck'
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)

    for host in host_list:
        host_ip = host.managementIp_
        host_hostname = host_ip.replace('.', '-')
        host_uuid = test_lib.lib_get_host_by_ip(host_ip).uuid
        if host_ip == mn_ip:
            cmd = "jq -r '.[].targets[]' /usr/local/zstacktest/prometheus/discovery/management-node/management-server-exporter.json"
            cmd_out = test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)
            expect_result = mn_ip + ':' + str(8081)
            if cmd_out.strip() != expect_result.strip():
                test_util.test_fail('targets in management-node-exporter.json is not right.')
        else:
            cmd = "jq -r '.[].targets[]' /usr/local/zstacktest/prometheus/discovery/hosts/%s-%s.json" % (host_uuid, host_hostname)
            cmd_out =  test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)
            expect_result1 = host_ip + ':' + str(9103)
            expect_result2 = host_ip + ':' + str(9100)
            expect_result3 = host_ip + ':' + str(7069)
            if expect_result1 not in cmd_out or expect_result2 not in cmd_out or expect_result3 not in cmd_out:
                test_util.test_fail('targets in hosts/%s-%s.json is not right.') % (host_uuid, host_hostname)
            cmd = "jq -r '.[].labels[]' /usr/local/zstacktest/prometheus/discovery/hosts/%s-%s.json" % (host_uuid, host_hostname)
            cmd_out =  test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)
            if host_uuid.strip() != cmd_out.strip():
                test_util.test_fail('labels in hosts/%s-%s.json is not right.') % (host_uuid, host_hostname)

def check_vrouter_prometheus_conf():
    test_util.test_dsc("Check vrouters' prometheus config.")
    vrs = test_lib.lib_get_all_vrs()
    for vr in vrs:
        vr_ip = test_lib.lib_find_vr_mgmt_ip(vr)
        vr_hostname = vr_ip.replace('.', '-')
        conditions = res_ops.gen_query_conditions('vmNics.ip', '=', vr_ip)
        vr_uuid  = res_ops.query_resource(res_ops.VIRTUALROUTER_VM, conditions)[0].uuid
        cmd = "jq -r '.[].targets[]' /usr/local/zstacktest/prometheus/discovery/vrouter/%s-%s.json" % (vr_uuid,vr_hostname)
        cmd_out = test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)
        expect_result = vr_ip + ':' + str(7272)
        if cmd_out.strip() != expect_result.strip():
            test_util.test_fail('targets in vrouter/%s-%s.json is not right.') % (vr_uuid,vr_hostname)
        cmd = "jq -r '.[].labels[]' /usr/local/zstacktest/prometheus/discovery/vrouter/%s-%s.json" % (vr_uuid,vr_hostname)
        cmd_out = test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)
        if cmd_out.strip() != vr_uuid.strip():
                test_util.test_fail('labels in vrouter/%s-%s.json is not right.') % (vr_uuid,vr_hostname)

def check_prometheus_data():
    test_util.test_dsc("Check prometheus data.")
    cmd = "ps -ef|grep [t]ools/prometheus |awk '{for(i=7+1;i<=NF;i++)printf $i \" \";printf\"\\n\"}'"
    cmd_out = test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)
    if cmd_out == None:
        test_util.test_fail('prometheus agent is not enabled.')
    cmd = 'ls -A /var/lib/zstack/prometheus/data/ |wc -w'
    cmd_out = test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)
    if cmd_out <= 10:
        test_util.test_fail('prometheus data is null.')

def test():
    test_util.test_dsc("create vr vm and vpc vrouter")
    vm = test_stub.create_vr_vm('vr_vm','imageName_s','l3NoVlanNetworkName2')
    test_obj_dict.add_vm(vm)

    if not test_lib.lib_find_vr_by_vm(vm.vm) or not test_lib.lib_find_vr_by_vm(vm.vm)[0]:
        test_lib.lib_error_cleanup(test_obj_dict)
        test_util.test_skip("skip the test for no vr found in the env.")
    vpc_vr = test_stub.create_vpc_vrouter()
    check_host_prometheus_conf()
    check_vrouter_prometheus_conf()
    check_prometheus_data()
    hosts = test_lib.lib_get_all_hosts_from_plan()
    
    for host in hosts:
        host_ops.reconnect_host(host_uuid)
    check_host_prometheus_conf()
    check_vrouter_prometheus_conf()
    check_prometheus_data()

    test_lib.lib_execute_ssh_cmd(mn_ip,"root","password","zstack-ctl restart_node",timeout=300)
    check_host_prometheus_conf()
    check_vrouter_prometheus_conf()
    check_prometheus_data()

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Test prometheus Success')

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
