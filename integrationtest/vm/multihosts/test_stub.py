'''

Create an unified test_stub to share test operations

@author: Youyk
'''
import os
import random
import commands
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util  as test_util
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.header.host as host_header
import apibinding.inventory as inventory
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.datamigrate_operations as datamigr_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vpc_operations as vpc_ops
import zstackwoodpecker.header.vm as vm_header
import zstacklib.utils.xmlobject as xmlobject
import zstacklib.utils.ssh as ssh
import threading
import time
import sys
import telnetlib
import random
from contextlib import contextmanager
from functools import wraps
import itertools
import types
import copy
#import traceback



import zstackwoodpecker.test_state as test_state
Port = test_state.Port

rule1_ports = Port.get_ports(Port.rule1_ports)
rule2_ports = Port.get_ports(Port.rule2_ports)
rule3_ports = Port.get_ports(Port.rule3_ports)
rule4_ports = Port.get_ports(Port.rule4_ports)
rule5_ports = Port.get_ports(Port.rule5_ports)
denied_ports = Port.get_denied_ports()
#rule1_ports = [1, 22, 100]
#rule2_ports = [9000, 9499, 10000]
#rule3_ports = [60000, 60010, 65535]
#rule4_ports = [5000, 5501, 6000]
#rule5_ports = [20000, 28999, 30000]
#test_stub.denied_ports = [101, 4999, 8990, 15000, 30001, 49999]
target_ports = rule1_ports + rule2_ports + rule3_ports + rule4_ports + rule5_ports + denied_ports

def create_volume(volume_creation_option=None, from_offering=True):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('vr_test_volume')

    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create(from_offering)
    return volume

def create_vr_vm(vm_name, image_name, l3_name):
    imagename = os.environ.get(image_name)
    l3name = os.environ.get(l3_name)
    vm = create_vm(vm_name, imagename, l3name)
    return vm

def create_vm(vm_name, image_name, l3_name, host_uuid = None, disk_offering_uuids=None):
    vm_creation_option = test_util.VmOption()
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_timeout(600000)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if disk_offering_uuids:
        vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vm_with_instance_offering(vm_name, image_name, l3_name, instance_offering):
    vm_creation_option = test_util.VmOption()
    image_uuid = test_lib.lib_get_ready_image_by_name(image_name).uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering.uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_timeout(600000)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vpc_vrouter(vr_name='test_vpc'):
    conf = res_ops.gen_query_conditions('name', '=', 'test_vpc')
    vr_list = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)
    if vr_list:
        return ZstackTestVR(vr_list[0])
    vr_offering = res_ops.get_resource(res_ops.VR_OFFERING)[0]
    vr_inv =  vpc_ops.create_vpc_vrouter(name=vr_name, virtualrouter_offering_uuid=vr_offering.uuid)
    return ZstackTestVR(vr_inv)

def query_vpc_vrouter(vr_name):
    conf = res_ops.gen_query_conditions('name', '=', vr_name)
    vr_list = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)
    if vr_list:
        return ZstackTestVR(vr_list[0])

def attach_l3_to_vpc_vr(vpc_vr, l3_list):
    for l3 in l3_list:
        vpc_vr.add_nic(l3.uuid)

def attach_l3_to_vpc_vr_by_uuid(vpc_vr, l3_uuid):
    vpc_vr.add_nic(l3_uuid)

class ZstackTestVR(vm_header.TestVm):
    def __init__(self, vr_inv):
        super(ZstackTestVR, self).__init__()
        self._inv = vr_inv

    def __hash__(self):
        return hash(self.inv.uuid)

    def __eq__(self, other):
        return self.inv.uuid == other.inv.uuid

    @property
    def inv(self):
        return self._inv

    @inv.setter
    def inv(self, value):
        self._inv = value

    def destroy(self, session_uuid = None):
        vm_ops.destroy_vm(self.inv.uuid, session_uuid)
        super(ZstackTestVR, self).destroy()

    def reboot(self, session_uuid = None):
        self.inv = vm_ops.reboot_vm(self.inv.uuid, session_uuid)
        super(ZstackTestVR, self).reboot()

    def reconnect(self, session_uuid = None):
        self.inv = vm_ops.reconnect_vr(self.inv.uuid, session_uuid)

    def migrate(self, host_uuid, timeout = None, session_uuid = None):
        self.inv = vm_ops.migrate_vm(self.inv.uuid, host_uuid, timeout, session_uuid)
        super(ZstackTestVR, self).migrate(host_uuid)

    def migrate_to_random_host(self, timeout = None, session_uuid = None):
        host_uuid = random.choice([host.uuid for host in res_ops.get_resource(res_ops.HOST)
                                                      if host.uuid != test_lib.lib_find_host_by_vm(self.inv).uuid])
        self.inv = vm_ops.migrate_vm(self.inv.uuid, host_uuid, timeout, session_uuid)
        super(ZstackTestVR, self).migrate(host_uuid)

    def update(self):
        '''
        If vm's status was changed by none vm operations, it needs to call
        vm.update() to update vm's infromation.

        The none vm operations: host.maintain() host.delete(), zone.delete()
        cluster.delete()
        '''
        super(ZstackTestVR, self).update()
        if self.get_state != vm_header.EXPUNGED:
            update_inv = test_lib.lib_get_vm_by_uuid(self.inv.uuid)
            if update_inv:
                self.inv = update_inv
                #vm state need to chenage to stopped, if host is deleted
                host = test_lib.lib_find_host_by_vm(update_inv)
                if not host and self.inv.state != vm_header.STOPPED:
                    self.set_state(vm_header.STOPPED)
            else:
                self.set_state(vm_header.EXPUNGED)
            return self.inv


def add_test_minimal_iso(iso_name):
    import zstackwoodpecker.zstack_test.zstack_test_image as test_image
    img_option = test_util.ImageOption()
    img_option.set_name(iso_name)
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_url(os.environ.get('isoForVmUrl'))
    image_inv = img_ops.add_iso_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
    return image

def add_test_root_volume_offering(root_offering_name, root_offering_size):
    import zstackwoodpecker.operations.volume_operations as vol_ops
    root_offering_option = test_util.DiskOfferingOption()
    root_offering_option.set_name(root_offering_name)
    root_offering_option.set_diskSize(root_offering_size)
    root_volume_offering = vol_ops.create_volume_offering(root_offering_option)
    return root_volume_offering

def add_test_vm_offering(cpuNum, memorySize, vm_offering_name):
    vm_offering_option = test_util.InstanceOfferingOption()
    vm_offering_option.set_cpuNum(cpuNum)
    vm_offering_option.set_memorySize(memorySize)
    vm_offering_option.set_name(vm_offering_name)
    vm_offering = vm_ops.create_instance_offering(vm_offering_option)
    return vm_offering

def create_vm_with_iso_for_test(vm_offering_uuid, iso_uuid, root_volume_offering_uuid, vm_name = None):
    import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(vm_offering_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(iso_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_root_disk_uuid(root_volume_offering_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vm_with_iso(l3_uuid_list, image_uuid, vm_name = None, root_disk_uuids = None, instance_offering_uuid = None, \
                       disk_offering_uuids = None, default_l3_uuid = None, system_tags = None, \
                       session_uuid = None, ps_uuid=None):
    import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    if not instance_offering_uuid:
        instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_root_disk_uuid(root_disk_uuids)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_default_l3_uuid(default_l3_uuid)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_session_uuid(session_uuid)
    vm_creation_option.set_ps_uuid(ps_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vm_with_fake_iso(vm_name, l3_name, session_uuid = None):
    img_option = test_util.ImageOption()
    img_option.set_name('fake_iso')
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('mediumDiskOfferingName')).uuid
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], \
            session_uuid)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    if os.system("sshpass -p password ssh %s 'ls  %s/apache-tomcat/webapps/zstack/static/zstack-repo/'" % (mn_ip, os.environ.get('zstackInstallPath'))) == 0:
        img_option.set_url('http://%s:8080/zstack/static/zstack-repo/7/x86_64/os/ks.cfg' % (mn_ip))
    else:
        img_option.set_url('http://%s:8080/zstack/static/zstack-dvd/ks.cfg' % (mn_ip))
    image_uuid = img_ops.add_iso_template(img_option).uuid

    vm_creation_option = test_util.VmOption()
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_root_disk_uuid(root_disk_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_iso_vm_with_random_offering(vm_name, l3_name=None, session_uuid=None, root_disk_uuid=None,
                                       instance_offering_uuid=None, host_uuid=None, disk_offering_uuids=None,
                                       root_password=None, ps_uuid=None, system_tags=None):
    img_option = test_util.ImageOption()
    img_option.set_name('fake_iso')
    ps_list = res_ops.query_resource_fields(res_ops.PRIMARY_STORAGE, [], session_uuid)
    bs_list = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], session_uuid)
    ps = None
    if ps_uuid:
        ps = random.choice([ps for ps in ps_list if ps.uuid == ps_uuid])
    if ps and (ps.type == "SharedBlock" or ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE):
        bs = random.choice([bs for bs in bs_list if (ps.type == "SharedBlock" and bs.type == 'ImageStoreBackupStorage') or (ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE and bs.type == 'Ceph')])
        bs_uuid = bs.uuid
    else:
        bs_uuid = bs_list[0].uuid 

    img_option.set_backup_storage_uuid_list([bs_uuid])
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    if os.system("sshpass -p password ssh %s 'ls  %s/apache-tomcat/webapps/zstack/static/zstack-repo/'" % (mn_ip, os.environ.get('zstackInstallPath'))) == 0:
        img_option.set_url('http://%s:8080/zstack/static/zstack-repo/7/x86_64/os/ks.cfg' % (mn_ip))
    else:
        img_option.set_url('http://%s:8080/zstack/static/zstack-dvd/ks.cfg' % (mn_ip))
    image_uuid = img_ops.add_iso_template(img_option).uuid

    if l3_name:
        l3name = os.environ.get(l3_name)
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3name).uuid
    else:
        l3_net_uuid = random.choice(res_ops.get_resource(res_ops.L3_NETWORK)).uuid

    if not root_disk_uuid:
        root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('mediumDiskOfferingName')).uuid

    if not instance_offering_uuid:
        conf = res_ops.gen_query_conditions('type', '=', 'UserVM')
        instance_offering_uuid = random.choice(res_ops.query_resource(res_ops.INSTANCE_OFFERING, conf)).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_root_disk_uuid(root_disk_uuid)
    if system_tags:
        vm_creation_option.set_system_tags(system_tags)
    if disk_offering_uuids:
        vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    if root_password:
        vm_creation_option.set_root_password(root_password)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)
    if ps_uuid:
        vm_creation_option.set_ps_uuid(ps_uuid)

    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm



