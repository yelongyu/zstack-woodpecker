import os
import random
import time
import json

import apibinding.inventory as inventory
import zstacklib.utils.debug as debug
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.operations.datamigrate_operations as datamigr_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.stack_template as stack_template_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as ts_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.snap as robot_snapshot_header
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_vol_header

debug.install_runtime_tracedumper()
test_stage = ts_header.TestStage
TestAction = ts_header.TestAction
SgRule = ts_header.SgRule
Port = ts_header.Port
WOODPECKER_MOUNT_POINT = '/tmp/zstack/mnt'
SSH_TIMEOUT = 600
MINI = False
STEP = 1


class robot_test_dict(object):
    def __init__(self):
        self.vm = {}  # {name:volume_obj}
        self.volume = {}  # {name: volume_obj}
        self.snapshot = {}  # {name: snapshot}
        self.backup = {}  # {name:{'backup':backup,'volume':volume,'md5':md5}}
        self.image = {}  # {name: image_obj}
        self.snap_tree = {}  # {vol_name: snap_tree}
        self.volume_check = {}  # {name: robot_flag}

    def __repr__(self):
        str = 'Dict:: \n'
        for k, v in self.vm.items():
            str += ('\tName: %s, Uuid: %s\n' % (k, v.get_vm().uuid))
        for k, v in self.volume.items():
            str += ('\tName: %s, Uuid: %s\n' % (k, v.get_volume().uuid))
        for k, v in self.snapshot.items():
            str += ('\tName: %s, Uuid: %s, Tree: %s, Md5: %s\n' % (
                k, v.get_target_volume().get_volume().uuid, v.snapshot_tree, v.md5sum))
        for k, v in self.backup.items():
            str += ('\tName: %s, Uuid: %s, Volume: %s, Md5: %s\n' % (
                k, v['backup'].uuid, v['backup'].volumeUuid, v['md5']))
        for k, v in self.image.items():
            str += ('\tName: %s, Uuid: %s\n' % (k, v.image.uuid))
        return str

    def add_vm(self, name, vm_obj):
        self.vm[name] = vm_obj

    def remove_vm(self, vm_obj):
        for k, v in self.vm.items():
            if v == vm_obj:
                self.vm.pop(k)

    def add_volume(self, name, vol_obj, volume_check=True):
        self.volume[name] = vol_obj
        if volume_check:
            self.volume_check[name] = True
        else:
            self.volume_check[name] = False

    def remove_volume(self, vol_obj):
        for k, v in self.volume.items():
            if v == vol_obj:
                self.volume.pop(k)
                self.remove_snap_tree(name=k)

    def add_snapshot(self, name, snap_obj):
        self.snapshot[name] = snap_obj

    def remove_snapshot(self, snap_obj):
        for k, v in self.snapshot.items():
            if v == snap_obj:
                self.snapshot.pop(k)

    def add_backup(self, name, backup, volume):
        self.backup[name] = {'backup': backup, 'volume': volume, 'md5': ''}

    def remove_backup(self, backup):
        for k, v in self.backup.items():
            if v['backup'] == backup:
                self.backup.pop(k)

    def set_backup_md5sum(self, name, md5sum):
        self.backup[name]['md5'] = md5sum

    def get_backup_md5sum(self, name):
        return self.backup[name]['md5']

    def add_image(self, name, image_obj):
        self.image[name] = image_obj

    def remove_image(self, image_obj):
        for k, v in self.image.items():
            if v == image_obj:
                self.image.pop(k)

    def add_snap_tree(self, name, snap_tree):
        self.snap_tree[name] = snap_tree

    def remove_snap_tree(self, snap_tree=None, name=None):
        if name:
            self.snap_tree.pop(name)
        for k, v in self.snap_tree.items():
            if v == snap_tree:
                self.snap_tree.pop(k)

    def check(self):
        # vm.check
        for k, vm in self.vm.items():
            vm_check = True
            for volume in vm.get_vm().allVolumes:
                if volume.type == "Root":
                    continue
                if not self.volume_check[volume.name]:
                    vm_check = False
            if vm_check:
                vm.check()

        # volume.check
        for k, volume in self.volume.items():
            if self.volume_check[k]:
                test_util.test_logger('Need to add checker for volume %s' % k)
                volume.check()
            else:
                test_util.test_logger('NO Need to add checker for volume %s' % k)

        # snap_tree.check
        for k, snap_tree in self.snap_tree.items():
            snap_tree.check()

    def cleanup(self):
        for k, backup_dict in self.backup.items():
            backup = backup_dict['backup']
            bs_uuids = [_bs.backupStorageUuid for _bs in backup.backupStorageRefs]
            vol_ops.delete_volume_backup(bs_uuids, backup.uuid)

        # image
        for k, image in self.image.items():
            image.clean()
        # vm.check
        for k, vm in self.vm.items():
            vm.clean()
        # volume.check
        for k, volume in self.volume.items():
            try:
                volume.clean()
            except:# root_volume can not clean
                pass


