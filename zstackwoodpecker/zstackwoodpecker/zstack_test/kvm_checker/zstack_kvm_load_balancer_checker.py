import os
import sys
import traceback

import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.header.load_balancer as lb_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.shell as shell
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import apibinding.inventory as inventory

class zstack_kvm_lbl_checker(checker_header.TestChecker):
    '''check virtual router load balancer listener. '''

    def set_lbl(self, lbl):
        self.lbl = lbl
        self.lbl_uuid = lbl.get_load_balancer_listener().uuid

    def get_ssh_ip_result(self):
        vm = self.vm_list[0]
        host = test_lib.lib_get_vm_host(vm)
        port = self.lbl.get_creation_option().get_load_balancer_port()
        iport = self.lbl.get_creation_option().get_instance_port()
        if iport == 22:
            vm_command = '/sbin/ip a|grep inet'
            vm_cmd_result = test_lib.lib_execute_ssh_cmd(self.vip_ip, \
                test_lib.lib_get_vm_username(vm), \
                test_lib.lib_get_vm_password(vm), \
                vm_command,\
                port = port)
        if iport == 80:
            vm_command = 'curl %s:%s' % (self.vip_ip, port)
            vm_cmd_result = shell.call('%s' % vm_command)

        if not vm_cmd_result:
            test_util.test_logger('Checker result: FAIL to execute test ssh command in vip: %s for lb: %s.' % (self.vip_ip, self.lbl_uuid))
            return False
        for key, values in self.vm_ip_test_dict.iteritems():
            if key in vm_cmd_result:
                self.vm_ip_test_dict[key] += 1
                break

        return True

    def do_rr_check(self):
        lb_num = len(self.vm_list)
        tmp_num = lb_num
        while (tmp_num > 0):
            if not self.get_ssh_ip_result():
                return self.judge(False)
            tmp_num -= 1

        for key, values in self.vm_ip_test_dict.iteritems():
            if values != 1:
                test_util.test_logger('Load Balance %s algorithm test failed, since [ip]: %s is not scheduled on [load balancer listener]: %s. The full test result: %s' % (self.algorithm, key, self.lbl_uuid, self.vm_ip_test_dict))
                return self.judge(False)

        tmp_num = lb_num * 2 
        while (tmp_num > 0):
            if not self.get_ssh_ip_result():
                return self.judge(False)
            tmp_num -= 1

        for key, values in self.vm_ip_test_dict.iteritems():
            if values != 3:
                test_util.test_logger('Load Balance %s test failed, since [ip]: %s is not scheduled for 3 times on [load balancer listener]: %s. The full test result: %s' % (self.algorithm, key, self.lbl_uuid, self.vm_ip_test_dict))
                return self.judge(False)
        test_util.test_logger('Load Balance with %s algorithm test Pass. Destination IP and reach times: %s' % (self.algorithm, self.vm_ip_test_dict))
        return self.judge(True)

    def do_lc_check(self):
        pass

    def do_so_check(self):
        tmp_num = 5
        while (tmp_num > 0):
            if not self.get_ssh_ip_result():
                return self.judge(False)
            tmp_num -= 1

        for key, values in self.vm_ip_test_dict.iteritems():
            if values != 0 and values != 5:
                test_util.test_logger('Load Balance: %s with source algorithm test failed, since [ip]: %s is scheduled %s times. Full test result: %s' % (self.lbl_uuid, key, values, self.vm_ip_test_dict))
                return self.judge(False)
        test_util.test_logger('Load Balance with %s algorithm test Pass. Destination IP and reach times: %s' % (self.algorithm, self.vm_ip_test_dict))
        return self.judge(True)

    def check(self):
        super(zstack_kvm_lbl_checker, self).check()
        self.vm_nic_uuids = self.lbl.get_vm_nics_uuid()
        self.algorithm = self.lbl.get_algorithm()
        self.vm_list = []
        self.vm_ip_test_dict = {}

        if self.lbl.get_creation_option().get_instance_port() != 22 and self.lbl.get_creation_option().get_instance_port() != 80:
            test_util.test_logger('LBL target port is not 22 or 80, skip test.')
            return self.judge(self.exp_result)

        for vm_nic_uuid in self.vm_nic_uuids:
            vm = test_lib.lib_get_vm_by_nic(vm_nic_uuid)
            if vm.state == 'Running':
                nic_ip = test_lib.lib_get_nic_by_uuid(vm_nic_uuid).ip
                self.vm_ip_test_dict[nic_ip] = 0
                self.vm_list.append(vm)

        if not self.vm_list:
            test_util.test_logger('There is not living vm for load balancer test')
            return self.judge(False)

        cond = res_ops.gen_query_conditions('listeners.uuid', '=', self.lbl_uuid)
        vip_uuid = res_ops.query_resource(res_ops.LOAD_BALANCER, cond)[0].vipUuid
        cond = res_ops.gen_query_conditions('uuid', '=', vip_uuid)
        self.vip_ip = res_ops.query_resource(res_ops.VIP, cond)[0].ip

        if not len(self.vm_list) > 1:
            self.do_so_check()
            return

        if self.algorithm == lb_header.LB_ALGORITHM_RR:
            self.do_rr_check()
        elif self.algorithm == lb_header.LB_ALGORITHM_LC:
            #self.do_lc_check()
            #If not consider long connection, leastconn is same as round robin.
            self.do_rr_check()
        elif self.algorithm == lb_header.LB_ALGORITHM_SO:
            self.do_so_check()