def create_vm_with_random_offering(vm_name, image_name=None, l3_name=None, session_uuid=None,
                                   instance_offering_uuid=None, host_uuid=None, disk_offering_uuids=None,
                                   root_password=None, ps_uuid=None, system_tags=None, timeout=None, bs_type=None):
    if image_name:
        imagename = os.environ.get(image_name)
        image_uuid = test_lib.lib_get_image_by_name(imagename, bs_type).uuid
    else:
        conf = res_ops.gen_query_conditions('format', '!=', 'iso')
        conf = res_ops.gen_query_conditions('mediaType', '!=', 'ISO', conf)
        conf = res_ops.gen_query_conditions('system', '=', 'false', conf)
        image_uuid = random.choice(res_ops.query_resource(res_ops.IMAGE, conf)).uuid

    if l3_name:
        l3name = os.environ.get(l3_name)
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3name).uuid
    else:
        l3_net_uuid = random.choice(res_ops.get_resource(res_ops.L3_NETWORK)).uuid

    if not instance_offering_uuid:
        conf = res_ops.gen_query_conditions('type', '=', 'UserVM')
        instance_offering_uuid = random.choice(res_ops.query_resource(res_ops.INSTANCE_OFFERING, conf)).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_timeout(1800000)
    if system_tags:
        vm_creation_option.set_system_tags(system_tags)
    if disk_offering_uuids:
        vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    if root_password:
        vm_creation_option.set_root_password(root_password)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)
    if ps_uuid:
        vm_creation_option.set_ps_uuid(ps_uuid)
    if timeout:
        vm_creation_option.set_timeout(timeout)

    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm


def create_multi_vms(name_prefix='', count=10, host_uuid=None, ps_uuid=None, data_volume_number=0, ps_uuid_for_data_vol=None, timeout=None, bs_type=None):
    vm_list = []
    for i in xrange(count):
        if not data_volume_number:
            vm = create_vm_with_random_offering(name_prefix+"{}".format(i), image_name='imageName_net',
                                                l3_name='l3VlanNetwork2', host_uuid=host_uuid, ps_uuid=ps_uuid, timeout=timeout, bs_type=bs_type)
        else:
            disk_offering_list = res_ops.get_resource(res_ops.DISK_OFFERING)
            disk_offering_uuids = [random.choice(disk_offering_list).uuid for _ in xrange(data_volume_number)]
            if ps_uuid_for_data_vol:
                vm = create_vm_with_random_offering(name_prefix+"{}".format(i), image_name='imageName_net',
                                                    l3_name='l3VlanNetwork2', host_uuid=host_uuid, ps_uuid=ps_uuid,
                                                    disk_offering_uuids=disk_offering_uuids,
                                                    system_tags=['primaryStorageUuidForDataVolume::{}'.format(ps_uuid_for_data_vol)], timeout=timeout, bs_type=bs_type)
            else:
                vm = create_vm_with_random_offering(name_prefix+"{}".format(i), image_name='imageName_net',
                                                    l3_name='l3VlanNetwork2', host_uuid=host_uuid, ps_uuid=ps_uuid,
                                                    disk_offering_uuids=disk_offering_uuids, timeout=timeout, bs_type=bs_type)

        vm_list.append(vm)
    for vm in vm_list:
        vm.check()
    if host_uuid:
        for vm in vm_list:
            assert vm.get_vm().hostUuid == host_uuid
    if ps_uuid:
        for vm in vm_list:
            root_volume = test_lib.lib_get_root_volume(vm.get_vm())
            assert root_volume.primaryStorageUuid == ps_uuid

    if ps_uuid_for_data_vol:
        for vm in vm_list:
            data_volume_list = [volume for volume in vm.get_vm().allVolumes if volume.type != 'Root']
            for data_volume in data_volume_list:
                assert data_volume.primaryStorageUuid == ps_uuid_for_data_vol

    return vm_list


def create_multi_volumes(count=10, host_uuid=None, ps=None):
    volume_list = []
    for i in xrange(count):
        disk_offering = random.choice(res_ops.get_resource(res_ops.DISK_OFFERING))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        if ps:
            volume_creation_option.set_primary_storage_uuid(ps.uuid)
            if ps.type == inventory.LOCAL_STORAGE_TYPE:
                if not host_uuid:
                    host_uuid = random.choice(res_ops.get_resource(res_ops.HOST)).uuid
            volume_creation_option.set_system_tags(['localStorage::hostUuid::{}'.format(host_uuid)])
        volume = create_volume(volume_creation_option)
        volume_list.append(volume)
    for volume in volume_list:
        volume.check()
    if ps:
        for volume in volume_list:
            assert volume.get_volume().primaryStorageUuid == ps.uuid
    return volume_list


def add_primaryStorage(first_ps=None):
    cluster_uuid = first_ps.attachedClusterUuids[0]
    ps_config = test_util.PrimaryStorageOption()
    if first_ps.type == inventory.LOCAL_STORAGE_TYPE:
        ps_config.set_name("local-ps2")
        ps_config.set_description("test")
        ps_config.set_zone_uuid(first_ps.zoneUuid)
        ps_config.set_type(first_ps.type)
        ps_config.set_url("/home/local-ps2")
    else:
        test_util.test_skip('currently only support add local storage')

    ps = ps_ops.create_local_primary_storage(ps_config)
    ps_ops.attach_primary_storage(ps.uuid, cluster_uuid)
    ps.attachedClusterUuids.append(cluster_uuid)
    return ps