class robot(object):
    def __init__(self):
        self.robot_resource = {}
        self.resource_stack_template = None
        self.initial_formation_parameters = None
        self.test_dict = robot_test_dict()
        self.path_list = []
        self.default_config = {}

    def set_initial_formation(self, resource_stack):
        self.resource_stack_template = resource_stack

    def get_initial_formation(self):
        return self.resource_stack_template

    def set_initial_formation_parameters(self, initial_formation_parameters):
        self.initial_formation_parameters = initial_formation_parameters

    def get_initial_formation_parameters(self):
        return self.initial_formation_parameters

    def get_test_dict(self):
        return self.test_dict

    def set_path_list(self, path_list):
        self.path_list = path_list

    def get_path_list(self):
        return self.path_list

    def get_robot_resource(self):
        return self.robot_resource

    def get_default_config(self):
        return self.default_config

    # Todo:robot_initial_resource(/bs/ps/image/host/offering/...)
    def initial_resource(self):
        # bs
        cond = res_ops.gen_query_conditions('type', '=', 'ImageStoreBackupStorage')
        bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
        self.robot_resource['bs'] = []
        if not bss:
            test_util.test_fail("Robot test must have imagestore bs")
        for bs in bss:
            test_util.test_logger("Robot resource:: bs: [%s], uuid: [%s}" % (bs.name, bs.uuid))
            self.robot_resource['bs'].append(bs.uuid)

        # ps
        pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
        self.robot_resource['ps'] = []
        for ps in pss:
            test_util.test_logger("Robot resource:: ps: [%s], uuid: [%s}" % (ps.name, ps.uuid))
            self.robot_resource['ps'].append(ps.uuid)

        # vol_image
        if not MINI:
            cond = res_ops.gen_query_conditions('mediaType', '=', 'DataVolumeTemplate')
            images = res_ops.query_resource(res_ops.IMAGE, cond)
            self.robot_resource['vol_image'] = []
            if not images:
                test_util.test_logger("Robot resource must hava data_volume_image.")
                image_option = test_util.ImageOption()
                image_option.set_format('qcow2')
                image_option.set_name('data_volume_image')
                image_option.set_url(os.environ.get('emptyimageUrl'))
                image_option.set_backup_storage_uuid_list(self.robot_resource['bs'])
                image_option.set_timeout(120000)
                image_option.set_mediaType("DataVolumeTemplate")
                images.append(img_ops.add_image(image_option))
            for image in images:
                test_util.test_logger("Robot resource:: vol_image: [%s], uuid: [%s}" % (image.name, image.uuid))
                self.robot_resource['vol_image'].append(image.uuid)

        # vm_image not include vrouter image
        cond = res_ops.gen_query_conditions('mediaType', '=', 'RootVolumeTemplate')
        cond = res_ops.gen_query_conditions('system', '=', 'false', cond)
        images = res_ops.query_resource(res_ops.IMAGE, cond)
        self.robot_resource['vm_image'] = []
        for image in images:
            test_util.test_logger("Robot resource:: vm_image: [%s], uuid: [%s}" % (image.name, image.uuid))
            self.robot_resource['vm_image'].append(image.uuid)

        # host
        hosts = res_ops.query_resource(res_ops.HOST)
        self.robot_resource['host'] = []
        for host in hosts:
            test_util.test_logger("Robot resource:: host: [%s], uuid: [%s}" % (host.name, host.uuid))
            self.robot_resource['host'].append(host.uuid)

    # Todo:create_resource_stack
    def create_resource_stack(self):
        stack_template_option = test_util.StackTemplateOption()
        stack_template_option.set_name("robot_test")
        stack_template_option.set_templateContent(self.resource_stack_template)
        stack_template = stack_template_ops.add_stack_template(stack_template_option)
        self.initial_formation_auto_parameter(stack_template.uuid)
        resource_stack_option = test_util.ResourceStackOption()
        resource_stack_option.set_template_uuid(stack_template.uuid)
        resource_stack_option.set_parameters(self.get_initial_formation_parameters())
        resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)
        resource_list = resource_stack_ops.get_resource_from_resource_stack(resource_stack.uuid)
        self.import_resource_from_formation(resource_list)

    def initial_formation_auto_parameter(self, template_uuid):
        if self.get_initial_formation_parameters():
            return

        para_invs = stack_template_ops.check_stack_template(template_uuid)
        instance_offering_dict = dict()
        image_dict = dict()
        pub_l3network_dict = dict()
        pri_l3network_dict = dict()
        disk_offering_dict = dict()
        for para_inv in para_invs.parameters:
            test_util.test_logger("Robot:: check stack template: [%s] " % para_inv)
            if para_inv.resourceType == "InstanceOffering":
                if para_inv.paramName in instance_offering_dict:
                    test_util.test_fail("duplicate parameter name found, should be a bug")
                cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
                cond = res_ops.gen_query_conditions('type', '=', 'UserVm', cond)
                for paraname in instance_offering_dict:
                    cond = res_ops.gen_query_conditions('uuid', '!=', instance_offering_dict[paraname], cond)
                instance_offerings = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)
                if not instance_offerings:
                    test_util.test_fail("Not enough disinct resource for so many parameters")
                instance_offering_dict[para_inv.paramName] = instance_offerings[0].uuid
            elif para_inv.resourceType == "Image":
                if para_inv.paramName in image_dict:
                    test_util.test_fail("duplicate parameter name found, should be a bug")

                cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
                cond = res_ops.gen_query_conditions('status', '=', 'Ready', cond)
                if not image_dict:
                    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('imageName_net'), cond)
                    images = res_ops.query_resource(res_ops.IMAGE, cond)
                else:
                    for paraname in image_dict:
                        cond = res_ops.gen_query_conditions('uuid', '!=', image_dict[paraname], cond)
                    images = res_ops.query_resource(res_ops.IMAGE, cond)
                if not images:
                    test_util.test_fail("Not enough disinct resource for so many parameters")

                image_dict[para_inv.paramName] = images[0].uuid
            elif para_inv.resourceType == "L3Network":
                if "pub" in para_inv.paramName.lower():
                    if para_inv.paramName in pub_l3network_dict:
                        test_util.test_fail("duplicate parameter name found, should be a bug")
                    if not pub_l3network_dict:
                        public_l3 = test_lib.lib_get_l3_by_name(os.environ.get('l3PublicNetworkName'))
                    else:
                        test_util.test_fail("No more public l3")
                    if not public_l3:
                        test_util.test_fail("Not enough disinct resource for so many parameters")

                    pub_l3network_dict[para_inv.paramName] = public_l3.uuid
                else:
                    if para_inv.paramName in pri_l3network_dict:
                        test_util.test_fail("duplicate parameter name found, should be a bug")

                    public_l3 = test_lib.lib_get_l3_by_name(os.environ.get('l3PublicNetworkName'))
                    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
                    cond = res_ops.gen_query_conditions('system', '=', 'false')
                    cond = res_ops.gen_query_conditions('uuid', '!=', public_l3.uuid, cond)
                    for paraname in pri_l3network_dict:
                        cond = res_ops.gen_query_conditions('uuid', '!=', pri_l3network_dict[paraname], cond)
                    pri_l3s = res_ops.query_resource(res_ops.L3_NETWORK, cond)
                    if not pri_l3s:
                        test_util.test_fail("Not enough disinct resource for so many parameters")

                    pri_l3network_dict[para_inv.paramName] = pri_l3s[0].uuid
            elif para_inv.resourceType == "DiskOffering":
                if para_inv.paramName in disk_offering_dict:
                    test_util.test_fail("duplicate parameter name found, should be a bug")

                if not disk_offering_dict:
                    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
                    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('smallDiskOfferingName'), cond)
                    disk_offerings = res_ops.query_resource(res_ops.DISK_OFFERING, cond)
                else:
                    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
                    for paraname in disk_offering_dict:
                        cond = res_ops.gen_query_conditions('uuid', '!=', disk_offering_dict[paraname], cond)
                    disk_offerings = res_ops.query_resource(res_ops.DISK_OFFERING, cond)
                if not disk_offerings:
                    test_util.test_fail("Not enough disinct resource for so many parameters")

                disk_offering_dict[para_inv.paramName] = disk_offerings[0].uuid
            all_dict = instance_offering_dict.copy()
            all_dict.update(image_dict)
            all_dict.update(pub_l3network_dict)
            all_dict.update(pri_l3network_dict)
            all_dict.update(disk_offering_dict)
            self.set_initial_formation_parameters(str(all_dict).replace("u'", "'"))

    # Todo:import resource_stack auto created vm/volumes(not include vrouter)
    def import_resource_from_formation(self, resource_list):
        # import VM
        imported_resource = []
        for resource in resource_list:
            if resource.hasattr("VmInstance"):
                test_util.test_logger("debug VmInstance %s" % (resource["VmInstance"]["uuid"]))
                test_util.test_logger("debug VmInstance %s" % (resource["VmInstance"]["name"]))
                if resource["VmInstance"]["uuid"] in imported_resource:
                    continue

                imported_resource.append(resource["VmInstance"]["uuid"])

                if resource["VmInstance"]["type"] == "ApplianceVm":
                    continue
                new_vm = zstack_vm_header.ZstackTestVm()
                new_vm.create_from(resource["VmInstance"]["uuid"])
                new_vm.update()
                root_volume = zstack_vol_header.ZstackTestVolume()
                root_volume.create_from(test_lib.lib_get_root_volume(new_vm.get_vm()).uuid)

                new_vm.test_volumes.append(root_volume)
                root_snap_tree = robot_snapshot_header.ZstackSnapshotTree(root_volume)
                root_snap_tree.update()
                root_volume.snapshot_tree = root_snap_tree
                self.test_dict.add_volume(name=new_vm.vm.name + "-root", vol_obj=root_volume)
                self.test_dict.add_snap_tree(name=new_vm.vm.name + "-root", snap_tree=root_snap_tree)
                self.default_config['HOST'] = new_vm.get_vm().hostUuid
                self.default_config['PS'] = root_volume.get_volume().primaryStorageUuid

                # import Volume already attached
                volume_index = 1
                for volume in new_vm.get_vm().allVolumes:
                    if volume.type != "Data":
                        continue
                    if volume.uuid in imported_resource:
                        continue
                    new_volume_name = "%s-volume%s" % (resource["VmInstance"]["name"], volume_index)
                    vol_ops.update_volume(volume.uuid, new_volume_name, None)
                    new_volume = zstack_vol_header.ZstackTestVolume()
                    new_volume.create_from(volume.uuid)
                    new_volume_snap_tree = robot_snapshot_header.ZstackSnapshotTree(new_volume)
                    new_volume_snap_tree.update()
                    new_volume.snapshot_tree = new_volume_snap_tree
                    self.test_dict.add_volume(new_volume_name, new_volume)
                    test_util.test_logger("@@test_dict_volume_keys:{}@@".format(self.test_dict.volume.keys()))
                    test_util.test_logger("@@test_dict_volume_values:{}@@".format(self.test_dict.volume.values()))
                    self.test_dict.add_snap_tree(volume.name + "-st", snap_tree=new_volume_snap_tree)
                    imported_resource.append(volume.uuid)
                    volume_index += 1
                new_vm.update()
                self.test_dict.add_vm(resource["VmInstance"]["name"], new_vm)

        # import Volume
        for resource in resource_list:
            if resource.hasattr("Volume"):
                test_util.test_logger("debug Volume list %s" % (resource["Volume"]["uuid"]))
                test_util.test_logger("debug Volume list %s" % (resource["Volume"]["name"]))
                if resource["Volume"]["uuid"] in imported_resource:
                    continue

                imported_resource.append(resource["Volume"]["uuid"])

                new_volume = zstack_vol_header.ZstackTestVolume()
                new_volume.create_from(resource["Volume"]["uuid"])

                self.test_dict.add_volume(resource["Volume"]['name'], new_volume)

        # import VIP

        # import EIP

        # import PF

    # Todo:run_actions and check

    def initial(self, path_list, resource_stack=None):
        self.set_path_list(path_list)
        self.initial_resource()
        if resource_stack:
            self.set_initial_formation(resource_stack)
            self.create_resource_stack()

    def path(self):
        for _path in self.path_list:
            yield _path


def robot_run_constant_path(robot_test_obj, set_robot=True):
    test_lib.ROBOT = set_robot
    constant_path = robot_test_obj.get_path_list()

    path = robot_test_obj.path()
    test_util.test_logger("Robot action start!")
    global STEP
    while True:
        test_dict = robot_test_obj.get_test_dict()
        resource_dict = robot_test_obj.get_robot_resource()

        test_util.test_logger(constant_path)
        test_util.test_logger(resource_dict)
        test_util.test_logger(test_dict)
        try:
            tmpt = next(path)
            action = tmpt[0]
            args = tmpt[1:]
            run_action(robot_test_obj, action, args, STEP)
            STEP += 1
        except StopIteration:
            break

        debug(robot_test_obj)
        if set_robot:
            robot_test_obj.test_dict.check()

    test_util.test_logger("Robot action run over!")


def run_action(robot_test_obj, action, args, index):
    test_util.test_logger("New Round: Start Robot action %s step [ %s ] with args [%s] " % (index, action, args))
    action_dict[action](robot_test_obj, args)
    test_util.test_logger("Finish Robot action [ %s ] " % action)


default_snapshot_depth = 8


def change_global_config_sp_depth(robot_test_obj, args):
    global default_snapshot_depth
    if not args:
        test_util.test_fail("no snapshot depth available for next action: change_global_config_sp_depth")
    default_snapshot_depth = conf_ops.change_global_config('volumeSnapshot', 'incrementalSnapshot.maxNum', args[0])


def recover_global_config_sp_depth(robot_test_obj, args):
    conf_ops.change_global_config('volumeSnapshot', 'incrementalSnapshot.maxNum', default_snapshot_depth)


def cleanup_imagecache_on_ps(robot_test_obj, args):
    for ps_uuid in robot_test_obj.get_robot_resource()['ps']:
        ps_ops.cleanup_imagecache_on_primary_storage(ps_uuid)


def idel(robot_test_obj, args):
    if len(args) > 1:
        test_util.test_fail("invalid parameter for next action: idle")
    elif len(args) == 1:
        idle_time = args[0]
        time.sleep(int(idle_time))
    else:
        test_lib.lib_vm_random_idel_time(1, 5)


def create_vm(robot_test_obj, args):
    name = args[0]
    l3_uuid = None
    disk_offering_uuid = None
    ps_type = None
    provisiong = None

    arg_dict = parser_args(args[1:])
    if 'flag' in arg_dict:
        flag = arg_dict['flag']
        if "thick" in flag:
            provisiong = "Thick"
        if "thin" in flag:
            provisiong = "Thin"
        if "ceph" in flag:
            ps_type = "Ceph"
        if "sblk" in flag:
            ps_type = "SharedBlock"

    if 'network' in arg_dict:
        if arg_dict['network'] == "random":
            cond = res_ops.gen_query_conditions("system", "=", "false")
            l3s = res_ops.query_resource(res_ops.L3_NETWORK, cond)
            l3_uuid = random.choice(l3s).uuid
        else:
            network_name = arg_dict["network"]
            cond = res_ops.gen_query_conditions("name", "=", network_name)
            l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond)
            if not l3:
                test_util.test_fail("Network: %s does not exist" % network_name)
            else:
                l3_uuid = l3[0].uuid

    if arg_dict.has_key('data_volume') and arg_dict['data_volume'] == 'true':
        disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
        dataVolumeSystemTags = ["capability::virtio-scsi"]

    if provisiong:
        rootVolumeSystemTag = "volumeProvisioningStrategy::%sProvisioning" % provisiong

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid

    cond = res_ops.gen_query_conditions("type", "=", "UserVm")
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)[0].uuid

    if ps_type:
        cond = res_ops.gen_query_conditions("type", "=", ps_type)
        pss = res_ops.gen_query_conditions(res_ops.PRIMARY_STORAGE, cond)
        if not pss:
            test_util.test_fail("there is no primarystorage type: [%s]" % ps_type)
        vm_creation_option.set_ps_uuid(pss[0].uuid)

    if l3_uuid:
        vm_creation_option.set_l3_uuids([l3_uuid])
    else:
        l3_name = os.environ.get('l3VlanNetworkName1')
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        vm_creation_option.set_l3_uuids([l3_net_uuid])

    if disk_offering_uuid:
        vm_creation_option.set_data_disk_uuids([disk_offering_uuid])
        vm_creation_option.set_dataVolume_systemTags(dataVolumeSystemTags)

    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(name)
    vm_creation_option.set_rootVolume_systemTags([rootVolumeSystemTag])

    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    root_volume = zstack_vol_header.ZstackTestVolume()
    root_volume.create_from(vm.vm.allVolumes[0].uuid)
    vm.test_volumes.append(root_volume)
    root_snap_tree = robot_snapshot_header.ZstackSnapshotTree(root_volume)
    root_snap_tree.update()
    root_volume.snapshot_tree = root_snap_tree
    robot_test_obj.test_dict.add_vm(name, vm_obj=vm)
    robot_test_obj.test_dict.add_volume(name=vm.vm.name + "-root", vol_obj=root_volume)
    robot_test_obj.test_dict.add_snap_tree(name=vm.vm.name + "-root", snap_tree=root_snap_tree)
    robot_test_obj.default_config['PS'] = root_volume.get_volume().primaryStorageUuid
    robot_test_obj.default_config['HOST'] = vm.get_vm().hostUuid

    if arg_dict.has_key('data_volume') and arg_dict['data_volume'] == 'true':
        volume = zstack_vol_header.ZstackTestVolume()
        cond = res_ops.gen_query_conditions("name", "=", "DATA-for-%s" % name)
        vol_inv = res_ops.query_resource(res_ops.VOLUME, cond)[0]
        vol_ops.update_volume(vol_inv.uuid, "auto-volume" + name[-1],
                              "change %s to auto-volume%s" % (vol_inv.name, name[-1]))

        volume.create_from(vol_inv.uuid, target_vm=vm)
        vm.test_volumes.append(volume)
        volume_snap_tree = robot_snapshot_header.ZstackSnapshotTree(volume)
        volume_snap_tree.update()
        volume.snapshot_tree = volume_snap_tree
        robot_test_obj.test_dict.add_volume("auto-volume" + name[-1], volume)
        robot_test_obj.test_dict.add_snap_tree("auto-volume" + name[-1], volume_snap_tree)