def migrate_vm_to_random_host(vm):
    test_util.test_dsc("migrate vm to random host")
    if not test_lib.lib_check_vm_live_migration_cap(vm.vm):
        test_util.test_skip('skip migrate if live migrate not supported')
    target_host = test_lib.lib_find_random_host(vm.vm)
    current_host = test_lib.lib_find_host_by_vm(vm.vm)
    vm.migrate(target_host.uuid)

    new_host = test_lib.lib_get_vm_host(vm.vm)
    if not new_host:
        test_util.test_fail('Not find available Hosts to do migration')

    if new_host.uuid != target_host.uuid:
        test_util.test_fail('[vm:] did not migrate from [host:] %s to target [host:] %s, but to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid, new_host.uuid))
    else:
        test_util.test_logger('[vm:] %s has been migrated from [host:] %s to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid))

def create_sg(sg_creation_option=None):
    if not sg_creation_option:
        sg_creation_option = test_util.SecurityGroupOption()
        sg_creation_option.set_name('test_sg')
        sg_creation_option.set_description('test sg description')

    sg = zstack_sg_header.ZstackTestSecurityGroup()
    sg.set_creation_option(sg_creation_option)
    sg.create()
    return sg

def create_delete_account(account_name='test', session_uuid=None):
    try:
        account_inv = acc_ops.create_normal_account(account_name, 'password', session_uuid)
    except:
	test_util.test_logger('ignore exception')
    try:
        acc_ops.delete_account(account_inv.uuid, session_uuid)
    except:
        test_util.test_logger('ignore exception')

def exercise_connection(ops_num=120, thread_threshold=10):
    session_uuid = acc_ops.login_as_admin()
    for ops_id in range(ops_num):
        thread = threading.Thread(target=create_delete_account, args=(ops_id, session_uuid, ))
        while threading.active_count() > thread_threshold:
            time.sleep(0.5)
        exc = sys.exc_info()
        thread.start()

    while threading.activeCount() > 1:
        exc = sys.exc_info()
        time.sleep(0.1)
    acc_ops.logout(session_uuid)


def check_cpu_mem(vm, shutdown=False, window=False):
    zone_uuid = vm.get_vm().zoneUuid

    available_cpu, available_memory = check_available_cpu_mem(zone_uuid)
    vm_outer_cpu, vm_outer_mem = vm.get_vm().cpuNum, vm.get_vm().memorySize
    vm_internal_cpu, vm_internal_mem = check_vm_internal_cpu_mem(vm, shutdown, window)

    return available_cpu, available_memory, vm_outer_cpu, vm_outer_mem, vm_internal_cpu, vm_internal_mem


def check_available_cpu_mem(zone_uuid):
    available_cpu = test_lib.lib_get_cpu_memory_capacity([zone_uuid]).availableCpu
    available_memory = test_lib.lib_get_cpu_memory_capacity([zone_uuid]).availableMemory
    return available_cpu, available_memory


def check_window_vm_internal_cpu_mem(vm):
    vm_ip = vm.get_vm().vmNics[0].ip
    test_lib.lib_wait_target_up(vm_ip, '23', 360)
    vm_username = os.environ.get('winImageUsername')
    vm_password = os.environ.get('winImagePassword')
    tn=telnetlib.Telnet(vm_ip)
    tn.read_until("login: ")
    tn.write(vm_username+"\r\n")
    tn.read_until("password: ")
    tn.write(vm_password+"\r\n")
    tn.read_until(vm_username+">")
    tn.write("wmic cpu get NumberOfCores\r\n")
    vm_cpuinfo=tn.read_until(vm_username+">")
    tn.write("wmic computersystem get TotalPhysicalMemory\r\n")
    vm_meminfo=tn.read_until(vm_username+">")
    tn.close()
    test_util.test_logger(vm_cpuinfo.strip().split()[-2])
    test_util.test_logger(vm_meminfo.strip().split()[-2])
    return int(vm_cpuinfo.strip().split()[-2]), int(vm_meminfo.strip().split()[-2])/1024/1024


def check_vm_internal_cpu_mem(vm, shutdown, window):
    if window:
        return check_window_vm_internal_cpu_mem(vm)
    managerip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    vm_ip = vm.get_vm().vmNics[0].ip
    get_cpu_cmd = "cat /proc/cpuinfo| grep 'processor'| wc -l"
    if not shutdown:
        get_mem_cmd = "free -m |grep Mem"
    else:
        get_mem_cmd = "dmidecode -t 17 | grep 'Size:'"
    res = test_lib.lib_ssh_vm_cmd_by_agent(managerip, vm_ip, 'root',
                'password', get_cpu_cmd)
    vm_cpu = int(res.result.strip())
    res = test_lib.lib_ssh_vm_cmd_by_agent(managerip, vm_ip, 'root',
                'password', get_mem_cmd)
    vm_mem = int(res.result.split()[1])
    return vm_cpu, vm_mem


class TwoPrimaryStorageEnv(object):
    def __init__(self, test_object_dict, first_ps_vm_number=0, second_ps_vm_number=0, first_ps_volume_number=0, second_ps_volume_number=0,
                 vm_creation_with_volume_number=0):
        self._first_ps_vm_number = first_ps_vm_number
        self._second_ps_vm_number = second_ps_vm_number
        self._first_ps_volume_number = first_ps_volume_number
        self._second_ps_volume_number = second_ps_volume_number
        self._vm_creation_with_volume_number = vm_creation_with_volume_number
        self._test_object_dict = test_object_dict
        self._host_uuid = None
        self._first_ps = None
        self._second_ps = None
        self._first_ps_vm_list = []
        self._second_ps_vm_list = []
        self._first_ps_volume_list = []
        self._second_ps_volume_list = []
        self._new_ps = False

    def check_env(self):
        ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
        self._first_ps = ps_list[0]
        if len(ps_list) == 2:
            self._second_ps = ps_list[1]
        if self._first_ps.type == inventory.LOCAL_STORAGE_TYPE or self._second_ps.type == inventory.LOCAL_STORAGE_TYPE:
            self._host_uuid = random.choice(res_ops.get_resource(res_ops.HOST)).uuid

    def deploy_env(self):
        if self._first_ps_vm_number:
            self._first_ps_vm_list = create_multi_vms(name_prefix="vm_in_first_ps-", count=self._first_ps_vm_number,
                                                     host_uuid=self._host_uuid, ps_uuid=self._first_ps.uuid,
                                                     data_volume_number=self._vm_creation_with_volume_number)
            for vm in self._first_ps_vm_list:
                self._test_object_dict.add_vm(vm)

        if self._first_ps_volume_number:
            self._first_ps_volume_list = create_multi_volumes(count=self._first_ps_volume_number, host_uuid=self._host_uuid,
                                                            ps=self._first_ps)
            for volume in self._first_ps_volume_list:
                self._test_object_dict.add_volume(volume)

        if not self._second_ps:
            self._second_ps = add_primaryStorage(self._first_ps)
            self._new_ps = True

        if self._second_ps_vm_number:
            self._second_ps_vm_list = create_multi_vms(name_prefix="vm_in_second_ps-", count=self._second_ps_vm_number,
                                                      host_uuid=self._host_uuid, ps_uuid=self._second_ps.uuid)
            for vm in self._second_ps_vm_list:
                self._test_object_dict.add_vm(vm)

        if self._second_ps_volume_number:
            self._second_ps_volume_list = create_multi_volumes(count=self._second_ps_volume_number, host_uuid=self._host_uuid,
                                                             ps=self._second_ps)
            for volume in self._second_ps_volume_list:
                self._test_object_dict.add_volume(volume)

    @property
    def host_uuid(self):
        return self._host_uuid

    @property
    def first_ps(self):
        return self._first_ps

    @property
    def second_ps(self):
        return self._second_ps

    @property
    def first_ps_vm_list(self):
        return self._first_ps_vm_list

    @property
    def second_ps_vm_list(self):
        return self._second_ps_vm_list

    @property
    def first_ps_volume_list(self):
        return self._first_ps_volume_list

    @property
    def second_ps_volume_list(self):
        return self._second_ps_volume_list

    @property
    def new_ps(self):
        return self._new_ps

    def get_vm_list_from_ps(self, ps):
        if ps is self._first_ps:
            return self._first_ps_vm_list
        elif ps is self._second_ps:
            return self._second_ps_vm_list
        else:
            raise NameError

class SanAndCephPrimaryStorageEnv(object):
    def __init__(self, test_object_dict, first_ps_vm_number=0, second_ps_vm_number=0, first_ps_volume_number=0, second_ps_volume_number=0,
                 vm_creation_with_volume_number=0):
        self._first_ps_vm_number = first_ps_vm_number
        self._second_ps_vm_number = second_ps_vm_number
        self._first_ps_volume_number = first_ps_volume_number
        self._second_ps_volume_number = second_ps_volume_number
        self._vm_creation_with_volume_number = vm_creation_with_volume_number
        self._test_object_dict = test_object_dict
        self._host_uuid = None
        self._first_ps = None #San PS
        self._second_ps = None #Ceph PS
        self._first_ps_vm_list = []
        self._second_ps_vm_list = []
        self._first_ps_volume_list = []
        self._second_ps_volume_list = []
        self._new_ps = False
        
    def check_env(self):
        ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
        self._first_ps = random.choice([ps for ps in ps_list if ps.type == "SharedBlock"])
        # if len(ps_list) == 2:
        self._second_ps = random.choice([ps for ps in ps_list if ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE])
        if self._first_ps.type == inventory.LOCAL_STORAGE_TYPE or self._second_ps.type == inventory.LOCAL_STORAGE_TYPE:
            self._host_uuid = random.choice(res_ops.get_resource(res_ops.HOST)).uuid

    def deploy_env(self):
        if self._first_ps_vm_number:
            self._first_ps_vm_list = create_multi_vms(name_prefix="vm_in_first_ps-", count=self._first_ps_vm_number,
                                                     host_uuid=self._host_uuid, ps_uuid=self._first_ps.uuid,
                                                     data_volume_number=self._vm_creation_with_volume_number, 
                                                     bs_type='ImageStoreBackupStorage')
            for vm in self._first_ps_vm_list:
                self._test_object_dict.add_vm(vm)

        if self._first_ps_volume_number:
            self._first_ps_volume_list = create_multi_volumes(count=self._first_ps_volume_number, host_uuid=self._host_uuid,
                                                            ps=self._first_ps)
            for volume in self._first_ps_volume_list:
                self._test_object_dict.add_volume(volume)

        if not self._second_ps:
            self._second_ps = add_primaryStorage(self._first_ps)
            self._new_ps = True

        if self._second_ps_vm_number:
            self._second_ps_vm_list = create_multi_vms(name_prefix="vm_in_second_ps-", count=self._second_ps_vm_number,
                                                      host_uuid=self._host_uuid, ps_uuid=self._second_ps.uuid, 
                                                      bs_type='Ceph')
            for vm in self._second_ps_vm_list:
                self._test_object_dict.add_vm(vm)

        if self._second_ps_volume_number:
            self._second_ps_volume_list = create_multi_volumes(count=self._second_ps_volume_number, host_uuid=self._host_uuid,
                                                             ps=self._second_ps)
            for volume in self._second_ps_volume_list:
                self._test_object_dict.add_volume(volume)

    @property
    def host_uuid(self):
        return self._host_uuid

    @property
    def first_ps(self):
        return self._first_ps

    @property
    def second_ps(self):
        return self._second_ps

    @property
    def first_ps_vm_list(self):
        return self._first_ps_vm_list

    @property
    def second_ps_vm_list(self):
        return self._second_ps_vm_list

    @property
    def first_ps_volume_list(self):
        return self._first_ps_volume_list

    @property
    def second_ps_volume_list(self):
        return self._second_ps_volume_list

    @property
    def new_ps(self):
        return self._new_ps

    def get_vm_list_from_ps(self, ps):
        if ps is self._first_ps:
            return self._first_ps_vm_list
        elif ps is self._second_ps:
            return self._second_ps_vm_list
        else:
            raise NameError

def check_vm_running_on_host(vm_uuid, host_ip):
    cmd = "virsh list|grep %s|awk '{print $3}'" %(vm_uuid)
    host_username = os.environ.get('hostUsername')
    host_password = os.environ.get('hostPassword')
    vm_is_exist = True if test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd) else False

    return vm_is_exist

def stop_host(host_vm, scenarioConfig, force=None):
    host_vm_uuid = host_vm.uuid_
    mn_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    try:
        host_inv = sce_ops.stop_vm(mn_ip, host_vm_uuid,force=force)
        test_lib.lib_wait_target_down(mn_ip, '22', 120)
        return host_inv
    except:
        test_util.test_logger("Fail to stop host [%s]" % host_vm.ip_)
        return False

def start_host(host_vm, scenarioConfig):
    host_vm_uuid = host_vm.uuid_
    mn_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    try:
        host_inv = sce_ops.start_vm(mn_ip, host_vm_uuid)
        return host_inv
    except:
        test_util.test_logger("Fail to start host [%s]" % host_vm.ip_)
        return False

def recover_host(host_vm, scenarioConfig, deploy_config):
    stop_host(host_vm, scenarioConfig)
    host_inv = start_host(host_vm, scenarioConfig)
    if not host_inv:
       return False
    recover_host_vlan(host_vm, scenarioConfig, deploy_config)

def recover_host_vlan(host_vm, scenarioConfig, deploy_config):
    host_ip = host_vm.ip_
    test_lib.lib_wait_target_up(host_ip, '22', 120)
    host_config = sce_ops.get_scenario_config_vm(host_vm.name_,scenarioConfig)
    for l3network in xmlobject.safe_list(host_config.l3Networks.l3Network):
        if hasattr(l3network, 'l2NetworkRef'):
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                nic_name = sce_ops.get_ref_l2_nic_name(l2networkref.text_, deploy_config)
                if nic_name.find('.') >= 0 :
                    vlan = nic_name.split('.')[1]
                    test_util.test_logger('[vm:] %s %s is created.' % (host_ip, nic_name.replace("eth", "zsn")))
                    cmd = 'vconfig add %s %s' % (nic_name.split('.')[0].replace("eth", "zsn"), vlan)
                    test_lib.lib_execute_ssh_cmd(host_ip, host_config.imageUsername_, host_config.imagePassword_, cmd)
    return True

host_username = os.environ.get('physicalHostUsername')
host_password = os.environ.get('physicalHostPassword')
host_password2 = os.environ.get('physicalHostPassword2')

def down_host_network(host_ip, scenarioConfig):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_ip)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    cmd = "virsh domiflist %s|sed -n '3p'|awk '{print $1}'|xargs -i virsh domif-setlink %s {} down" % (host_vm_inv.uuid, host_vm_inv.uuid)
    if test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, cmd)
    else:
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s;%s with username %s" %(host_inv.managementIp, host_password, host_password2, host_username))

def up_host_network(host_ip, scenarioConfig):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_ip)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    cmd = "virsh domiflist %s|sed -n '3p'|awk '{print $1}'|xargs -i virsh domif-setlink %s {} up" % (host_vm_inv.uuid, host_vm_inv.uuid)
    if test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, cmd)
    else:
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s;%s with username %s" %(host_inv.managementIp, host_password, host_password2, host_username))

def recover_smp_nfs_server(host_ip):
    cmd = "bash /etc/rc.d/rc.local"
    if test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password2, cmd) == False :
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s with username %s" %(host_ip, host_password2, host_username))

def execute_cmd_in_host(host_vm, scenarioConfig, cmd):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_vm.ip_)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]
    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)
    sce_ops.execute_in_vm_console(zstack_management_ip, host_inv.managementIp, host_vm_inv.uuid, host_vm_config, cmd)

def get_host_network_status(host_ip, scenarioConfig):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_ip)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    cmd = "virsh domiflist %s|sed -n '3p'|awk '{print $1}'|xargs -i virsh domif-getlink %s {}" % (host_vm_inv.uuid, host_vm_inv.uuid)
    if test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, cmd)
    else:
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s;%s with username %s" %(host_inv.managementIp, host_password, host_password2, host_username))

def get_mn_host_management_ip():
    scenario_file = test_lib.scenario_file
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    management_ip = sce_ops.get_host_management_ip_by_public_ip_from_scenario_file(scenario_file, mn_ip)
    if not management_ip:
        return mn_ip
    else:
        return management_ip

def get_sce_hosts(scenarioConfig=test_lib.all_scenario_config, scenarioFile=test_lib.scenario_file):
    host_list = []

    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return host_list

    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            with open(scenarioFile, 'r') as fd:
                xmlstr = fd.read()
                fd.close()
                scenario_file = xmlobject.loads(xmlstr)
                for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                    if s_vm.name_ == vm.name_:
                        host_list.append(s_vm)
    return host_list

def get_sce_host_by_ip(host_ip):
    sce_host_list = get_sce_hosts()
    for sce_host in sce_host_list:
        for sce_ip in xmlobject.safe_list(sce_host.ips.ip):
            if sce_ip.ip_ == host_ip:
                return sce_host

    return None

def get_host_has_vr():
    cond = res_ops.gen_query_conditions('type', '=', 'ApplianceVm')
    vr_list = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
    host_list = []
    for vr in vr_list:
        if vr.hostUuid not in host_list:
            host_list.append(vr.hostUuid)
    return host_list

def get_host_has_mn():
    mns = res_ops.query_resource(res_ops.MANAGEMENT_NODE)
    mn_host = []
    host_list = []
    for mn in mns:
        if mn.hostName not in mn_host:
            mn_host.append(mn.hostName)

    hosts = res_ops.query_resource(res_ops.HOST)
    for host in hosts:
        if host.managementIp in mn_host:
            if host.uuid not in host_list:
                host_list.append(host.uuid)
        else:
            sce_host = get_sce_host_by_ip(host.managementIp)
            if sce_host != None:
                for sce_ip in xmlobject.safe_list(sce_host.ips.ip):
                    if sce_ip.ip_ in mn_host:
                        host_list.append(host.uuid)
   
    return host_list

def get_host_has_nfs():
    cond = res_ops.gen_query_conditions('type', '=', 'NFS')
    primarystorages = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    host_list = []
    nfs_list = []
    for primarystorage in primarystorages:
        nfs_ps_url = primarystorage.url
        nfs_host_ip, nfs_path = nfs_ps_url.split(':', 1)
        if nfs_host_ip not in nfs_list:
            nfs_list.append(nfs_host_ip)

    hosts = res_ops.query_resource(res_ops.HOST)
    for host in hosts:
        if host.managementIp in nfs_list:
            if host.uuid not in host_list:
                host_list.append(host.uuid)
        else:
            sce_host = get_sce_host_by_ip(host.managementIp)
            if sce_host != None:
                for sce_ip in xmlobject.safe_list(sce_host.ips.ip):
                    if sce_ip.ip_ in nfs_list:
                        host_list.append(host.uuid)

    return host_list

def ensure_vm_not_on(vm_uuid, host_uuid, host_list):
    if host_uuid not in host_list:
        return True
    cond1 = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond1 = res_ops.gen_query_conditions('status', '=', 'Connected', cond1)
    candidate_hosts = res_ops.query_resource(res_ops.HOST, cond1)
    for candidate_host in candidate_hosts:
        if candidate_host.uuid not in host_list:
            vm_ops.migrate_vm(vm_uuid, candidate_host.uuid)
            return True
    return False
          

def ensure_host_has_no_vr(host_uuid):
    cond = res_ops.gen_query_conditions('type', '=', 'ApplianceVm')
    cond1 = res_ops.gen_query_conditions('hostUuid', '=', host_uuid, cond)
    vr_list = res_ops.query_resource(res_ops.VM_INSTANCE, cond1)
    if not vr_list:
        test_util.test_logger("host originally has no vr need to migrate.")
        return

    cond2 = res_ops.gen_query_conditions('uuid', '!=', host_uuid)
    cadidate_host_uuid = res_ops.query_resource(res_ops.HOST, cond2)[0].uuid

    for vr in vr_list:
        vm_ops.migrate_vm(vr.uuid, cadidate_host_uuid)


def ensure_all_vrs_on_host(host_uuid):
    cond = res_ops.gen_query_conditions('type', '=', 'ApplianceVm')
    vr_list = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
    if not vr_list:
        test_util.test_logger("no vr in current env.")
        return

    for vr in vr_list:
        vm_ops.migrate_vm(vr.uuid, host_uuid)

    #This is for ensure the migration completed
    time.sleep(60)


def ensure_host_not_nfs_provider(host_uuid):
    cond = res_ops.gen_query_conditions('type', '=', 'NFS')
    primarystorage = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    for nfs_ps in primarystorage:
        nfs_ps_url = nfs_ps.url
        nfs_host_ip, nfs_path = nfs_ps_url.split(':', 1)

    nfs_host_uuid = test_lib.lib_get_host_by_ip(nfs_host_ip)
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    cond1 = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond1 = res_ops.gen_query_conditions('status', '=', 'Connected', cond1)
    cond1 = res_ops.gen_query_conditions('managementIp', '!=', mn_ip, cond1)
    cond1 = res_ops.gen_query_conditions('managementIp', '!=', nfs_host_ip, cond1)
    candidate_host_uuid = res_ops.query_resource(res_ops.HOST, cond1)[0].uuid
    if host_uuid == nfs_host_uuid:
        vm_ops.migrate_vm(vm.uuid, candidate_host_uuid)


def async_exec_ifconfig_nic_down_up(sleep_time, ip, host_username, host_password, nic):
    def _wrapper(sleep_time, ip, host_username, host_password, nic):
        cmd = "ifconfig %s down; sleep %s; ifconfig %s up" %(nic, sleep_time, nic)
        test_lib.lib_execute_ssh_cmd(ip, host_username, host_password, cmd,  timeout=sleep_time+20)

    t = threading.Thread(target=_wrapper, args=(sleep_time, ip, host_username, host_password, nic))
    t.start()

    return t


def skip_if_not_storage_network_separate(scenarioConfig):
    is_storage_network_separated = False
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            for l3Network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if xmlobject.has_element(l3Network, 'primaryStorageRef'):
                    is_storage_network_separated = True
                    break
    if not is_storage_network_separated:
        test_util.test_skip("not found separate network in scenario config.")


def get_host_l2_nic_name(l2interface):
    if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
        l2_network_interface = l2interface.replace("eth", "zsn")
        return l2_network_interface
    else:
        return l2interface
        #return "br_eth0"


@contextmanager
def expected_failure(msg, *exceptions):
    try:
        yield
    except exceptions:
        test_util.test_logger("Expected failure: {}".format(msg))
    else:
        test_util.test_fail("CRITICAL ERROR: {} succeed!".format(msg))


class PSEnvChecker(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
        assert self.ps_list

    @property
    def is_one_ps_env(self):
        return len(self.ps_list) == 1

    @property
    def is_one_local_env(self):
        return self.is_one_ps_env and self.ps_list[0].type == inventory.LOCAL_STORAGE_TYPE

    @property
    def is_one_nfs_env(self):
        return self.is_one_ps_env and self.ps_list[0].type == inventory.NFS_PRIMARY_STORAGE_TYPE

    @property
    def is_one_ceph_env(self):
        return self.is_one_ps_env and self.ps_list[0].type == inventory.CEPH_PRIMARY_STORAGE_TYPE

    @property
    def is_one_smp_env(self):
        return self.is_one_ps_env and self.ps_list[0].type == "SharedMountPoint"
    
    @property
    def is_one_sb_env(self):
        return self.is_one_ps_env and self.ps_list[0].type == "SharedBlock"

    @property
    def is_multi_ps_env(self):
        return len(self.ps_list) >= 2

    @property
    def is_multi_local_env(self):
        if not self.is_multi_ps_env:
            return False
        for ps in self.ps_list:
            if ps.type != inventory.LOCAL_STORAGE_TYPE:
                return False
        return True

    @property
    def is_multi_nfs_env(self):
        if not self.is_multi_ps_env:
            return False
        for ps in self.ps_list:
            if ps.type != inventory.NFS_PRIMARY_STORAGE_TYPE:
                return False
        return True

    @property
    def is_multi_ceph_env(self):
        if not self.is_multi_ps_env:
            return False
        for ps in self.ps_list:
            if ps.type != inventory.CEPH_PRIMARY_STORAGE_TYPE:
                return False
        return True

    @property
    def is_multi_smp_env(self):
        if not self.is_multi_ps_env:
            return False
        for ps in self.ps_list:
            if ps.type != "SharedMountPoint":
                return False
        return True

    @property
    def is_multi_sb_env(self):
        if not self.is_multi_ps_env:
            return False
        for ps in self.ps_list:
            if ps.type != "SharedBlock":
                return False
        return True

    @property
    def is_local_nfs_env(self):
        return self.have_local and self.have_nfs

    @property
    def is_sb_ceph_env(self):
        return self.have_sb and self.have_ceph

    @property
    def is_local_smp_env(self):
        return self.have_local and self.have_smp

    def is_local_shared_env(self):
        return self.is_local_nfs_env or self.is_local_smp_env

    @property
    def have_local(self):
        for ps in self.ps_list:
            if ps.type == inventory.LOCAL_STORAGE_TYPE:
                return True
        return False

    @property
    def have_smp(self):
        for ps in self.ps_list:
            if ps.type == "SharedMountPoint":
                return True
        return False

    @property
    def have_sb(self):
        for ps in self.ps_list:
            if ps.type == "SharedBlock":
                return True
        return False

    @property
    def have_nfs(self):
        for ps in self.ps_list:
            if ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE:
                return True
        return False

    @property
    def have_ceph(self):
        for ps in self.ps_list:
            if ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:
                return True
        return False

    def get_random_ps(self):
        return random.choice(self.ps_list)

    def get_random_local(self):
        if not self.have_local:
            raise EnvironmentError
        return random.choice([ps for ps in self.ps_list if ps.type == inventory.LOCAL_STORAGE_TYPE])

    def get_random_nfs(self):
        if not self.have_nfs:
            raise EnvironmentError
        return random.choice([ps for ps in self.ps_list if ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE])

    def get_random_ceph(self):
        if not self.have_ceph:
            raise EnvironmentError
        return random.choice([ps for ps in self.ps_list if ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE])

    def get_random_smp(self):
        if not self.have_smp:
            raise EnvironmentError
        return random.choice([ps for ps in self.ps_list if ps.type == "SharedMountPoint"])

    def get_random_sb(self):
        if not self.have_sb:
            raise EnvironmentError
        return random.choice([ps for ps in self.ps_list if ps.type == "SharedBlock"])

    def get_two_ps(self):
        if not self.is_multi_ps_env:
            raise EnvironmentError
        if self.is_local_nfs_env:
            return self.get_random_local(), self.get_random_nfs()
        elif self.is_local_smp_env:
            return self.get_random_local(), self.get_random_smp()
        elif self.is_sb_ceph_env:
            return self.get_random_sb(), self.get_random_ceph()
        else:
            return random.sample(self.ps_list, 2)


def skip_if_only_one_ps(test_method):
    @wraps(test_method)
    def wrapper():
        if PSEnvChecker().is_one_ps_env:
            test_util.test_skip("Skip test if only one PrimaryStorage")
        return test_method()
    return wrapper


def skip_if_multi_ps(test_method):
    @wraps(test_method)
    def wrapper():
        if PSEnvChecker().is_multi_ps_env:
            test_util.test_skip("Skip test if multi PrimaryStorage Env")
        return test_method()
    return wrapper

def skip_if_not_have_local(test_method):
    @wraps(test_method)
    def wrapper():
        if not PSEnvChecker().have_local:
            test_util.test_skip("Skip test if not have local PrimaryStorage")
        return test_method()
    return wrapper

def skip_if_not_local_nfs(test_method):
    @wraps(test_method)
    def wrapper():
        if not PSEnvChecker().is_local_nfs_env:
            test_util.test_skip("Skip test if not local nfs PrimaryStorage Env")
        return test_method()
    return wrapper


def skip_if_local_nfs(test_method):
    @wraps(test_method)
    def wrapper():
        if PSEnvChecker().is_local_nfs_env:
            test_util.test_skip("Skip test if not local nfs PrimaryStorage Env")
        return test_method()
    return wrapper


def skip_if_multi_nfs(test_method):
    @wraps(test_method)
    def wrapper():
        if PSEnvChecker().is_multi_nfs_env:
            test_util.test_skip("Skip test if multi nfs PrimaryStorage Env")
        return test_method()
    return wrapper


def skip_if_have_local(test_method):
    @wraps(test_method)
    def wrapper():
        if PSEnvChecker().have_local:
            test_util.test_skip("Skip test if have local PrimaryStorage")
        return test_method()
    return wrapper


def skip_if_have_nfs(test_method):
    @wraps(test_method)
    def wrapper():
        if PSEnvChecker().have_nfs:
            test_util.test_skip("Skip test if have nfs PrimaryStorage")
        return test_method()
    return wrapper


def skip_if_local_shared(test_method):
    @wraps(test_method)
    def wrapper():
        if PSEnvChecker().is_local_smp_env or PSEnvChecker().is_local_nfs_env:
            test_util.test_skip("Skip test if ocal-shared environment")
        return test_method()
    return wrapper


def skip_if_not_local_shared(test_method):
    @wraps(test_method)
    def wrapper():
        if PSEnvChecker().is_local_smp_env == False and PSEnvChecker().is_local_nfs_env == False:
            test_util.test_skip("Skip test if not local-shared environment")
        return test_method()
    return wrapper


def wait_until_vm_reach_state(timeout, state, *vm_list):
    total_time = 0
    interval = 5
    while total_time <= timeout:
        [vm.update() for vm in vm_list]
        state_list = [vm.get_vm().state for vm in vm_list]
        if state in state_list and len(set(state_list)) == 1:
            test_util.test_logger('All VMs reach {} status!'.format(state))
            break
        else:
            time.sleep(interval)
            total_time += interval
    else:
        test_util.test_fail('Some VM Fail to Reach {} state in {}s'.format(timeout))


def create_eip(eip_name=None, vip_uuid=None, vnic_uuid=None, vm_obj=None, \
        session_uuid = None):
    if not vip_uuid:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        vip_uuid = net_ops.acquire_vip(l3_uuid).uuid

    eip_option = test_util.EipOption()
    eip_option.set_name(eip_name)
    eip_option.set_vip_uuid(vip_uuid)
    eip_option.set_vm_nic_uuid(vnic_uuid)
    eip_option.set_session_uuid(session_uuid)
    eip = zstack_eip_header.ZstackTestEip()
    eip.set_creation_option(eip_option)
    if vnic_uuid and not vm_obj:
        test_util.test_fail('vm_obj can not be None in create_eip() API, when setting vm_nic_uuid.')
    eip.create(vm_obj)
    return eip

def create_vip(vip_name=None, l3_uuid=None, session_uuid = None):
    if not vip_name:
        vip_name = 'test vip'
    if not l3_uuid:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    vip_creation_option = test_util.VipOption()
    vip_creation_option.set_name(vip_name)
    vip_creation_option.set_l3_uuid(l3_uuid)
    vip_creation_option.set_session_uuid(session_uuid)

    vip = zstack_vip_header.ZstackTestVip()
    vip.set_creation_option(vip_creation_option)
    vip.create()

    return vip

def get_another_ip_of_host(ip, username, password):
    '''
        This function is only suitable for 2 network cards in the host.
    '''
    cmd = "ip r|grep kernel|grep -v %s|awk '{print $NF}' | sort -n | uniq" %(ip)
    output = test_lib.lib_execute_ssh_cmd(ip, username, password, cmd, timeout=30)
    return output.split(':')[-1].strip()


def generate_pub_test_vm(tbj):
    if res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].type == inventory.LOCAL_STORAGE_TYPE:
        disk_offering_uuids = None
    else:
        disk_offering_uuids = [random.choice(res_ops.get_resource(res_ops.DISK_OFFERING)).uuid]
    l3_name_list = ['l3PublicNetworkName', 'l3NoVlanNetworkName1', 'l3NoVlanNetworkName2']

    pub_l3_vm, vm1, vm2 = [create_vm_with_random_offering(vm_name='test_vm',
                                                          image_name='imageName3',
                                                          disk_offering_uuids=random.choice([None, disk_offering_uuids]),
                                                          l3_name=name) for name in l3_name_list]
    #import time
    #time.sleep(120)
    #for vm in (pub_l3_vm, vm1, vm2):
    #    if 'DHCP' not in [service.networkServiceType for service
    #                      in test_lib.lib_get_l3_by_uuid(vm.get_vm().vmNics[0].l3NetworkUuid).networkServices]:
    #        set_static_ip(vm.get_vm())

    for vm in (pub_l3_vm, vm1, vm2):
        vm.check()
        tbj.add_vm(vm)

    return pub_l3_vm, vm1, vm2