def migrate_vm(robot_test_obj, args):
    target_vm = None
    if not args:
        test_util.test_fail("no resource available for next action: migrate vm")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]
    # if not target_vm:
    #     test_util.test_fail("no resource available for next action: migrate_vm")

    target_hosts = vm_ops.get_vm_migration_candidate_hosts(target_vm.vm.uuid)
    if not target_hosts:
        test_util.test_fail('no avaiable host was found for doing vm migration')
    else:
        target_vm.migrate(target_hosts[0].uuid)


def create_vm_by_image(robot_test_obj, args):
    if len(args) < 3:
        test_util.test_fail("no resource available for next action: create vm by image")
    target_image_name = args[0]
    image_format = args[1]
    vm_name = args[2]
    target_image = None
    ps_uuid = robot_test_obj.robot_resource['ps'][0]

    cond = res_ops.gen_query_conditions("system", "=", "false")
    if image_format != 'iso':
        cond = res_ops.gen_query_conditions("mediaType", "=", "RootVolumeTemplate", cond)
    cond = res_ops.gen_query_conditions("name", "=", target_image_name, cond)
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    if images:
        target_image = images[0]

    vm_creation_option = test_util.VmOption()
    if image_format == "iso":
        if not MINI:
            root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName')).uuid
            vm_creation_option.set_root_disk_uuid(root_disk_uuid)
        else:
            vm_creation_option.set_root_disk_size(4294967296)  # 4G
        if not target_image:
            target_image = add_image(robot_test_obj, [target_image_name, 'root', os.environ.get('isoForVmUrl')])
    if not MINI:
        vm_creation_option.set_ps_uuid(ps_uuid)
    else:
        cluster = res_ops.query_resource(res_ops.CLUSTER)[0]
        robot_test_obj.default_config['MINI_CLUSTER'] = cluster.uuid
        vm_creation_option.set_cluster_uuid(cluster.uuid)
    vm_creation_option.set_image_uuid(target_image.uuid)
    vm_creation_option.set_name(vm_name)
    # conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    #     # instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    #     # vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_cpu_num(2)
    vm_creation_option.set_memory_size(2147483648)
    l3_name = os.environ.get('l3PublicNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])

    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    root_volume = zstack_vol_header.ZstackTestVolume()
    root_volume.create_from(vm.vm.allVolumes[0].uuid)
    vm.test_volumes.append(root_volume)
    root_snap_tree = robot_snapshot_header.ZstackSnapshotTree(root_volume)
    root_snap_tree.update()
    root_volume.snapshot_tree = root_snap_tree
    robot_test_obj.test_dict.add_vm(vm_name, vm_obj=vm)
    robot_test_obj.test_dict.add_volume(name=vm.vm.name + "-root", vol_obj=root_volume)
    robot_test_obj.test_dict.add_snap_tree(name=vm.vm.name + "-root", snap_tree=root_snap_tree)
    robot_test_obj.default_config['PS'] = root_volume.get_volume().primaryStorageUuid
    robot_test_obj.default_config['HOST'] = vm.get_vm().hostUuid

    if image_format == "iso":
        host = test_lib.lib_get_vm_host(vm.get_vm())
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm.get_vm())
        cmd = 'ping -c 5 -W 5 %s >/tmp/ping_result 2>&1; ret=$?; cat /tmp/ping_result; exit $ret' % vm.get_vm().vmNics[
            0].ip
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, vm.get_vm().vmNics[0].ip,
                                                                 test_lib.lib_get_vm_username(vm.get_vm()),
                                                                 test_lib.lib_get_vm_password(vm.get_vm()), cmd)
        cmd = "yum install -y java wget"
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, vm.get_vm().vmNics[0].ip,
                                                                 test_lib.lib_get_vm_username(vm.get_vm()),
                                                                 test_lib.lib_get_vm_password(vm.get_vm()), cmd)
        cmd = "wget -np -r -nH --cut-dirs=2 http://172.20.1.27/mirror/vdbench/; chmod a+x /root/vdbench/vdbench"
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, vm.get_vm().vmNics[0].ip,
                                                                 test_lib.lib_get_vm_username(vm.get_vm()),
                                                                 test_lib.lib_get_vm_password(vm.get_vm()), cmd)


def stop_vm(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: stop vm")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]

    target_vm.stop()
    target_vm.update()

    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()


def start_vm(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: start vm")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]

    target_vm.start()
    target_vm.update()

    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()


def suspend_vm(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: suspend vm")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]

    target_vm.suspend()
    target_vm.update()

    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()


def resume_vm(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: resume vm")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]

    target_vm.resume()
    target_vm.update()

    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()


def reboot_vm(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: reboot vm")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]

    target_vm.reboot()
    target_vm.update()

    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()


def run_workloads(robot_test_obj, args):
    target_vms = []
    target_cmd = ''
    timeout = 600
    pre_cmd = ""

    WORKLOADS = {
        "FIO": "fio -filename=/root/test-fio -direct=1 -iodepth 32 -thread -rw=randrw -rwmixread=70 -ioengine=libaio -bs=4k -size=90% -numjobs=8 -runtime=600 -group_reporting -name=fio_test.txt",
        "IPERF": "iperf3 -s"}

    if len(args) < 1:
        test_util.test_fail("no resource available for next action: run_workloads")

    for vm_name in args[0].split('=')[1].split(','):
        target_vm = robot_test_obj.get_test_dict().vm[vm_name]
        target_vms.append(target_vm)
        if target_vm.get_state() != vm_header.RUNNING:
            test_util.test_fail("run_workloads: Failed to run workloads due that VM %s is not in Running state" % (
                target_vm.get_vm().uuid))

    for wkd, cmd in WORKLOADS.items():
        if args[1] == wkd:
            if len(args) > 2:
                target_cmd = args[2]
                timeout = int(args[3])
            else:
                target_cmd = cmd

    if "iperf3" in target_cmd:
        pre_cmd = "yum install iperf3 --nogpgcheck -y; iptables -F; service iptables save"

    target_cmd = "echo " + target_cmd + " \& >> /etc/rc.local"

    for target_vm in target_vms:
        host = test_lib.lib_get_vm_host(target_vm.get_vm())
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(target_vm.get_vm())
        default_l3_uuid = target_vm.get_vm().defaultL3NetworkUuid
        nic = target_vm.get_vm().vmNics[0]

        if pre_cmd:
            pre_cmd_result = test_lib.lib_ssh_vm_cmd_by_agent(host.managementIp, nic.ip,
                                                          test_lib.lib_get_vm_username(target_vm.get_vm()),
                                                          test_lib.lib_get_vm_password(target_vm.get_vm()), pre_cmd)

        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent(host.managementIp, nic.ip,
                                                      test_lib.lib_get_vm_username(target_vm.get_vm()),
                                                      test_lib.lib_get_vm_password(target_vm.get_vm()), target_cmd)
        test_util.test_logger("run_workloads - cmd result:  %s" % str(cmd_result.result))

        target_vm.reboot()
        target_vm.update()

        for volume in target_vm.test_volumes:
            volume.update()
            volume.update_volume()

    time.sleep(timeout)

def run_host_workloads(robot_test_obj, args):
    target_host = ""
    background = False
    timeout = 30
    pre_cmd = ""

    if len(args) == 2:
        target_host = args[0]
        cmd = args[1]
    elif len(args) == 3:
        target_host = args[0]
        cmd = args[1]
        if "background" in args[2]:
            background = True
        elif "timeout" in args[2]:
            timeout = int(args[2].split("=")[1])
    else:
        test_util.test_fail("arguments invalid for next action: run host workloads")

    if "fio" in cmd:
        pre_cmd = "yum install fio --nogpgcheck -y"
    elif "vdbench" in cmd:
        pre_cmd = "wget -np -r -nH --cut-dirs=2 http://172.20.1.27/mirror/vdbench/; chmod a+x /root/vdbench/vdbench"
    elif "iperf3" in cmd:
        pre_cmd = "yum install iperf3 --nogpgcheck -y"
        target_vm = robot_test_obj.get_test_dict().vm[cmd.split()[2]]
        target_ip = target_vm.get_vm().vmNics[0].ip
        cmd = cmd.replace(cmd.split()[2], target_ip)

    if background:
        cmd = cmd + ' &'

    if target_host == "all":
        for host in test_lib.lib_find_hosts_by_status("Connected"):
            pre_rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), pre_cmd)
            time.sleep(1)
            rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), cmd, timeout)
            if not rsp and not background:
                test_util.test_fail('%s failed on %s' % (cmd, host.managementIp))
    elif target_host == "random":
        host = random.choice(test_lib.lib_find_hosts_by_status("Connected"))
        pre_rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), pre_cmd)
        time.sleep(1)
        rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), cmd, timeout)
        if not rsp and not background:
            test_util.test_fail('%s failed on %s' % (cmd, host.managementIp))
    else:
        host = test_lib.lib_find_host_by_HostIp(target_host)
        if not host:
            test_util.test_fail('no host found for IP %s' % (target_host))
        pre_rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), pre_cmd)
        time.sleep(1)
        rsp = test_lib.lib_execute_ssh_cmd(host[0].managementIp, host[0].username, os.environ.get('hostPassword'), cmd, timeout)
        if not rsp and not background:
            test_util.test_fail('%s failed on %s' % (cmd, target_host))