def set_static_ip(vm):
    vmnic = vm.vmNics[0]
    cmd1 = '''echo -e "BOOTPROTO=static\nONBOOT=yes\nIPADDR={}\nGATEWAY={}\nNETMASK={}\n" > /etc/sysconfig/network-scripts/ifcfg-eth0 '''\
        .format(vmnic.ip, vmnic.gateway,vmnic.netmask)
    cmd2 = "service network restart"
    return run_cmd_in_vm_console(vm, (cmd1, cmd2))


def run_cmd_in_vm_console(vm, cmd_list):
    ssh_cmd = "sshpass -p %s ssh -t -t -t %s" % ("password", test_lib.lib_get_host_by_uuid(vm.hostUuid).managementIp)

    try:
        import pexpect
        result = pexpect.spawn('{} virsh console {}'.format(ssh_cmd, vm.uuid))
        result.expect('Escape character is', timeout=10)
        result.send('\n')
        result.expect('login:')
        result.sendline('root')
        result.expect('Password:')
        result.sendline('password')
        result.expect('#')
        for cmd in cmd_list:
            result.sendline(cmd)
            result.expect('#')
    except Exception as e:
        test_util.test_fail('Fail to run cmds in vm: {}'.format(e))
    finally:
        result.close()


def generate_local_shared_test_vms(tbj, vm_ha=False, host_uuid=None):
    local_ps, shared_ps = PSEnvChecker().get_two_ps()
    disk_offering_uuids = [random.choice(res_ops.get_resource(res_ops.DISK_OFFERING)).uuid]
    SHARED='SHARED'
    LOCAL='LOCAL'
    MIXED='MIXED'

    for root_vol, data_vol in itertools.product((LOCAL,SHARED),(None,LOCAL,SHARED,MIXED)):
        vm = create_vm_with_random_offering(vm_name='test_vm',
                                            disk_offering_uuids=disk_offering_uuids if data_vol else None,
                                            ps_uuid=local_ps.uuid if root_vol is LOCAL else shared_ps.uuid,
                                            l3_name='l3VlanNetworkName1',
                                            host_uuid=host_uuid,
                                            image_name='imageName_net',
                                            system_tags=['primaryStorageUuidForDataVolume::{}'.format(local_ps.uuid if data_vol in (LOCAL, MIXED)
                                                                                                            else shared_ps.uuid)] if data_vol else None)

        tbj.add_vm(vm)
        if data_vol is MIXED:
            test_util.test_dsc("Create volume from shared_ps and attached to VM")
            volume = create_multi_volumes(count=1, ps=shared_ps)[0]
            tbj.add_volume(volume)
            volume.attach(vm)

        if vm_ha:
            ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")

        yield vm


def stop_ha_vm(vm_uuid, force=None, session_uuid=None):
    import apibinding.api_actions as api_actions
    action = api_actions.StopVmInstanceAction()
    action.uuid = vm_uuid
    action.type = force
    action.stopHA = "true"
    action.timeout = 240000
    test_util.action_logger('Stop VM [uuid:] %s' % vm_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory


def check_if_vm_starting_incorrectly_on_original_host(vm_uuid, host_uuid, max_count=180):
    '''
    This function is designed for Nfs/Ceph/SMP/FusionStor and etc kinds of shared primary storage.
    Therefore, it should not be invoked when the env is local storage.

    The following failed cases should be captured:
        1. vm is starting && vm.hostUuid == original hostUuid
        2. vm is running && vm.hostUuid == original hostUuid

    The function should be exist in advance when checking the following case:
        1. vm is running && vm.hostUuid != original hostUuid
    '''
    cond = res_ops.gen_query_conditions('uuid', '=', vm_uuid)
    vm_stop_time = max_count
    for i in range(0, max_count):
        vm_stop_time = i
        vm_inv = res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0]
        if vm_inv.state == "Starting" and vm_inv.hostUuid == host_uuid:
            test_util.test_fail('Find vm is starting incorrectly on original disconnected host %s' %(host_uuid))
        elif vm_inv.state == "Running" and vm_inv.hostUuid == host_uuid:
            test_util.test_fail('Find vm is running incorrectly on original disconnected host %s' %(host_uuid))
        elif vm_inv.state == "Running" and vm_inv.hostUuid != host_uuid:
            test_util.test_logger('Find vm is running correctly on another host %s' %(host_uuid))
            break
        time.sleep(1)
    else:
        test_util.test_logger("Checked %s rounds, not find vm is Starting and host is original" %(max_count))


VM_OPS_TEST = [
"VM_TEST_NONE", 
"VM_TEST_MIGRATE",
"VM_TEST_SNAPSHOT",
"VM_TEST_STATE",
"VM_TEST_REIMAGE",
"VM_TEST_ATTACH",
"VM_TEST_RESIZE_DVOL",
"VM_TEST_RESIZE_RVOL",
"VM_TEST_CHANGE_OS",
"VM_TEST_ALL"
]


def vm_ops_test(vm_obj, vm_ops_test_choice="VM_TEST_NONE"):
    '''
    This function provides vm operation related test
    '''
    import zstackwoodpecker.zstack_test.zstack_test_image as test_image
    import zstackwoodpecker.operations.volume_operations as vol_ops
    import zstackwoodpecker.operations.vm_operations as vm_ops
    import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
    import zstackwoodpecker.header.vm as vm_header

    #import zstacklib.utils.ssh as ssh
    import test_stub
    test_obj_dict = test_state.TestStateDict()

    if vm_ops_test_choice not in VM_OPS_TEST: 
        test_util.test_fail( "Find not support vm operation" )

    if vm_ops_test_choice == "VM_TEST_NONE":
        test_util.test_logger( "VM_OPS_TEST.VM_TEST_NONE, therefore, skip vm_ops function" )
        return

    if vm_ops_test_choice == "VM_TEST_ALL" or vm_ops_test_choice == "VM_TEST_MIGRATE":
        test_util.test_dsc("@@@_FUNC_:vm_ops_test   @@@_IF_BRANCH_:VM_TEST_ALL|VM_TEST_MIGRATE")
        ps = test_lib.lib_get_primary_storage_by_vm(vm_obj.get_vm())
        if ps.type in [ inventory.CEPH_PRIMARY_STORAGE_TYPE, 'SharedMountPoint', inventory.NFS_PRIMARY_STORAGE_TYPE, 'SharedBlock', 'AliyunNAS']:
            target_host = test_lib.lib_find_random_host(vm_obj.vm)
            vm_obj.migrate(target_host.uuid)
        elif ps.type in [ inventory.LOCAL_STORAGE_TYPE ]:
            vm_obj.stop()
            vm_obj.check()
            target_host = test_lib.lib_find_random_host(vm_obj.vm)
            vol_ops.migrate_volume(vm_obj.get_vm().allVolumes[0].uuid, target_host.uuid)
            vm_obj.start()
            test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)
            #vm_obj.check()
        else:
            test_util.test_fail("FOUND NEW STORAGTE TYPE. FAILED")


    if vm_ops_test_choice == "VM_TEST_ALL" or vm_ops_test_choice == "VM_TEST_SNAPSHOT":
        test_util.test_dsc("@@@_FUNC_:vm_ops_test   @@@_IF_BRANCH_:VM_TEST_ALL|VM_TEST_SNAPSHOT")
        #vm_root_volume_inv = test_lib.lib_get_root_volume(vm_obj.get_vm())
        #snapshots_root = test_obj_dict.get_volume_snapshot(vm_root_volume_inv.uuid)
        vol_obj = zstack_volume_header.ZstackTestVolume()
        vol_obj.set_volume(test_lib.lib_get_root_volume(vm_obj.get_vm()))
        snapshots_root = zstack_sp_header.ZstackVolumeSnapshot()
        snapshots_root.set_utility_vm(vm_obj)
        snapshots_root.set_target_volume(vol_obj)
        snapshots_root.create_snapshot('create_data_snapshot1')
        snapshots_root.check()
        sp1 = snapshots_root.get_current_snapshot()
        #comment this data check for avoiding execute a cmd in vm in flat network mode.
        #the code below is worked in vr mode.
        #TODO: fix for work in flat network mode.
        #cmd = "touch /opt/check_snapshot"
        #if not test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, '22', 90):
        #    test_util.test_fail('VM is expected to running before execute cmd %s' %(cmd))
        #if not test_lib.lib_execute_command_in_vm(vm_obj.get_vm(), cmd):
        #    test_util.test_fail("execute cmd %s in vm failed" %(cmd))
        vm_obj.stop()
        vm_obj.check()
        snapshots_root.use_snapshot(sp1)
        vm_obj.start()
        test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)
        #vm_obj.check()
        #cmd = "! test -f /opt/check_snapshot"
        #if not test_lib.lib_execute_command_in_vm(vm_obj.get_vm(), cmd):
        #    test_util.test_fail("execute cmd %s in vm failed" %(cmd))


    if vm_ops_test_choice == "VM_TEST_ALL" or vm_ops_test_choice == "VM_TEST_STATE":
        test_util.test_dsc("@@@_FUNC_:vm_ops_test   @@@_IF_BRANCH_:VM_TEST_ALL|VM_TEST_STATE")
        vm_ops.stop_vm(vm_obj.vm.uuid, 'cold')
        vm_obj.set_state(vm_header.STOPPED)
        vm_obj.check()
        vm_obj.start()
        test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)
        #vm_obj.check()
        vm_obj.stop()
        vm_obj.check()
        vm_obj.start()
        test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)
        #vm_obj.check()
        vm_obj.suspend()
        vm_obj.check()
        vm_obj.resume()
        #vm_obj.check()
        test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)


    if vm_ops_test_choice == "VM_TEST_ALL" or vm_ops_test_choice == "VM_TEST_REIMAGE":
        test_util.test_dsc("@@@_FUNC_:vm_ops_test   @@@_IF_BRANCH_:VM_TEST_ALL|VM_TEST_REIMAGE")
        cond = res_ops.gen_query_conditions("uuid", '=', vm_obj.vm.imageUuid)
        img_inv = res_ops.query_resource(res_ops.IMAGE, cond)[0]
        if img_inv.format == "iso" or img_inv.mediaType == "ISO":
            test_util.test_dsc("skip reimage if image type is iso")
        else:
            #comment this data check for avoiding execute a cmd in vm in flat network mode.
            #the code below is worked in vr mode.
            #TODO: fix for work in flat network mode.
            #cmd = "touch /opt/beforeReimage"
            #if not test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, '22', 90):
            #    test_util.test_fail('VM is expected to running before execute cmd %s' %(cmd))
            #if not test_lib.lib_execute_command_in_vm(vm_obj.get_vm(), cmd):
            #    test_util.test_fail("execute cmd %s in vm failed" %(cmd))
            vm_obj.stop()
            vm_obj.reinit()
            vm_obj.update()
            vm_obj.check()
            vm_obj.start()
            #vm_obj.check()
            test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)
            #cmd = "! test -f /opt/beforeReimage"
            #if not test_lib.lib_execute_command_in_vm(vm_obj.get_vm(), cmd):
            #    test_util.test_fail("execute cmd %s in vm failed" %(cmd))


    if vm_ops_test_choice == "VM_TEST_ALL" or vm_ops_test_choice == "VM_TEST_ATTACH":

        test_util.test_dsc("@@@_FUNC_:vm_ops_test   @@@_IF_BRANCH_:VM_TEST_ALL|VM_TEST_ATTACH")

        test_util.test_dsc("@@@==>ATTACH ISO")
        cond = res_ops.gen_query_conditions("status", '=', "Connected")
        bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid
        img_option = test_util.ImageOption()
        img_option.set_name('iso')
        img_option.set_backup_storage_uuid_list([bs_uuid])
        mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
        if os.system("sshpass -p password ssh %s 'ls  %s/apache-tomcat/webapps/zstack/static/zstack-repo/'" % (mn_ip, os.environ.get('zstackInstallPath'))) == 0:
            os.system("sshpass -p password ssh %s 'echo fake iso for test only >  %s/apache-tomcat/webapps/zstack/static/zstack-repo/7/x86_64/os/test.iso'" % (mn_ip, os.environ.get('zstackInstallPath')))
            img_option.set_url('http://%s:8080/zstack/static/zstack-repo/7/x86_64/os/test.iso' % (mn_ip))
        else:
            os.system("sshpass -p password ssh %s 'echo fake iso for test only >  %s/apache-tomcat/webapps/zstack/static/test.iso'" % (mn_ip, os.environ.get('zstackInstallPath')))
            img_option.set_url('http://%s:8080/zstack/static/test.iso' % (mn_ip))
        image_inv = img_ops.add_iso_template(img_option)
        image = test_image.ZstackTestImage()
        image.set_image(image_inv)
        image.set_creation_option(img_option)

        cond = res_ops.gen_query_conditions('name', '=', 'iso')
        iso_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
        img_ops.attach_iso(iso_uuid, vm_obj.vm.uuid)
        #vm_obj.check()
        test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)
        img_ops.detach_iso(vm_obj.vm.uuid, iso_uuid)
        test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)
        #vm_obj.check()

        test_util.test_dsc("@@@==>ATTACH VOLUME")
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_name('volume1')
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume = test_stub.create_volume(volume_creation_option)
        test_obj_dict.add_volume(volume)
        volume.check()
        volume.attach(vm_obj)
        volume.detach(vm_obj.get_vm().uuid)

        ps = test_lib.lib_get_primary_storage_by_vm(vm_obj.get_vm())
        if ps.type in [ inventory.CEPH_PRIMARY_STORAGE_TYPE, 'SharedBlock' ]:
            test_util.test_dsc("@@@==>ATTACH SHAREABLE VOLUME")
            disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
            volume_creation_option = test_util.VolumeOption()
            volume_creation_option.set_name('shareable_volume1')
            volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
            volume_creation_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi'])
            volume = test_stub.create_volume(volume_creation_option)
            test_obj_dict.add_volume(volume)
            volume.check()
            volume.attach(vm_obj)
            volume.detach(vm_obj.get_vm().uuid)
            test_lib.lib_error_cleanup(test_obj_dict)

        test_util.test_dsc("@@@==>ATTACH NIC(TODO:)")


    if vm_ops_test_choice == "VM_TEST_ALL" or vm_ops_test_choice == "VM_TEST_RESIZE_RVOL":
        test_util.test_dsc("@@@_FUNC_:vm_ops_test   @@@_IF_BRANCH_:VM_TEST_ALL|VM_TEST_RESIZE_RVOL")
        vol_size = test_lib.lib_get_root_volume(vm_obj.get_vm()).size
        volume_uuid = test_lib.lib_get_root_volume(vm_obj.get_vm()).uuid
        set_size = 1024*1024*1024*45
        vm_obj.stop()
        vm_obj.check()
        vol_ops.resize_volume(volume_uuid, set_size)
        vm_obj.update()
        vol_size_after = test_lib.lib_get_root_volume(vm_obj.get_vm()).size
        if set_size != vol_size_after:
            test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)
        vm_obj.start()
        #vm_obj.check()
        test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)


    if vm_ops_test_choice == "VM_TEST_ALL" or vm_ops_test_choice == "VM_TEST_RESIZE_DVOL":
        test_util.test_dsc("@@@_FUNC_:vm_ops_test   @@@_IF_BRANCH_:VM_TEST_ALL|VM_TEST_RESIZE_DVOL")
        volume_creation_option = test_util.VolumeOption()
        test_util.test_dsc('Create volume and check')
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume = test_stub.create_volume(volume_creation_option)
        test_obj_dict.add_volume(volume)
        volume.check()
        volume_uuid = volume.volume.uuid
        vol_size = volume.volume.size
        volume.attach(vm_obj)
        vm_obj.stop()
        vm_obj.check()

        set_size = 1024*1024*1024*13
        vol_ops.resize_data_volume(volume_uuid, set_size)
        vm_obj.update()
        vol_size_after = test_lib.lib_get_data_volumes(vm_obj.get_vm())[0].size
        if set_size != vol_size_after:
            test_util.test_fail('Resize Data Volume failed, size = %s' % vol_size_after)
        test_lib.lib_error_cleanup(test_obj_dict)


    if vm_ops_test_choice == "VM_TEST_ALL" or vm_ops_test_choice == "VM_TEST_CHANGE_OS":
        test_util.test_dsc("@@@_FUNC_:vm_ops_test   @@@_IF_BRANCH_:VM_TEST_ALL|VM_TEST_CHANGE_OS")
        vm_uuid = vm_obj.get_vm().uuid
        last_l3network_uuid = test_lib.lib_get_l3s_uuid_by_vm(vm_obj.get_vm())
        last_ps_uuid = test_lib.lib_get_root_volume(vm_obj.get_vm()).primaryStorageUuid
        vm_ops.stop_vm(vm_uuid)
        image_uuid = test_lib.lib_get_image_by_name("ttylinux").uuid
        vm_ops.change_vm_image(vm_uuid,image_uuid)
        vm_ops.start_vm(vm_uuid)
        vm_obj.update()
        #check whether the vm is running successfully
        test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip,22, 300)
        #check whether the network config has changed
        l3network_uuid_after = test_lib.lib_get_l3s_uuid_by_vm(vm_obj.get_vm())
        if l3network_uuid_after != last_l3network_uuid:
           test_util.test_fail('Change VM Image Failed.The Network config has changed.')
        #check whether primarystorage has changed
        ps_uuid_after = test_lib.lib_get_root_volume(vm_obj.get_vm()).primaryStorageUuid
        if ps_uuid_after != last_ps_uuid:
           test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')



DVOL_OPS_TEST = [
"DVOL_TEST_NONE",
"DVOL_TEST_MIGRATE",
"DVOL_TEST_SNAPSHOT",
"DVOL_TEST_STATE",
"DVOL_TEST_ATTACH",
"DVOL_TEST_RESIZE",
"DVOL_TEST_ALL"
]