def reboot_host(robot_test_obj, args):
    target_host = ""
    hosts = []
    timeout = 1800

    if len(args) == 2:
        target_host = args[0]
        action = args[1]
    else:
        test_util.test_fail("arguments invalid for next action: reboot host")

    if action == "reboot":
        cmd = "reboot"
    elif action == "soft_crash":
        cmd = "echo c > /proc/sysrq-trigger"

    test_util.test_logger('Reboot Host: Action %s' % (cmd))

    if target_host == "all":
        for host in test_lib.lib_find_hosts_by_status("Connected"):
            hosts.append(host)
            rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), cmd)
            if rsp:
                test_util.test_fail('%s failed on %s' % (cmd, host.managementIp))
    elif target_host == "random":
        host = random.choice(test_lib.lib_find_hosts_by_status("Connected"))
        hosts.append(host)
        rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), cmd)
        if rsp:
            test_util.test_fail('%s failed on %s' % (cmd, host.managementIp))
    else:
        host = test_lib.lib_find_host_by_HostIp(target_host)
        hosts.append(host[0])
        if not host:
            test_util.test_fail('no host found for IP %s' % (target_host))
        rsp = test_lib.lib_execute_ssh_cmd(host[0].managementIp, host[0].username, os.environ.get('hostPassword'), cmd)
        if rsp:
            test_util.test_fail('%s failed on %s' % (cmd, target_host))

    time.sleep(120)

    while timeout:
        for host in hosts:
            try:
                _host = test_lib.lib_find_host_by_HostIp(host.managementIp)
            except:
                timeout -= 15
                if timeout == 0:
                    test_util.test_fail('%s is not up in 1800 seconds after reboot' % (host.managementIp))
                time.sleep(15)
                continue

            if _host[0].status == "Connected":
                test_util.test_logger('%s is up and Connected' % (host.managementIp))
                hosts.remove(host)
                continue
            else:
                timeout -= 15
                if timeout == 0:
                    test_util.test_fail('%s is not up in 1800 seconds after reboot' % (host.managementIp))
                time.sleep(15)

        if not hosts:
            test_util.test_logger('all the hosts are up and Connected')
            break

    time.sleep(120)

    timeout = 1800
    target_vms = []

    for vm_name, target_vm in robot_test_obj.get_test_dict().vm.iteritems():
        target_vms.append(target_vm)

    while timeout:
        for target_vm in target_vms:
            target_vm.update()

            cond = res_ops.gen_query_conditions("resourceUuid", '=', target_vm.get_vm().uuid)
            cond = res_ops.gen_query_conditions("tag", '=', "ha::NeverStop", cond)
            tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)

            if tag:
                if target_vm.get_vm().state == "Running":
                    target_vm.set_state(vm_header.RUNNING)
                    target_vms.remove(target_vm)
                    continue
                else:
                    timeout -= 15
                    if timeout == 0:
                        test_util.test_fail('VM %s is not in Stopped or Running state in 1800 seconds after reboot' % (
                            target_vm.get_vm().name))
                    time.sleep(15)
            else:
                if target_vm.get_vm().state == "Stopped":
                    target_vm.set_state(vm_header.STOPPED)
                    target_vms.remove(target_vm)
                    continue
                else:
                    timeout -= 15
                    if timeout == 0:
                        test_util.test_fail('VM %s is not in Stopped or Running state in 1800 seconds after reboot' % (
                            target_vm.get_vm().name))
                    time.sleep(15)
        if not target_vms:
            test_util.test_logger('all the VMs are Stopped or Running after reboot')
            break


def expunge_vm(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: expunge vm")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]

    target_vm.expunge()

    robot_test_obj.test_dict.remove_volume(target_vm.test_volumes[0])
    robot_test_obj.test_dict.remove_vm(target_vm)
    robot_test_obj.test_dict.remove_snap_tree(args[0] + '-root')


def delete_vm(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: delete vm")

    destroy_vm(robot_test_obj, [args[0]])
    expunge_vm(robot_test_obj, [args[0]])


def reinit_vm(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: reinit vm")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]

    target_vm.reinit()
    target_vm.update()

    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()

    robot_test_obj.test_dict.volume[args[0] + '-root'].snapshot_tree.Newhead = True


def clone_vm(robot_test_obj, args):
    if len(args) < 2:
        test_util.test_fail("no resource available for next action: clone_vm")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]
    clone_vm_name = args[1]

    full = False if len(args) != 3 else True
    invs = vm_ops.clone_vm(target_vm.get_vm().uuid, [clone_vm_name], None, full=full)[0]

    vm_uuid = invs.inventory.uuid
    new_vm = zstack_vm_header.ZstackTestVm()
    new_vm.create_from(vm_uuid)
    root_volume = zstack_vol_header.ZstackTestVolume()
    root_volume.create_from(test_lib.lib_get_root_volume(new_vm.get_vm()).uuid)

    new_vm.test_volumes.append(root_volume)
    root_snap_tree = robot_snapshot_header.ZstackSnapshotTree(root_volume)
    root_snap_tree.update()
    root_volume.snapshot_tree = root_snap_tree
    robot_test_obj.test_dict.add_vm(new_vm.vm.name, vm_obj=new_vm)
    robot_test_obj.test_dict.add_volume(name=new_vm.vm.name + "-root", vol_obj=root_volume)
    robot_test_obj.test_dict.add_snap_tree(name=new_vm.vm.name + "-root", snap_tree=root_snap_tree)

    if full:
        for vol in invs.inventory.allVolumes:
            if vol.type == 'Data':
                for volume in target_vm.test_volumes:
                    if volume.get_volume().uuid in vol.name:
                        new_name = new_vm.vm.name.replace(target_vm.get_vm().name, volume.name)
                        vol_ops.update_volume(vol.uuid, new_name, "change_name")

                        new_volume = zstack_vol_header.ZstackTestVolume()
                        new_volume.create_from(vol.uuid, new_vm)
                        new_vm.test_volumes.append(new_volume)
                        robot_test_obj.test_dict.add_volume(new_name, new_volume)
                        new_volume.set_md5sum(volume.get_md5sum())

                        snap_tree = robot_snapshot_header.ZstackSnapshotTree(new_volume)
                        new_volume.snapshot_tree = snap_tree
                        snap_tree.update()
                        robot_test_obj.test_dict.add_snap_tree(new_name, snap_tree)
                        new_volume.update()
                        new_volume.update_volume()

    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()


def change_vm_image(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: change vm image")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]
    vm_root_image_uuid = target_vm.get_vm().imageUuid

    ps_uuid = test_lib.lib_get_root_volume(target_vm.get_vm()).primaryStorageUuid
    cond = res_ops.gen_query_conditions('uuid', '!=', vm_root_image_uuid)
    cond = res_ops.gen_query_conditions('mediaType', '=', "RootVolumeTemplate", cond)
    cond = res_ops.gen_query_conditions('system', '=', "false", cond)
    target_images = res_ops.query_resource(res_ops.IMAGE, cond)

    for ti in target_images:
        for tbs in ti.backupStorageRefs:
            bs_inv = test_lib.lib_get_backup_storage_by_uuid(tbs.backupStorageUuid)
            ps_uuid_list = test_lib.lib_get_primary_storage_uuid_list_by_backup_storage(bs_inv.uuid)
            if ps_uuid not in ps_uuid_list:
                continue
            if bs_inv.name != "only_for_robot_backup_test":
                target_image = ti
                break

    if not target_vm or not target_image:
        test_util.test_fail("no resource available for next action: change vm image")

    target_vm.change_vm_image(target_image.uuid)
    target_vm.update()

    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()

    robot_test_obj.test_dict.volume[args[0] + '-root'].snapshot_tree.Newhead = True


def create_vm_backup(robot_test_obj, args):
    if len(args) < 2:
        test_util.test_fail("no resource available for next action: create vm backup")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]
    backup_name = args[1]

    zone_inv = res_ops.query_resource(res_ops.ZONE)[0]
    cond = res_ops.gen_query_conditions("attachedZoneUuids", "=", zone_inv.uuid)
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid

    backup_option = test_util.BackupOption()
    backup_option.set_name(backup_name)
    backup_option.set_volume_uuid(test_lib.lib_get_root_volume(target_vm.get_vm()).uuid)
    backup_option.set_backupStorage_uuid(bs_uuid)

    if len(args) == 3:
        backup_option.set_mode('full')

    backups = vm_ops.create_vm_backup(backup_option)

    for backup in backups:
        for test_volume in target_vm.test_volumes:
            if backup.volumeUuid == test_volume.get_volume().uuid:
                robot_test_obj.test_dict.add_backup(backup_name + '-' + backup.volumeUuid, backup, test_volume)
                md5sum = test_volume.get_md5sum()
                robot_test_obj.test_dict.set_backup_md5sum(backup_name + '-' + backup.volumeUuid, md5sum)


def use_vm_backup(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: use vm backup")

    backup_name = args[0]

    cond = res_ops.gen_query_conditions("name", '=', backup_name)
    groupUuid = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)[0].groupUuid
    vol_ops.revert_vm_from_backup(groupUuid)

    test_dict = robot_test_obj.get_test_dict()
    for name, backup_dict in test_dict.backup.items():
        if backup_name in name:
            test_volume = backup_dict['volume']
            test_volume.update()
            test_volume.update_volume()
            md5sum = test_dict.get_backup_md5sum(name)
            test_volume.set_md5sum(md5sum)
            test_volume.snapshot_tree.Newhead = True


def create_vm_from_vmbackup(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: create vm from vm_backup")

    test_dict = robot_test_obj.get_test_dict()
    backup_dict = None
    for k, v in test_dict.backup.items():
        if args[0] in k:
            backup_dict = v
            d_backup_name = k

    target_backup = backup_dict['backup']

    l3_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetworkName1')).uuid
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(os.environ.get('instanceOfferingName_s')).uuid
    vm_name = target_backup.name.split('-')[0] + "-from-" + target_backup.name.split('-')[1]
    backup_vm = vol_ops.create_vm_from_vm_backup(vm_name, target_backup.groupUuid,
                                                 instance_offering_uuid, l3_uuid, [l3_uuid])
    new_vm = zstack_vm_header.ZstackTestVm()
    new_vm.create_from(backup_vm.uuid)

    root_volume = zstack_vol_header.ZstackTestVolume()
    root_volume.create_from(test_lib.lib_get_root_volume(new_vm.get_vm()).uuid)

    new_vm.test_volumes.append(root_volume)
    root_snap_tree = robot_snapshot_header.ZstackSnapshotTree(root_volume)
    root_snap_tree.update()
    root_volume.snapshot_tree = root_snap_tree
    robot_test_obj.test_dict.add_vm(new_vm.vm.name, vm_obj=new_vm)
    robot_test_obj.test_dict.add_volume(name=new_vm.vm.name + "-root", vol_obj=root_volume)
    robot_test_obj.test_dict.add_snap_tree(name=new_vm.vm.name + "-root", snap_tree=root_snap_tree)

    cond = res_ops.gen_query_conditions("groupUuid", '=', target_backup.groupUuid)
    backups = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)

    for backup in backups:
        if backup.type == "Root":
            continue
        old_volume_name = json.loads(backup.metadata)["name"]
        new_name = old_volume_name + "-from-" + backup.name.split("-")[1]
        new_volume_name = "data-volume-create-from-backup-" + backup.uuid
        cond = res_ops.gen_query_conditions("name", '=', new_volume_name)
        vol = res_ops.query_resource(res_ops.VOLUME, cond)[0]

        vol_ops.update_volume(vol.uuid, new_name, "change_name")

        new_volume = zstack_vol_header.ZstackTestVolume()
        new_volume.create_from(vol.uuid, new_vm)
        new_vm.test_volumes.append(new_volume)
        robot_test_obj.test_dict.add_volume(new_name, new_volume)
        md5sum = test_dict.get_backup_md5sum(backup.name + '-' + backup.volumeUuid)
        new_volume.set_md5sum(md5sum)

        snap_tree = robot_snapshot_header.ZstackSnapshotTree(new_volume)
        new_volume.snapshot_tree = snap_tree
        snap_tree.update()
        robot_test_obj.test_dict.add_snap_tree(new_name, snap_tree)
        new_volume.update()
        new_volume.update_volume()


def create_volume_backup(robot_test_obj, args):
    if len(args) < 2:
        test_util.test_fail("no resource available for next action: create volume backup")

    target_volume = robot_test_obj.get_test_dict().volume[args[0]]
    backup_name = args[1]

    zone_inv = res_ops.query_resource(res_ops.ZONE)[0]
    cond = res_ops.gen_query_conditions("attachedZoneUuids", "=", zone_inv.uuid)
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid

    backup_option = test_util.BackupOption()
    backup_option.set_name(backup_name)
    backup_option.set_volume_uuid(target_volume.get_volume().uuid)
    backup_option.set_backupStorage_uuid(bs_uuid)

    backup = vol_ops.create_backup(backup_option)

    robot_test_obj.test_dict.add_backup(backup_name, backup, target_volume)

    md5sum = target_volume.get_md5sum()
    robot_test_obj.test_dict.set_backup_md5sum(backup_name, md5sum)


def use_volume_backup(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: use volume backup")

    test_dict = robot_test_obj.get_test_dict()
    backup_dict = None
    for k, v in test_dict.backup.items():
        if args[0] in k:
            backup_dict = v
            d_backup_name = k

    target_backup = backup_dict['backup']

    backup = vol_ops.revert_volume_from_backup(target_backup.uuid)

    target_volume = backup_dict['volume']
    target_volume.update()
    target_volume.update_volume()

    md5sum = robot_test_obj.test_dict.get_backup_md5sum(d_backup_name)
    target_volume.set_md5sum(md5sum)
    target_volume.snapshot_tree.Newhead = True


def create_volume(robot_test_obj, args):
    # name systemTag size=random or number flag=[large,notCheck]
    large_flag = False
    volume_check_flag = True
    disksize = 2 * 1024 * 1024 * 1024
    ps_type = None

    if len(args) < 1:
        test_util.test_fail("no resource available for next action: create volume")
    target_volume_name = args[0]
    ps_uuid = robot_test_obj.get_default_config()['PS']
    systemtags = []
    if len(args) > 1 and args[1][0] == "=":
        tags = args[1].split('=')[1].split(',')
        if 'scsi' in tags:
            systemtags.append("capability::virtio-scsi")
        if 'shareable' in tags:
            systemtags.append("ephemeral::shareable")
        if 'thin' in tags:
            systemtags.append("volumeProvisioningStrategy::ThinProvisioning")
        if 'thick' in tags:
            systemtags.append("volumeProvisioningStrategy::ThickProvisioning")
        if 'ceph' in tags:
            ps_type = "Ceph"
        if 'sharedblock' in tags:
            ps_type = "SharedBlock"

    # parser args[3:] size flag
    # todo: add ps_type, offering_uuid, if loacl_ps appoint host will be better
    arg_dict = parser_args(args[1:])
    if "flag" in arg_dict:
        flag = arg_dict["flag"]
        if "large" in flag:
            large_flag = True
        if "nocheck" in flag:
            volume_check_flag = False
        if "scsi" in flag:
            systemtags.append("capability::virtio-scsi")
        if "shareable" in flag:
            systemtags.append("ephemeral::shareable")
        if "thin" in flag:
            systemtags.append("volumeProvisioningStrategy::ThinProvisioning")
        if "thick" in flag:
            systemtags.append("volumeProvisioningStrategy::ThickProvisioning")
        if 'ceph' in flag:
            ps_type = "Ceph"
        if 'sblk' in flag:
            ps_type = "SharedBlock"

    if "size" in arg_dict:
        if arg_dict["size"] == "random":
            if large_flag:
                disksize = random.choice([10, 50, 100, 200]) * 1024 * 1024 * 1024
            else:
                disksize = random.choice([1, 2, 3, 4]) * 1024 * 1024 * 1024
        else:
            disksize = arg_dict['size']

    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name(target_volume_name)
    volume_creation_option.set_primary_storage_uuid(ps_uuid)

    if ps_uuid:
        ps = test_lib.lib_get_primary_storage_by_uuid(ps_uuid)
        if ps.type in [inventory.LOCAL_STORAGE_TYPE or 'MiniStorage']:
            host_uuid = robot_test_obj.get_default_config()['HOST']
            systemtags.append("localStorage::hostUuid::%s" % (host_uuid))

    if ps_type:
        cond = res_ops.gen_query_conditions("type", "=", ps_type)
        pss = res_ops.gen_query_conditions(res_ops.PRIMARY_STORAGE, cond)
        if not pss:
            test_util.test_fail("there is no primarystorage type: [%s]" % ps_type)
        volume_creation_option.set_primary_storage_uuid(pss[0].uuid)

    if systemtags:
        volume_creation_option.set_system_tags(systemtags)
    if not MINI:
        new_volume = test_lib.lib_create_volume_from_offering(volume_creation_option)
    else:
        volume_creation_option.set_diskSize(disksize)
        volume_inv = vol_ops.create_volume_from_diskSize(volume_creation_option)
        new_volume = zstack_vol_header.ZstackTestVolume()
        new_volume.create_from(volume_inv.uuid)

    snap_tree = robot_snapshot_header.ZstackSnapshotTree(new_volume)
    snap_tree.update()
    new_volume.snapshot_tree = snap_tree
    robot_test_obj.test_dict.add_volume(target_volume_name, new_volume, volume_check_flag)
    robot_test_obj.test_dict.add_snap_tree(target_volume_name, snap_tree)


def create_scsi_volume():
    pass


def attach_volume(robot_test_obj, args):
    if len(args) != 2:
        test_util.test_fail("no resource available for next action: attach volume")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]
    target_volume = robot_test_obj.get_test_dict().volume[args[1]]

    root_volume = test_lib.lib_get_root_volume(target_vm.get_vm())
    ps = test_lib.lib_get_primary_storage_by_uuid(root_volume.primaryStorageUuid)
    if not test_lib.lib_check_vm_live_migration_cap(target_vm.vm) or ps.type == inventory.LOCAL_STORAGE_TYPE:
        ls_ref = test_lib.lib_get_local_storage_reference_information(target_volume.get_volume().uuid)
        if ls_ref:
            volume_host_uuid = ls_ref[0].hostUuid
            vm_host_uuid = test_lib.lib_get_vm_host(target_vm.vm).uuid
            if vm_host_uuid and volume_host_uuid != vm_host_uuid:
                test_util.test_logger('need to migrate volume: %s to host: %s, before attach it to vm: %s' % (
                    target_volume.get_volume().uuid, vm_host_uuid, target_vm.vm.uuid))
                target_volume.migrate(vm_host_uuid)

    target_volume.attach(target_vm)
    target_vm.test_volumes.append(target_volume)

    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()


def delete_volume(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: delete volume")

    target_volume = robot_test_obj.get_test_dict().volume[args[0]]

    if target_volume.get_volume().isShareable:
        for target_vm in target_volume.sharable_target_vms:
            target_vm.test_volumes.remove(target_volume)

    elif target_volume.get_volume().target_vm:
        target_volume.get_volume().target_vm.test_volumes.remove(target_volume)

    target_volume.delete()

    target_volume.update()
    target_volume.update_volume()
    target_volume.snapshot_tree.update()


def recover_volume(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: recover volume")

    target_volume = robot_test_obj.get_test_dict().volume[args[0]]

    target_volume.recover()

    target_volume.update()
    target_volume.update_volume()
    target_volume.snapshot_tree.update()


def detach_volume(robot_test_obj, args):
    if len(args) < 1:
        test_util.test_fail("no resource available for next action: detach volume")

    target_volume = robot_test_obj.get_test_dict().volume[args[0]]
    target_vm = robot_test_obj.get_test_dict().vm[args[1]] if len(args) == 2 else None

    if target_volume.get_volume().isShareable and not target_vm:
        test_util.test_fail("no resource available for next action: detach_share_volume")

    if not target_vm:
        target_vm = target_volume.target_vm

    target_volume.detach(target_vm.get_vm().uuid)
    target_vm.test_volumes.remove(target_volume)

    target_volume.update()
    target_volume.update_volume()

    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()


def expunge_volume(robot_test_obj, args):
    if len(args) < 1:
        test_util.test_fail("no resource available for next action: expunge volume")

    name = args[0]
    target_volume = robot_test_obj.get_test_dict().volume[name]
    target_volume.expunge()
    robot_test_obj.test_dict.remove_volume(target_volume)
    robot_test_obj.test_dict.remove_snap_tree(name)


def migrate_volume():
    pass


def resize_volume(robot_test_obj, args):
    if len(args) != 2:
        test_util.test_fail("no resource available for next action: reisze root volume")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]
    if args[1] == "random":
        delta = random.randint(10485760, 21474836480)
    else:
        delta = args[1]

    root_volume_uuid = test_lib.lib_get_root_volume(target_vm.get_vm()).uuid
    current_size = test_lib.lib_get_root_volume(target_vm.get_vm()).size
    new_size = current_size + int(delta)

    vol_ops.resize_volume(root_volume_uuid, new_size)

    target_volume = robot_test_obj.get_test_dict().volume[args[0] + '-root']
    target_vm.update()
    target_volume.update()
    target_volume.update_volume()


def resize_data_volume(robot_test_obj, args):
    if len(args) != 2:
        test_util.test_fail("no resource available for next action: reisze data volume")

    target_volume = robot_test_obj.get_test_dict().volume[args[0]]
    if args[1] == "random":
        delta = random.randint(10485760, 21474836480)
    else:
        delta = args[1]

    current_size = target_volume.get_volume().size
    new_size = current_size + int(delta)
    target_volume.resize(new_size)

    target_volume.update()
    target_volume.update_volume()


def create_data_vol_template_from_volume(robot_test_obj, args):
    if len(args) != 2:  # vol_name image_name
        test_util.test_fail("no resource available for next action: create data volume image")

    target_volume = robot_test_obj.get_test_dict().volume[args[0]]
    image_name = args[1]

    new_data_vol_temp = test_lib.lib_create_data_vol_template_from_volume(vm_target_vol=target_volume.get_volume())
    img_ops.update_image(new_data_vol_temp.get_image().uuid, image_name, None)

    robot_test_obj.get_test_dict().add_image(image_name, new_data_vol_temp)

    target_volume.update()
    target_volume.update_volume()


def create_root_vol_template_from_volume(robot_test_obj, args):
    if len(args) != 2:  # vm_name image_name
        test_util.test_fail("no resource available for next action: create root volume image")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]
    target_volume = robot_test_obj.get_test_dict().volume[target_vm.get_vm().name + '-root']
    image_name = args[1]

    new_root_vol_temp = test_lib.lib_create_root_vol_template_from_volume(target_volume.get_volume())
    img_ops.update_image(new_root_vol_temp.get_image().uuid, image_name, None)

    robot_test_obj.get_test_dict().add_image(image_name, new_root_vol_temp)

    target_volume.update()
    target_volume.update_volume()


def create_data_volume_from_image(robot_test_obj, args):
    systemtags = []
    if len(args) < 1:
        test_util.test_fail("no resource available for next action: create vm image")
    target_volume_name = args[0]
    if len(args) == 2:
        tags = args[1].split('=')[1].split(',')
        if 'scsi' in tags:
            systemtags.append("capability::virtio-scsi")
        if 'shareable' in tags:
            systemtags.append("ephemeral::shareable")
    cond = res_ops.gen_query_conditions('mediaType', '=', "DataVolumeTemplate")
    target_images = res_ops.query_resource(res_ops.IMAGE, cond)
    if not target_images:
        ps_uuid = robot_test_obj.get_default_config()['PS']

        image_option = test_util.ImageOption()
        image_option.set_format('qcow2')
        image_option.set_name('data_volume_image')
        bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
        bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, bs_cond)
        filtered_bss = []
        for bs in bss:
            ps_uuid_list = test_lib.lib_get_primary_storage_uuid_list_by_backup_storage(bs.uuid)
            if ps_uuid in ps_uuid_list:
                filtered_bss.append(bs)

        if not filtered_bss:
            test_util.test_fail("not find available backup storage. test fail")

        image_option.set_url(os.environ.get('emptyimageUrl'))
        image_option.set_backup_storage_uuid_list([filtered_bss[0].uuid])
        image_option.set_timeout(120000)
        image_option.set_mediaType("DataVolumeTemplate")
        image = img_ops.add_image(image_option)
        new_image = zstack_image_header.ZstackTestImage()
        new_image.set_creation_option(image_option)
        new_image.set_image(image)
        robot_test_obj.test_dict.add_image(new_image)
        target_images = [image]
    ps_uuid = robot_test_obj.get_default_config()['PS']
    ps = test_lib.lib_get_primary_storage_by_uuid(ps_uuid)
    host_uuid = None
    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        host_uuid = robot_test_obj.get_default_config()['HOST']
        systemtags.append("localStorage::hostUuid::%s" % (host_uuid))

    volume_inv = vol_ops.create_volume_from_template(target_images[0]['uuid'], ps_uuid, target_volume_name, host_uuid,
                                                     systemtags)
    new_volume = zstack_vol_header.ZstackTestVolume()
    new_volume.create_from(volume_inv.uuid, None)
    snap_tree = robot_snapshot_header.ZstackSnapshotTree(new_volume)
    snap_tree.update()
    new_volume.snapshot_tree = snap_tree
    robot_test_obj.test_dict.add_volume(target_volume_name, new_volume)
    robot_test_obj.test_dict.add_snap_tree(target_volume_name, snap_tree)


def create_image_from_volume(robot_test_obj, args):
    if len(args) != 2:  # vm_name  image_name
        test_util.test_fail("no resource available for next action: create vm image")

    target_vm = robot_test_obj.get_test_dict().vm[args[0]]
    image_name = args[1]

    new_image = test_lib.lib_create_template_from_volume(test_lib.lib_get_root_volume(target_vm.get_vm()).uuid)
    img_ops.update_image(new_image.get_image().uuid, image_name, None)

    robot_test_obj.test_dict.add_image(image_name, new_image)

    # Todo:update root snapshot tree
    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()


def delete_image(robot_test_obj, args):
    if len(args) < 1:
        test_util.test_fail("no resource available for next action: delete image")

    name = args[0]
    target_image = robot_test_obj.get_test_dict().image[name]
    target_image.delete()
    target_image.update()


def recover_image(robot_test_obj, args):
    if len(args) < 1:
        test_util.test_fail("no resource available for next action: delete image")

    name = args[0]
    target_image = robot_test_obj.get_test_dict().image[name]
    target_image.recover()
    target_image.update()


def expunge_image(robot_test_obj, args):
    if len(args) < 1:
        test_util.test_fail("no resource available for next action: expunge image")

    name = args[0]
    target_image = robot_test_obj.get_test_dict().image[name]
    target_image.expunge()
    robot_test_obj.test_dict.remove_image(target_image)


def create_data_template_from_backup():
    pass


def add_image(robot_test_obj, args):
    # name type url
    if len(args) < 3:
        test_util.test_fail("no resource available for next action: add image")
    image_name = args[0]
    _type = args[1]
    url = args[2]
    img_option = test_util.ImageOption()
    img_option.set_name(image_name)
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    img_option.set_backup_storage_uuid_list([bs.uuid for bs in bss])
    img_option.set_url(url)
    if _type == 'data':
        img_option.set_mediaType = 'DataVolumeTemplate'
        img_option.set_format('qcow2')
        image_inv = img_ops.add_add_data_volume_template(img_option)
        image = zstack_image_header.ZstackTestImage()
        image.set_image(image_inv)
        robot_test_obj.test_dict.add_image(image_name, image_obj=image)
        return image_inv
    if url.split(".")[-1] == 'iso':
        img_option.set_format('iso')
        img_option.set_mediaType = 'ISO'
        image_inv = img_ops.add_iso_template(img_option)
    else:
        img_option.set_format('qcow2')
        img_option.set_mediaType = 'RootVolumeTemplate'
        image_inv = img_ops.add_root_volume_template(img_option)
    image = zstack_image_header.ZstackTestImage()
    image.set_image(image_inv)
    robot_test_obj.test_dict.add_image(image_name, image_obj=image)
    return image_inv


def export_image():
    pass


def sync_image_from_imagestore():
    pass


def reconnect_bs():
    pass


def reclaim_space_from_bs():
    pass


def ps_migrate_volume(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: ps_migrate volume")
    target_volume = robot_test_obj.get_test_dict().volume[args[0]]
    old_ps_uuid = target_volume.primaryStorageUuid

    target_pss = datamigr_ops.get_ps_candidate_for_vol_migration(target_volume.get_volume().uuid)

    if not target_pss:
        test_util.test_fail("no resource available for next action: ps_migrate volume")

    datamigr_ops.ps_migrage_volume(target_pss[0].uuid, target_volume.get_volume().uuid)

    if 'root' in args[0]:
        vm_name = args[0].split('-')[0]
        test_vm = robot_test_obj.get_test_dict().vm[vm_name]
        test_vm.update()
    target_volume.update()
    target_volume.update_volume()
    target_volume.snapshot_tree.update(update_utility=True)

    ps_ops.clean_up_trash_on_primary_storage(old_ps_uuid)


def create_sg():
    pass


def delete_sg():
    pass


def sg_rule_operations():
    pass


def create_vip():
    pass


def delete_vip():
    pass


def vip_operations():
    pass


def create_volume_snapshot(robot_test_obj, args):
    if len(args) != 2:
        test_util.test_fail("no resource available for next action: create vm snapshot")

    target_volume = robot_test_obj.get_test_dict().volume[args[0]]
    snapshot_name = args[1]

    snapshot = target_volume.snapshot_tree.create_snapshot(snapshot_name)

    robot_test_obj.test_dict.add_snapshot(snapshot_name, snapshot)
    target_volume.update()
    target_volume.update_volume()
    md5sum = target_volume.get_md5sum()
    snapshot.set_md5sum(md5sum)


def delete_volume_snapshot(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: delete volume snapshot")

    target_snapshot_name = args[0]
    target_snapshot = robot_test_obj.get_test_dict().snapshot[target_snapshot_name]
    target_snapshot_tree = target_snapshot.snapshot_tree

    target_snapshot_tree.delete(target_snapshot)

    target_volume = target_snapshot_tree.target_volume
    target_volume.update()
    target_volume.update_volume()

    robot_test_obj.test_dict.remove_snapshot(target_snapshot)


def use_volume_snapshot(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: use volume snapshot")

    target_snapshot_name = args[0]
    target_snapshot = robot_test_obj.get_test_dict().snapshot[target_snapshot_name]
    target_snapshot_tree = target_snapshot.snapshot_tree

    target_snapshot_tree.use(target_snapshot)

    target_volume = target_snapshot_tree.target_volume
    target_volume.update()
    target_volume.update_volume()

    md5sum = target_snapshot.get_md5sum()
    target_volume.set_md5sum(md5sum)


def batch_delete_volume_snapshot(robot_test_obj, args, real=True):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: batch delete volume snapshot")

    target_snapshot_uuid_list = []
    snapshot_tree_list = {}

    for name in args[0]:
        target_snapshot = robot_test_obj.get_test_dict().snapshot[name]
        target_snapshot_uuid_list.append(target_snapshot.get_snapshot().uuid)

    if real:
        vol_ops.batch_delete_snapshot(target_snapshot_uuid_list)

    print args[0]
    for name in args[0]:
        target_snapshot = robot_test_obj.get_test_dict().snapshot[name]
        if not snapshot_tree_list.has_key(target_snapshot.snapshot_tree):
            snapshot_tree_list[target_snapshot.snapshot_tree] = []
        snapshot_tree_list[target_snapshot.snapshot_tree].append(target_snapshot)
    for snap_tree, snaps in snapshot_tree_list.items():
        snap_tree.batch_delete_snapshots(snaps)


def backup_volume_snapshot():
    pass


def delete_backup_volume_snapshot():
    pass


def create_volume_from_snapshot():
    pass


def create_image_from_snapshot():
    pass


def create_zone():
    pass


def delete_zone():
    pass


def delete_cluster():
    pass


def create_cluster():
    pass


def delete_l2():
    pass


def create_l2():
    pass


def detach_l2():
    pass


def attach_l2():
    pass


def create_l3():
    pass


def delete_l3():
    pass


def attach_iso():
    pass


def detach_iso():
    pass


def attach_primary_storage():
    pass


def detach_primary_storage():
    pass


def cleanup_ps_cache(robot_test_obj, args):
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    pss = res_ops.query_resource_fields(res_ops.PRIMARY_STORAGE, cond, None, ['uuid'])

    for ps in pss:
        ps_ops.cleanup_imagecache_on_primary_storage(ps.uuid)


def ps_migrate_vm(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: ps_migrate_vm")

    target_vm_name = args[0]
    target_vm = robot_test_obj.test_dict.vm[target_vm_name]
    old_ps_uuid = test_lib.lib_get_root_volume(target_vm.get_vm()).primaryStorageUuid

    target_pss = datamigr_ops.get_ps_candidate_for_vm_migration(target_vm.get_vm().uuid)

    if not target_pss:
        test_util.test_fail("no resource available for next action: ps_migrate_vm")

    datamigr_ops.ps_migrage_vm(target_pss[0].uuid, target_vm.get_vm().uuid, withDataVolumes=True, withSnapshots=True)

    target_vm.update()
    for volume in target_vm.test_volumes:
        volume.update()
        volume.update_volume()

    ps_ops.clean_up_trash_on_primary_storage(old_ps_uuid)


def create_mini_vm(robot_test_obj, args):
    name = args[0]
    cpu = 2
    memory = 2 * 1024 * 1024 * 1024
    l3_uuid = None
    large = False
    flag = None

    arg_dict = parser_args(args[1:])
    if 'flag' in arg_dict:
        flag = arg_dict['flag']
        if "large" in flag:
            large = True
    if 'cpu' in arg_dict:
        if arg_dict['cpu'] == 'random':
            if large:
                start, end = 16, 60
            else:
                start, end = 1, 16
            cpu = random.randrange(start, end, 1)
        else:
            cpu = int(arg_dict['cpu'])
    if 'memory' in arg_dict:
        if arg_dict['memory'] == 'random':
            if large:
                memory = random.randrange(4, 7, 1) * 1024 * 1024 * 1024
            else:
                memory = random.randrange(256, 4096, 256) * 1024 * 1024
        else:
            memory = int(arg_dict['memory']) * 1024 * 1024 * 1024
    if 'network' in arg_dict:
        if arg_dict['network'] == "random":
            cond = res_ops.gen_query_conditions("system", "=", "false")
            l3s = res_ops.query_resource(res_ops.L3_NETWORK, cond)
            l3_uuid = random.choice(l3s).uuid
        else:
            network_name = arg_dict["network"]
            cond = res_ops.gen_query_conditions("name", "=", network_name)
            l3 = res_ops.query_resource(res_ops.L3_NETWORK, cond)
            if not l3:
                test_util.test_fail("Network: %s does not exist" % network_name)
            else:
                l3_uuid = l3[0].uuid

    provisiong = 'Thin' if not arg_dict.has_key('provision') else arg_dict['provision']
    if flag and "thick" in flag:
        provisiong = "Thick"

    rootVolumeSystemTag = "volumeProvisioningStrategy::%sProvisioning" % provisiong

    cond = res_ops.gen_query_conditions('state', '=', "Enabled")
    cluster = res_ops.query_resource(res_ops.CLUSTER, cond)[0]
    robot_test_obj.default_config['MINI_CLUSTER'] = cluster.uuid

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if l3_uuid:
        vm_creation_option.set_l3_uuids([l3_uuid])
    else:
        l3_name = os.environ.get('l3VlanNetworkName1')
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_cluster_uuid(cluster.uuid)
    vm_creation_option.set_name(name)
    vm_creation_option.set_cpu_num(cpu)
    vm_creation_option.set_memory_size(int(memory))
    vm_creation_option.set_rootVolume_systemTags([rootVolumeSystemTag])
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    root_volume = zstack_vol_header.ZstackTestVolume()
    root_volume.create_from(vm.vm.allVolumes[0].uuid)
    vm.test_volumes.append(root_volume)
    root_snap_tree = robot_snapshot_header.ZstackSnapshotTree(root_volume)
    root_snap_tree.update()
    root_volume.snapshot_tree = root_snap_tree
    robot_test_obj.test_dict.add_vm(name, vm_obj=vm)
    robot_test_obj.test_dict.add_volume(name=vm.vm.name + "-root", vol_obj=root_volume)
    robot_test_obj.test_dict.add_snap_tree(name=vm.vm.name + "-root", snap_tree=root_snap_tree)
    robot_test_obj.default_config['PS'] = root_volume.get_volume().primaryStorageUuid
    robot_test_obj.default_config['HOST'] = vm.get_vm().hostUuid
    if arg_dict.has_key('data_volume') and arg_dict['data_volume'] == 'true':
        create_volume(robot_test_obj, ['auto-volume' + name[-1], 'flag=scsi,' + provisiong])
        attach_volume(robot_test_obj, [name, 'auto-volume' + name[-1]])


def create_mini_iso_vm(robot_test_obj, args):
    pass


def change_vm_ha(robot_test_obj, args):
    if len(args) < 1:
        test_util.test_fail("no resource available for next action: change vm ha")
    vm = robot_test_obj.get_test_dict().vm[args[0]]
    vm_uuid = vm.get_vm().uuid
    status = vm.get_vm().state
    test_util.test_logger("VM: %s State: %s" % (args[0], status))
    ha_inv = ha_ops.get_vm_instance_ha_level(vm_uuid)
    if ha_inv:
        ha_ops.del_vm_instance_ha_level(vm_uuid)
    else:
        ha_ops.set_vm_instance_ha_level(vm_uuid, "NeverStop")
        while status != 'Running':
            vm_inv = test_lib.lib_get_vm_by_uuid(vm_uuid)
            status = vm_inv.state
        vm.set_state('Running')
        test_util.test_logger("VM: %s State: %s" % (args[0], status))


def destroy_vm(robot_test_obj, args):
    if len(args) < 1:
        test_util.test_fail("no resource available for next action: destroy_vm")
    vm = robot_test_obj.get_test_dict().vm[args[0]]

    vm.destroy()
    vm.update()

    for volume in vm.test_volumes:
        volume.update()
        volume.update_volume()

    root_volume = robot_test_obj.get_test_dict().volume[args[0] + '-root']
    vm.test_volumes = [root_volume]


def recover_vm(robot_test_obj, args):
    if len(args) < 1:
        test_util.test_fail("no resource available for next action: recover_vm")
    vm = robot_test_obj.get_test_dict().vm[args[0]]
    vm.recover()
    vm.update()


def delete_volume_backup(robot_test_obj, args):
    if len(args) < 1:
        test_util.test_fail("no resource available for next action: delete_volume_backup")
    backup_name = args[0]
    backup_dict = None
    for k, v in robot_test_obj.get_test_dict().backup.items():
        if backup_name in k:
            backup_dict = v
            d_backup_name = k
    target_backup = backup_dict['backup']
    bs_uuids = [_bs.backupStorageUuid for _bs in target_backup.backupStorageRefs]
    vol_ops.delete_volume_backup(bs_uuids, target_backup.uuid)
    robot_test_obj.test_dict.remove_backup(target_backup)


def delete_vm_backup(robot_test_obj, args):
    group_uuids = []

    if len(args) < 1:
        test_util.test_fail("no resource available for next action: delete_vm_backup")
    backup_name = args[0]
    backup_dict = None
    for k, v in robot_test_obj.get_test_dict().backup.items():
        if backup_name in k:
            backup_dict = v
            d_backup_name = k
            target_backup = backup_dict['backup']
            group_uuids.append(target_backup.groupUuid)
            robot_test_obj.test_dict.remove_backup(target_backup)

    for group_uuid in list(set(group_uuids)):
        vol_ops.delete_vm_backup(group_uuid=group_uuid)


def create_vm_snapshot(robot_test_obj, args):
    if len(args) != 2:
        test_util.test_fail("no resource available for next action: create_vm_snapshot")

    vm_name = args[0]
    snapshot_name = args[1]
    vm = robot_test_obj.test_dict.vm[vm_name]

    root_volume = robot_test_obj.test_dict.volume[vm_name + "-root"]
    group = vol_ops.create_volume_snapshot_group(snapshot_name, root_volume.volume.uuid)
    for snap_ref in group.volumeSnapshotRefs:
        cond = res_ops.gen_query_conditions("uuid", "=", snap_ref.volumeSnapshotUuid)
        snapshot = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, cond)[0]
        if snapshot.volumeType == "Data":
            for volume in vm.test_volumes:
                if volume.get_volume().uuid == snapshot.volumeUuid:
                    volume_snap_name = volume.get_volume().name + "-" + snapshot_name.split("-")[1]
                    vol_ops.update_snapshot(snapshot.uuid, volume_snap_name, "change name")
                    volume.snapshot_tree.add_snapshot(snapshot.uuid)
                    robot_test_obj.test_dict.add_snapshot(volume_snap_name, volume.snapshot_tree.current_snapshot)
                    volume.snapshot_tree.current_snapshot.set_md5sum(volume.get_md5sum())
                    volume.update()
                    volume.update_volume()
        else:
            root_volume.snapshot_tree.add_snapshot(snapshot.uuid)
            robot_test_obj.test_dict.add_snapshot(snapshot_name, root_volume.snapshot_tree.current_snapshot)
            root_volume.update()
            root_volume.update_volume()


def use_vm_snapshot(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: use_vm_snapshot")

    vm_snap_name = args[0]

    root_snapshot = robot_test_obj.test_dict.snapshot[vm_snap_name]
    snapshot_num = vm_snap_name.split("-")[1]

    vol_ops.revert_vm_from_snapshot_group(root_snapshot.snapshot.groupUuid)

    for name,snapshot in robot_test_obj.test_dict.snapshot.items():
        if snapshot_num == name.split('-')[1]:
            if 'vm' in name:
                volume_name = name.split("-")[0] + "-root"
            else:
                volume_name = name.split("-")[0]
            volume = robot_test_obj.test_dict.volume[volume_name]
            volume.snapshot_tree.use(snapshot, real=False)
            volume.update()
            volume.update_volume()
            volume.set_md5sum(snapshot.get_md5sum())


def ungroup_vm_snapshot(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: ungroup_vm_snapshot")

    vm_snap_name = args[0]

    root_snapshot = robot_test_obj.test_dict.snapshot[vm_snap_name]
    vol_ops.ungroup_volume_snapshot_group(root_snapshot.snapshot.groupUuid)



def delete_vm_snapshot(robot_test_obj, args):
    if len(args) != 1:
        test_util.test_fail("no resource available for next action: delete_vm_snapshot")

    vm_snap_name = args[0]

    snapshot_num = vm_snap_name.split("-")[1]
    snapshot_name_list = []

    root_snapshot = robot_test_obj.test_dict.snapshot[vm_snap_name]
    vol_ops.delete_volume_snapshot_group(root_snapshot.snapshot.groupUuid)

    for name,snapshot in robot_test_obj.test_dict.snapshot.items():
        if snapshot_num == name.split("-")[1]:
            snapshot_name_list.append(name)

    batch_delete_volume_snapshot(robot_test_obj, [snapshot_name_list], real=False)



action_dict = {
    'change_global_config_sp_depth': change_global_config_sp_depth,
    'recover_global_config_sp_depth': recover_global_config_sp_depth,
    "cleanup_imagecache_on_ps": cleanup_imagecache_on_ps,
    'idel': idel,
    'create_vm': create_vm,
    'create_vm_by_image': create_vm_by_image,
    'stop_vm': stop_vm,
    'start_vm': start_vm,
    'suspend_vm': suspend_vm,
    'resume_vm': resume_vm,
    'reboot_vm': reboot_vm,
    'reboot_host': reboot_host,
    'run_workloads': run_workloads,
    'run_host_workloads': run_host_workloads,
    'destroy_vm': destroy_vm,
    'migrate_vm': migrate_vm,
    'expunge_vm': expunge_vm,
    'reinit_vm': reinit_vm,
    'clone_vm': clone_vm,
    #'clone_vm_with_volume': clone_vm_with_volume,
    'change_vm_image': change_vm_image,
    'create_vm_backup': create_vm_backup,
    'use_vm_backup': use_vm_backup,
    'create_volume_backup': create_volume_backup,
    'use_volume_backup': use_volume_backup,

    'create_vm_from_vmbackup': create_vm_from_vmbackup,

    'create_volume': create_volume,
    'create_scsi_volume': create_scsi_volume,
    'attach_volume': attach_volume,
    'delete_volume': delete_volume,
    'delete_vm_backup': delete_vm_backup,
    'detach_volume': detach_volume,
    'expunge_volume': expunge_volume,
    'migrate_volume': migrate_volume,
    'resize_volume': resize_volume,
    'resize_data_volume': resize_data_volume,

    'create_data_volume_template_from_volume': create_data_vol_template_from_volume,
    'create_data_volume_from_image': create_data_volume_from_image,
    'create_root_vol_template_from_volume': create_root_vol_template_from_volume,

    'create_image_from_volume': create_image_from_volume,
    'delete_image': delete_image,
    'expunge_image': expunge_image,
    'create_data_template_from_backup': create_data_template_from_backup,
    'add_image': add_image,
    'export_image': export_image,
    'sync_image_from_imagestore': sync_image_from_imagestore,

    'reconnect_bs': reconnect_bs,
    'reclaim_space_from_bs': reclaim_space_from_bs,

    'ps_migrate_vm': ps_migrate_vm,

    'create_security_group': create_sg,
    'delete_security_group': delete_sg,
    'security_group_rules_operations': sg_rule_operations,

    'create_vip': create_vip,
    'delete_vip': delete_vip,
    'vip_operations': vip_operations,

    'create_volume_snapshot': create_volume_snapshot,
    'delete_volume_snapshot': delete_volume_snapshot,
    'use_volume_snapshot': use_volume_snapshot,
    'batch_delete_volume_snapshot': batch_delete_volume_snapshot,
    'backup_volume_snapshot': backup_volume_snapshot,
    'delete_backup_volume_snapshot': delete_backup_volume_snapshot,
    'create_volume_from_snapshot': create_volume_from_snapshot,
    'create_image_from_snapshot': create_image_from_snapshot,

    'create_vm_snapshot': create_vm_snapshot,
    'delete_vm_snapshot': delete_vm_snapshot,
    'use_vm_snapshot': use_vm_snapshot,
    'ungroup_vm_snapshot': ungroup_vm_snapshot,

    'create_zone': create_zone,
    'delete_zone': delete_zone,

    'create_cluster': create_cluster,
    'delete_cluster': delete_cluster,

    'create_l2': create_l2,
    'delete_l2': delete_l2,
    'detach_l2_from_zone': detach_l2,
    'attach_l2_to_zone': attach_l2,

    'create_l3': create_l3,
    'delete_l3': delete_l3,

    'attach_iso': attach_iso,
    'detach_iso': detach_iso,

    'attach_primary_storage_to_cluster': attach_primary_storage,
    'detach_primary_storage_from_cluster': detach_primary_storage,

    'cleanup_ps_cache': cleanup_ps_cache,
    'ps_migrate_volume': ps_migrate_volume,

    'create_mini_vm': create_mini_vm,
    'create_mini_iso_vm': create_mini_iso_vm,
    'change_vm_ha': change_vm_ha,
    'delete_vm': delete_vm,
    'recover_vm': recover_vm,
    'recover_volume': recover_volume,
    'recover_image': recover_image,
    'delete_volume_backup': delete_volume_backup,

}


def robot_create_utility_vm():
    '''
            Create utility vm for all ps for robot testing
            we adandon this function to create utility vm
            by using volume.update() or snap_tree.update() to create utility vm
        '''
    cond = res_ops.gen_query_conditions('state', '=', "Enabled")
    cond = res_ops.gen_query_conditions('status', '=', "Connected", cond)
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    for ps in pss:
        utility_vm = None
        cond = res_ops.gen_query_conditions('name', '=', "utility_vm_for_robot_test")
        cond = res_ops.gen_query_conditions('state', '=', "Running", cond)
        vms = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
        for vm in vms:
            ps_uuid = test_lib.lib_get_root_volume(vm).primaryStorageUuid
            if ps_uuid == ps.uuid:
                utility_vm = vm
        if not utility_vm:
            utility_vm_image = None
            vm_create_option = test_util.VmOption()
            bs_uuids = test_lib.lib_get_backup_storage_uuid_list_by_zone(ps.zoneUuid)
            cond = res_ops.gen_query_conditions('name', '=', 'image_for_robot_test')
            cond = res_ops.gen_query_conditions('state', '=', "Enabled", cond)
            cond = res_ops.gen_query_conditions('status', '=', "Ready", cond)
            images = res_ops.query_resource(res_ops.IMAGE, cond)
            for bs_uuid in bs_uuids:
                temp_list = test_lib.lib_get_primary_storage_uuid_list_by_backup_storage(bs_uuid)
                if ps.uuid not in temp_list:
                    continue
                for image in images:
                    for bs_ref in image.backupStorageRefs:
                        if bs_ref.backupStorageUuid == bs_uuid:
                            utility_vm_image = image
                            break
            if not utility_vm_image:
                cond = res_ops.gen_query_conditions('name', '=', os.environ.get('imageName_net'))
                cond = res_ops.gen_query_conditions('state', '=', "Enabled", cond)
                cond = res_ops.gen_query_conditions('status', '=', "Ready", cond)
                images = res_ops.query_resource(res_ops.IMAGE, cond)
                for bs_uuid in bs_uuids:
                    temp_list = test_lib.lib_get_primary_storage_uuid_list_by_backup_storage(bs_uuid)
                    if ps.uuid not in temp_list:
                        continue
                    for image in images:
                        for bs_ref in image.backupStorageRefs:
                            if bs_ref.backupStorageUuid == bs_uuid:
                                utility_vm_image = image
                                break
            if not utility_vm_image:
                image_option = test_util.ImageOption()
                image_option.set_format('qcow2')
                image_option.set_url(os.environ.get('imageUrl_net'))
                image_option.set_name('image_for_robot_test')
                for bs_uuid in bs_uuids:
                    temp_list = test_lib.lib_get_primary_storage_uuid_list_by_backup_storage(bs_uuid)
                    if ps.uuid in temp_list:
                        target_bs_uuid = bs_uuid
                        break

                image_option.set_backup_storage_uuid_list([target_bs_uuid])
                image_option.set_timeout(7200000)
                image_option.set_mediaType("RootVolumeTemplate")
                import zstackwoodpecker.operations.image_operations as img_ops
                utility_vm_image = img_ops.add_image(image_option)

            utility_vm_create_option = test_util.VmOption()
            utility_vm_create_option.set_name('utility_vm_for_robot_test')
            utility_vm_create_option.set_image_uuid(utility_vm_image.uuid)
            utility_vm_create_option.set_ps_uuid(ps.uuid)
            if MINI:
                utility_vm_create_option.set_cpu_num(2)
                utility_vm_create_option.set_memory_size(int(2 * 1024 * 1024 * 1024))
            l3_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetworkName1')).uuid
            utility_vm_create_option.set_l3_uuids([l3_uuid])

            utility_vm = test_lib.lib_create_vm(utility_vm_create_option)
            # test_dict.add_utility_vm(utility_vm)
            if os.environ.get('ZSTACK_SIMULATOR') != "yes":
                utility_vm.check()
        else:
            import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
            utility_vm_uuid = utility_vm.uuid
            utility_vm = zstack_vm_header.ZstackTestVm()
            utility_vm.create_from(utility_vm_uuid)


def debug(robot_test_obj):
    '''
# vm: name uuid
#   volume: name uuid installPath
#     snapshot: name uuid installPath md5sum
#     backup: name uuid md5sum
#
...
    '''
    test_dict = robot_test_obj.get_test_dict()

    _str = 'Debug::\n'
    _str += " [Vm]:\n"
    for k, v in test_dict.vm.items():
        _str += "\t[name]: %s [uuid]: %s\n" % (k, v.get_vm().uuid)
    _str += " [Volume]:\n"
    for vol_name, test_volume in test_dict.volume.items():
        vol_inv = test_volume.get_volume()
        _str += "\t[name]: %s [uuid]: %s [installPath]: %s [md5sum]: %s\n" % (
            vol_inv.name, vol_inv.uuid, vol_inv.installPath, test_volume.get_md5sum())
        _str += "\t\t[Snapshot]:\n"
        for snap in test_volume.snapshot_tree.get_snapshot_list():
            _str += "\t\t\t[name]: %s [uuid]: %s [installPath]: %s [parent]: %s [md5sum]: %s\n" % (
                snap.snapshot.name, snap.snapshot.uuid, snap.snapshot.primaryStorageInstallPath, snap.parent,
                snap.md5sum
            )
        _str += "\t\t[Backup]:\n"
        for name, backup_dict in test_dict.backup.items():
            back_volume = backup_dict['volume']
            backup = backup_dict['backup']
            md5sum = backup_dict['md5']
            if back_volume == test_volume:
                _str += "\t\t\t[name]: %s [uuid] %s [md5sum]: %s\n" % (name, backup.uuid, md5sum)

    test_util.test_logger(_str)


def parser_args(args):
    arg_dict = {}
    for i in args:
        if "=" not in i or i[0] == "=":
            args.remove(i)
    for arg in args:
        arg_dict[arg.split('=')[0]] = arg.split('=')[1]
    return arg_dict