def dvol_ops_test(dvol_obj,vm_obj, dvol_ops_test_choice="DVOL_TEST_NONE"):
    '''
    This function provides dvol operation related test
    '''


    import zstackwoodpecker.operations.volume_operations as vol_ops


    #import zstacklib.utils.ssh as ssh
    import test_stub
    test_obj_dict = test_state.TestStateDict()


    if dvol_ops_test_choice not in DVOL_OPS_TEST:
        test_util.test_fail( "Find not support dvol operation" )


    if dvol_ops_test_choice == "DVOL_TEST_NONE":
        test_util.test_logger( "DVOL_OPS_TEST.DVOL_TEST_NONE, therefore, skip DVOL_ops function" )
        return


    if dvol_ops_test_choice == "DVOL_TEST_ALL" or dvol_ops_test_choice == "DVOL_TEST_MIGRATE":
        test_util.test_dsc("@@@_FUNC_:dvol_ops_test   @@@_IF_BRANCH_:DVOL_TEST_ALL|DVOL_TEST_MIGRATE")
        ps = test_lib.lib_get_primary_storage_by_vm(vm_obj.get_vm())
        if ps.type in [inventory.LOCAL_STORAGE_TYPE]:
            target_host = test_lib.lib_find_random_host(vm_obj.vm)
            vol_ops.migrate_volume(dvol_obj.uuid, target_host.uuid)
            target_host2 = test_lib.lib_find_host_by_vm(vm_obj.get_vm())
            vol_ops.migrate_volume(dvol_obj.uuid, target_host2.uuid)
        elif ps.type in [inventory.CEPH_PRIMARY_STORAGE_TYPE, 'SharedMountPoint', inventory.NFS_PRIMARY_STORAGE_TYPE, 'SharedBlock', 'AliyunNAS']:
            test_util.test_dsc("skip migrate if ps type is not local")
        else:
            test_util.test_fail("FOUND NEW STORAGTE TYPE. FAILED")


    if dvol_ops_test_choice == "DVOL_TEST_ALL" or dvol_ops_test_choice == "DVOL_TEST_SNAPSHOT":
        test_util.test_dsc("@@@_FUNC_:dvol_ops_test   @@@_IF_BRANCH_:DVOL_TEST_ALL|DVOL_TEST_SNAPSHOT")
        snapshot_option = test_util.SnapshotOption()
        snapshot_option.set_volume_uuid(dvol_obj.uuid)
        snapshot_option.set_name('snapshot-1')
        snapshot_option.set_description('Test')
        vol_snapshot = vol_ops.create_snapshot(snapshot_option)
        vol_ops.use_snapshot(vol_snapshot.uuid)


    if dvol_ops_test_choice == "DVOL_TEST_ALL" or dvol_ops_test_choice == "DVOL_TEST_STATE":
        test_util.test_dsc("@@@_FUNC_:dvol_ops_test   @@@_IF_BRANCH_:DVOL_TEST_ALL|DVOL_TEST_STATE")
        vol_ops.stop_volume(dvol_obj.uuid)
        vol_ops.start_volume(dvol_obj.uuid)


    if dvol_ops_test_choice == "DVOL_TEST_ALL" or dvol_ops_test_choice == "DVOL_TEST_ATTACH":
        test_util.test_dsc("@@@_FUNC_:dvol_ops_test   @@@_IF_BRANCH_:DVOL_TEST_ALL|DVOL_TEST_ATTACH")
        vol_ops.attach_volume(dvol_obj.uuid, vm_obj.get_vm().uuid)
        vm_obj.update()
        vol_ops.detach_volume(dvol_obj.uuid, vm_obj.get_vm().uuid)
        vm_obj.update()


    if dvol_ops_test_choice == "DVOL_TEST_ALL" or dvol_ops_test_choice == "DVOL_TEST_RESIZE":
        test_util.test_dsc("@@@_FUNC_:dvol_ops_test   @@@_IF_BRANCH_:DVOL_TEST_ALL|DVOL_TEST_RESIZE")
        vol_size_before = dvol_obj.size
        if vol_size_before < 1024*1024*1024*1:
            vol_size_before = 1024*1024*1024*1
        set_size = 1024*1024*1024*1 + vol_size_before
        vol_ops.resize_data_volume(dvol_obj.uuid, set_size)
        dvol_obj.size = set_size
def create_image_store_backup_storage(bs_name, bs_hostname, bs_username, bs_password, bs_url, bs_sshport, session_uuid=None):
    action = api_actions.AddImageStoreBackupStorageAction()
    action.name = bs_name
    action.url = bs_url
    action.hostname = bs_hostname
    action.username = bs_username
    action.password = bs_password
    action.sshPort = bs_sshport
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Sftp Backup Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def wait_until_vm_reachable(vm, timeout=120):
    vm_ip = vm.get_vm().vmNics[0].ip
    ping_cmd = "ping %s -c 1 | grep 'ttl='" % vm_ip
    for _ in xrange(timeout):
        if shell.call(ping_cmd, exception=False):
            break
        else:
            time.sleep(interval)


class MultiSharedPS(object):
    def __init__(self):
        self.vm = []
        self.image = None
        self.data_volume = {}
        self.ceph = None
        self.san = []
        self.bs = []
        self.ps = []
#         self.l3_name =  os.getenv('l3PublicNetworkName')
        self.l3_name = os.getenv('l3VlanNetworkName1')
        self.image_name_net = os.getenv('imageName_net')
        self.sp_tree = {}
        self.ps_type_dict = None
        self.ps_types = []
        self.snapshot = {}
        self.test_obj_dict = test_state.TestStateDict()
        self.vol_uuid = None
        self.snapshots = None
        self.sp_tree = test_util.SPTREE()

    def create_vm(self, vm_name=None, image_name=None, l3_name=None, ceph_image=False, with_data_vol=False, one_volume=False,
                  reverse=False, set_ps_uuid=True, ps_type=None, except_ps_type=None, iso_image=False):
        vm_name = vm_name if vm_name else 'multi_shared_ps_test_vm'
        image_name = image_name if image_name else self.image_name_net
        l3_name = l3_name if l3_name else self.l3_name
        vm_creation_option = test_util.VmOption()
        if iso_image:
            img_option = test_util.ImageOption()
            img_option.set_name('fake_iso')
            imagestore = res_ops.query_resource(res_ops.IMAGE_STORE_BACKUP_STORAGE)[0]
            img_option.set_backup_storage_uuid_list([imagestore.uuid])
            mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
            if os.system("sshpass -p password ssh %s 'ls  %s/apache-tomcat/webapps/zstack/static/zstack-repo/'" % (mn_ip, os.environ.get('zstackInstallPath'))) == 0:
                img_option.set_url('http://%s:8080/zstack/static/zstack-repo/7/x86_64/os/ks.cfg' % (mn_ip))
            else:
                img_option.set_url('http://%s:8080/zstack/static/zstack-dvd/ks.cfg' % (mn_ip))
            image_uuid = img_ops.add_iso_template(img_option).uuid
        else:
            if ceph_image:
                image_uuid = test_lib.lib_get_image_by_name(image_name, 'Ceph').uuid
            else:
                image_uuid = test_lib.lib_get_image_by_name(image_name, 'ImageStoreBackupStorage').uuid
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
        instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
        vm_creation_option.set_l3_uuids([l3_net_uuid])
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_name(vm_name)
        cond_ps = res_ops.gen_query_conditions('status', '=', 'Connected')
        cond_ps = res_ops.gen_query_conditions('state', '=', 'Enabled', cond_ps)
        all_vail_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond_ps)
        self.ps_type_dict = {ps.type: [] for ps in all_vail_ps}
        map(lambda x: self.ps_type_dict[x[0]].append(x[1]), [(ps.type, ps.uuid) for ps in all_vail_ps])
        if set_ps_uuid:
            self.ps_types = sorted(self.ps_type_dict.keys()) if not self.ps_types else self.ps_types
            if reverse:
                self.ps_types.reverse()
            ps_type = ps_type if ps_type else self.ps_types[0]
            if except_ps_type:
                ps_uuid_for_root_vol = self.get_ps(except_type=except_ps_type).uuid
            else:
                ps_uuid_for_root_vol = random.choice(self.ps_type_dict[ps_type])
            if with_data_vol:
                self.ps_types.remove(ps_type)
                ps_uuid_for_data_vol = random.choice(self.ps_type_dict[random.choice(self.ps_types)])
                systags = ["primaryStorageUuidForDataVolume::%s" % ps_uuid_for_data_vol]
                disk_offering1 = test_lib.lib_get_disk_offering_by_name(os.environ.get('mediumDiskOfferingName'))
                disk_offering_uuids = [disk_offering1.uuid]
                if one_volume:
                    system_tags=["virtio::diskOffering::%s::num::1" % (disk_offering1.uuid)]
                else:
                    disk_offering2 = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
                    disk_offering_uuids.append(disk_offering2.uuid)
                    disk_offering_uuids.append(disk_offering2.uuid)
                    disk_offering_uuids.append(disk_offering2.uuid)
                    system_tags=["virtio::diskOffering::%s::num::2" % (disk_offering2.uuid) ,"virtio::diskOffering::%s::num::1" % (disk_offering1.uuid)]
                system_tags.extend(systags)
                vm_creation_option.set_system_tags(system_tags)
                vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
                if iso_image:
                    vm_creation_option.set_root_disk_uuid(disk_offering1.uuid)
            vm_creation_option.set_ps_uuid(ps_uuid_for_root_vol)
        vm_creation_option.set_timeout(900000)
        vm = test_vm_header.ZstackTestVm()
        vm.set_creation_option(vm_creation_option)
        vm.create()
        if not iso_image:
            vm.check()
        if with_data_vol:
            vol_uuid = [vol for vol in vm.vm.allVolumes if vol.type == 'Data'][0].uuid
            volume = res_ops.query_resource(res_ops.VOLUME, res_ops.gen_query_conditions('uuid', '=', vol_uuid))
            for vol in volume:
                data_volume = zstack_volume_header.ZstackTestVolume()
                data_volume.set_volume(vol)
                data_volume.set_target_vm(vm)
                data_volume.check()
                self.data_volume[data_volume.get_volume().uuid] = data_volume
        self.vm.append(vm)
        self.test_obj_dict.add_vm(vm)

    def check_vol_seperated(self):
        ps_uuids = {vol.primaryStorageUuid for vol in self.vm[0].vm.allVolumes}
        assert len(ps_uuids) > 1

    def copy_data(self, vm):
        vm_ip = vm.get_vm().vmNics[0].ip
        test_lib.lib_wait_target_up(vm_ip, '22', timeout=600)
        cmd = "find /home -iname 'zstack-woodpecker.*'"
        file_path = commands.getoutput(cmd).split('\n')[0]
        file_name = os.path.basename(file_path)
        dst_file = os.path.join('/mnt', file_name)
        src_file_md5 = commands.getoutput('md5sum %s' % file_path).split(' ')[0]
        ssh.scp_file(file_path, dst_file, vm_ip, 'root', 'password')
        (_, dst_md5, _)= ssh.execute('sync; sync; sleep 30; md5sum %s' % dst_file, vm_ip, 'root', 'password')
        dst_file_md5 = dst_md5.split(' ')[0]
        test_util.test_dsc('src_file_md5: [%s], dst_file_md5: [%s]' % (src_file_md5, dst_file_md5))
        assert dst_file_md5 == src_file_md5, 'dst_file_md5 [%s] and src_file_md5 [%s] is not match, stop test' % (dst_file_md5, src_file_md5)
        return self

    def check_data(self, vm):
        vm_ip = vm.get_vm().vmNics[0].ip
        test_lib.lib_wait_target_up(vm_ip, '22', timeout=600)
        check_cmd = "if [ ! -d /mnt/zstackwoodpecker ];then tar xvf /mnt/zstack-woodpecker.tar -C /mnt > /dev/null 2>&1; fi; \
                     grep scenario_config_path /mnt/zstackwoodpecker/zstackwoodpecker/test_lib.py > /dev/null 2>&1 && echo 0 || echo 1"
        (_, ret, _)= ssh.execute(check_cmd, vm_ip, 'root', 'password')
        ret = ret.split('\n')[0]
        assert ret == '0', "data check failed!, the return code is %s, 0 is expected" % ret
        return self

    def get_ps_candidate(self, vol_uuid=None):
        if not vol_uuid:
            vol_uuid = self.vm[0].vm.rootVolumeUuid
        ps_to_migrate = random.choice(datamigr_ops.get_ps_candidate_for_vol_migration(vol_uuid))
        return ps_to_migrate

    def migrate_data_volume(self, detach=True, attach=True):
        for vol_uuid, data_volume in self.data_volume.iteritems():
            dst_ps = self.get_ps_candidate(vol_uuid)
            if detach:
                target_vm_list = [data_volume.get_target_vm()] if data_volume.get_target_vm() else data_volume.get_target_vms()[:]
                for vm in target_vm_list:
                        data_volume.detach(vm.get_vm().uuid)
            datamigr_ops.ps_migrage_data_volume(dst_ps.uuid, vol_uuid)
            data_volume.update()
            if attach:
                for vm in target_vm_list:
                        data_volume.attach(vm)
            assert data_volume.get_volume().primaryStorageUuid == dst_ps.uuid
            self.set_ceph_mon_env(dst_ps.uuid)

    def migrate_vm(self, vm=None):
        if not vm:
            vm = [self.vm[0]]
        for vmobj in vm:
            ps_to_migrate = self.get_ps_candidate(vmobj.get_vm().rootVolumeUuid)
            vmobj.stop()
            datamigr_ops.ps_migrage_root_volume(ps_to_migrate.uuid, vmobj.get_vm().rootVolumeUuid)
            vmobj.start()
            vmobj.check()
            vmobj.update()

    def resize_vm(self, new_size):
        self.root_vol_uuid = self.vm.vm.rootVolumeUuid
        vol_ops.resize_volume(self.root_vol_uuid, new_size)
        conditions = res_ops.gen_query_conditions('uuid', '=', self.vm.vm.uuid)
        self.vm.vm = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)[0]
        return self

    def set_ceph_mon_env(self, ps_uuid):
        cond_vol = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond_vol)[0]
        if ps.type.lower() == 'ceph':
            ps_mon_ip = ps.mons[0].monAddr
            os.environ['cephBackupStorageMonUrls'] = 'root:password@%s' % ps_mon_ip

    def get_bs(self, bs_type):
        conditions = res_ops.gen_query_conditions('type', '=', bs_type)
        bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, conditions)[0]
        return bs

    def get_ps(self, ps_type=None, except_type=None):
        if ps_type:
            conditions = res_ops.gen_query_conditions('type', '=', ps_type)
            ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, conditions)
            return ps[0]
        elif except_type:
            conditions = res_ops.gen_query_conditions('type', '!=', except_type)
            ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, conditions)
            return random.choice(ps)
        else:
            ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
            return random.choice(ps)

    def mount_disk_in_vm(self, vm):
        import tempfile
        test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, '22', timeout=600)
        script_file = tempfile.NamedTemporaryFile(delete=False)
#         script_file.write('''device="/dev/`ls -ltr --file-type /dev | awk '$4~/disk/ {print $NF}' | grep -v '[[:digit:]]'| sort | tail -1`" \n mount ${device}1 /mnt''')
        script_file.write('''device="/dev/`ls -ltr --file-type /dev | awk '$4~/disk/ {print $NF}' | tail -1`" \n mount ${device} /mnt''')
        script_file.close()
        test_lib.lib_execute_shell_script_in_vm(vm.vm, script_file.name)
        return self

    def create_image(self, vm=None, data_volume=None, imagestore=True):
        if imagestore:
            bs = self.get_bs('ImageStoreBackupStorage')
        else:
            bs = self.get_bs('Ceph')
        image_creation_option = test_util.ImageOption()
        image_creation_option.set_timeout(600000)
        image_creation_option.set_backup_storage_uuid_list([bs.uuid])
        if vm:
            self._image_name = 'root-volume-created-image-%s' % time.strftime('%y%m%d-%H%M%S', time.localtime())
            image_creation_option.set_root_volume_uuid(vm.vm.rootVolumeUuid)
            root = True
        else:
            self._image_name = 'data-volume-created-image-%s' % time.strftime('%y%m%d-%H%M%S', time.localtime())
            image_creation_option.set_data_volume_uuid(data_volume.get_volume().uuid)
            root = False
        image_creation_option.set_name(self._image_name)
        self._image = test_image.ZstackTestImage()
        self._image.set_creation_option(image_creation_option)
        self._image.create(root=root)
        self.image = self._image.image
        if bs.type.lower() == 'ceph':
            bs_mon_ip = bs.mons[0].monAddr
            os.environ['cephBackupStorageMonUrls'] = 'root:password@%s' % bs_mon_ip
        self._image.check()

    def create_data_volume(self, shared=False, vms=[], from_offering=True, ps_type=None, except_ps_type=None):
        conditions = res_ops.gen_query_conditions('name', '=', os.getenv('mediumDiskOfferingName'))
        disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING, conditions)[0].uuid
        volume_option = test_util.VolumeOption()
        if from_offering:
            volume_option.set_disk_offering_uuid(disk_offering_uuid)
        else:
            volume_option.set_volume_template_uuid(self.image.uuid)
        volume_option.set_name('multi_ps_data_volume')
        if ps_type:
            ps_uuid = self.get_ps(ps_type).uuid
            volume_option.set_primary_storage_uuid(ps_uuid)
            self.set_ceph_mon_env(ps_uuid)
        elif except_ps_type:
                ps = self.get_ps(except_type=except_ps_type)
                ps_type = ps.type
                volume_option.set_primary_storage_uuid(ps.uuid)
        if shared:
            if ps_type == 'SharedBlock':
                sys_tags = ['ephemeral::shareable', 'capability::virtio-scsi', 'volumeProvisioningStrategy::ThickProvisioning']
            else:
                sys_tags = ['ephemeral::shareable', 'capability::virtio-scsi']
            volume_option.set_system_tags(sys_tags)
        data_volume = create_volume(volume_option, from_offering=from_offering)
        self.test_obj_dict.add_volume(data_volume)
        data_volume.check()
        vms = list(vms) if vms else self.vm
        for vm in vms:
            data_volume.attach(vm)
        vol_uuid = data_volume.get_volume().uuid
#         if from_offering:
#             test_lib.lib_mkfs_for_volume(vol_uuid, vms[0].vm, '/mnt')
        self.data_volume[vol_uuid] = data_volume
        return self

    def create_snapshot(self, vol_uuid_list=[], target=None):
        if not isinstance(vol_uuid_list, types.ListType):
            vol_uuid_list = [vol_uuid_list]
        if target is 'vm':
            for vm in self.vm:
                vol_uuid_list.append(vm.vm.rootVolumeUuid)
        elif target is 'volume':
            for volume in self.data_volume.values():
                vol_uuid_list.append(volume.get_volume().uuid)
        for vol_uuid in vol_uuid_list:
            self.snapshots = self.test_obj_dict.get_volume_snapshot(vol_uuid)
            self.snapshots.set_utility_vm(self.vm[0])
            self.snapshots.create_snapshot('snapshot-%s' % time.strftime('%m%d-%H%M%S', time.localtime()))
    #         self.snapshots.check()
            curr_sp = self.snapshots.get_current_snapshot()
            if curr_sp.get_snapshot().type == 'Storage':
                self.sp_type = curr_sp.get_snapshot().type
                if not self.sp_tree.root:
                    self.sp_tree.add('root')
                self.sp_tree.revert(self.sp_tree.root)
            self.sp_tree.add(curr_sp.get_snapshot().uuid)
            self.sp_tree.show_tree()
            if vol_uuid not in self.snapshot:
                self.snapshot[vol_uuid] = [curr_sp]
            else:
                self.snapshot[vol_uuid].append(curr_sp)

    def delete_snapshot(self, vol_uuid):
        snapshot = random.choice(self.snapshot[vol_uuid])
        sp_uuid = snapshot.get_snapshot().uuid
        self.snapshots = self.test_obj_dict.get_volume_snapshot(vol_uuid)
        self.snapshots.delete_snapshot(snapshot)
        self.snapshot[vol_uuid].remove(snapshot)
        self.sp_tree.delete(sp_uuid)
        nodes = self.sp_tree.tree.keys()
        if 'root' in nodes:
            nodes.remove('root')
        left_sp_uuids = nodes
        self.sp_tree.show_tree()
        for uuid in left_sp_uuids:
            test_util.test_logger('Check if snapshot[uuid: %s] exist' % uuid)
            cond = res_ops.gen_query_conditions('uuid', '=', uuid)
            assert res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, cond)
        assert not res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, res_ops.gen_query_conditions('uuid', '=', sp_uuid))
        return self

    def get_vol_type(self, vol_uuid):
        conditions = res_ops.gen_query_conditions('uuid', '=', vol_uuid)
        vol = res_ops.query_resource(res_ops.VOLUME, conditions)[0]
        return vol.type

    def revert_sp(self, vol_uuid):
        with REVERTSP(self.vm, self.data_volume, vol_uuid):
            sp = random.choice(self.snapshot[vol_uuid])
            self.snapshots = self.test_obj_dict.get_volume_snapshot(vol_uuid)
            self.snapshots.use_snapshot(sp)
            if sp.get_snapshot().type != 'Storage':
                self.sp_tree.revert(sp.get_snapshot().uuid)
        return self

    def sp_check(self):
        self.snapshots.check()
        return self

class REVERTSP(object):
    def __init__(self, vm, data_volume, vol_uuid):
        self.vm = vm
        self.data_volume = data_volume
        self.vol_uuid = vol_uuid
        self.target_vm_list = []

    def __enter__(self):
        if self.vol_uuid in self.data_volume:
            data_volume = self.data_volume[self.vol_uuid]
            self.target_vm_list = [data_volume.get_target_vm()] if data_volume.get_target_vm() else data_volume.get_target_vms()[:]
            if self.target_vm_list:
                for vm in self.target_vm_list:
                    data_volume.detach(vm.get_vm().uuid)
        else:
            for vm in self.vm:
                vm.stop()
        return self

    def __exit__(self, *args):
        if self.target_vm_list:
            data_volume = self.data_volume[self.vol_uuid]
            for vm in self.target_vm_list:
                data_volume.attach(vm)
        else:
            for vm in self.vm:
                vm.start()
                vm.check()
