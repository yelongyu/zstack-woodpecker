#!/usr/bin/python
import os
import optparse

import test_lib
import test_util
import test_state
#import zstackwoodpecker.test_lib as test_lib
#import zstackwoodpecker.test_util as test_util
#import zstackwoodpecker.test_state as test_state

ACTION = 'Robot Action:'
ACTION_RESULT = 'Robot Action Result:'
VM = 'VM'
VOLUME = 'Volume'
SG = 'SG'
VIP = 'VIP'
EIP = 'EIP'
NIC = 'Nic'
ROOT_VOLUME = 'Root Volume'
IMAGE = 'Image'
RV_IMAGE = 'RootVolume Image'
DV_IMAGE = 'DataVolume Image'
RULE = 'Rule'
SP = 'SP'
PF = 'PF'

TA = test_state.TestAction

class ObjMap(object):
    def __init__(self):
        self.obj_map = {
                VM: {},
                VOLUME: {},
                SG: {},
                VIP: {},
                EIP: {},
                NIC: {},
                ROOT_VOLUME: {},
                IMAGE: {},
                RV_IMAGE: {},
                DV_IMAGE: {},
                SP: {},
                PF: {},
                RULE: {}}

        self.all_map = {}

    def add_map(self, uuid, obj):
        self.all_map[uuid] = obj

    def get_map(self, uuid):
        if self.all_map.has_key(uuid):
            return self.all_map[uuid]

class ActionParser(object):
    def __init__(self, action_line):
        self.action_line = action_line
        self.action = {ACTION: None,
                VM: None,
                VOLUME: None,
                SG: None,
                VIP: None,
                EIP: None,
                NIC: None,
                ROOT_VOLUME: None,
                IMAGE: None,
                RV_IMAGE: None,
                DV_IMAGE: None,
                SP: None,
                PF: None,
                RULE: None}

        self.action_result = {ACTION_RESULT: None,
                VM: None,
                VOLUME: None,
                SG: None,
                VIP: None,
                EIP: None,
                NIC: None,
                ROOT_VOLUME: None,
                IMAGE: None,
                PF: None,
                RV_IMAGE: None,
                DV_IMAGE: None,
                SP: None,
                RULE: None}

        self.new_obj = None
        self.parse()
    
    def parse(self):
        fields = self.action_line.split(';')
        for field in fields:
            field = field.strip().lower()
            if self.action_line.startswith(ACTION):
                for key in self.action.keys():
                    if key == ACTION or key == ACTION_RESULT:
                        new_key = key
                    else:
                        new_key = 'on %s:' % key

                    new_key = new_key.lower()
    
                    if field.startswith(new_key):
                        self.action[key] = field.split(new_key)[1].strip()
                        break
                else:
                    raise test_util.TestError('Does not recognize field in action: %s' % field)

            elif self.action_line.startswith(ACTION_RESULT):
                for key in self.action_result.keys():
                    if key == ACTION or key == ACTION_RESULT:
                        new_key = key
                    else:
                        new_key = 'new %s:' % key
                        new_key2 = 'on %s:' % key

                    new_key = new_key.lower()
                    new_key2 = new_key2.lower()
    
                    if field.startswith(new_key):
                        self.action_result[key] = field.split(new_key)[1].strip()
                        if key != ACTION_RESULT:
                            self.new_obj = self.action_result[key]
                        break

                    if field.startswith(new_key2):
                        self.action_result[key] = field.split(new_key2)[1].strip()
                        break
                else:
                    raise test_util.TestError('Does not recognize field in action result: %s' % field)

    def get_action(self):
        return self.action

    def get_action_result(self):
        return self.action_result

    def get_new_obj(self):
        return self.new_obj

class Robot(object):
    '''
    robot action file could be get by:
    grep 'Robot Action' robot_test_case_log_file > robot_action_file
    '''
    def __init__(self, options):
        self.robot_action_file = options.robot_action_file
        if not os.path.exists(self.robot_action_file):
            raise test_util.TestError('Robot Action File: %s does not exit' \
                    % self.robot_action_file)

        new_robot_action_file = '/tmp/zstack_robot_action_for_replay.log'
        os.system("grep 'Robot Action' %s > %s" % (self.robot_action_file, new_robot_action_file))
        self.robot_action_file = new_robot_action_file

        self.test_obj_dict = test_state.TestStateDict()
        self.obj_map = ObjMap()
        self.latest_obj = None
        self.robot_test_obj = test_util.Robot_Test_Object()

        #self.parse_action_log()

    def run(self):
        #TODO: judge action file size
        action_lines = open(self.robot_action_file, 'r').readlines()
        line_num = 0
        for action_line in action_lines:
            line_num += 1
            action_line = action_line.strip()
            if 'idel' in action_line:
                continue

            if action_line.startswith(ACTION):
                action_obj = ActionParser(action_line)
                action = action_obj.get_action()[ACTION]
                print "action: %s in line: %d" % (action, line_num)
                if action == TA.create_vm:
                    vm = test_lib.lib_create_vm()
                    self.latest_obj = vm
                    self.test_obj_dict.add_vm(vm)

                elif action == TA.stop_vm:
                    robot_vm_uuid = action_obj.get_action()[VM]
                    vm_obj = self.obj_map.get_map(robot_vm_uuid)
                    vm_obj.stop()
                    
                elif action == TA.start_vm:
                    robot_vm_uuid = action_obj.get_action()[VM]
                    vm_obj = self.obj_map.get_map(robot_vm_uuid)
                    vm_obj.start()
                    
                elif action == TA.reboot_vm:
                    robot_vm_uuid = action_obj.get_action()[VM]
                    vm_obj = self.obj_map.get_map(robot_vm_uuid)
                    vm_obj.reboot()

                elif action == TA.destroy_vm:
                    robot_vm_uuid = action_obj.get_action()[VM]
                    vm_obj = self.obj_map.get_map(robot_vm_uuid)
                    vm_obj.destroy()
                    self.test_obj_dict.rm_vm(vm_obj)

                elif action == TA.create_volume:
                    volume = test_lib.lib_create_volume_from_offering()
                    self.latest_obj = volume
                    self.test_obj_dict.add_volume(volume)

                elif action == TA.create_image_from_volume:
                    robot_vm_uuid = action_obj.get_action()[VM]
                    vm_obj = self.obj_map.get_map(robot_vm_uuid)
                    vm_root_vol_uuid = test_lib.lib_get_root_volume(vm_obj.get_vm()).uuid
                    new_image = test_lib.lib_create_template_from_volume(vm_root_vol_uuid)
                    self.test_obj_dict.add_image(new_image)
                    self.latest_obj = new_image

                elif action == TA.create_data_vol_template_from_volume:
                    robot_vm_uuid = action_obj.get_action()[VM]
                    vm_obj = self.obj_map.get_map(robot_vm_uuid)
                    robot_volume_uuid = action_obj.get_action()[VOLUME]
                    volume_obj =  self.obj_map.get_map(robot_volume_uuid)
                    if not volume_obj:
                        volume = test_lib.lib_get_root_volume(vm_obj.get_vm())
                    else:
                        volume = volume_obj.get_volume()

                    new_data_vol_temp = test_lib.lib_create_data_vol_template_from_volume(vm_obj, volume)
                    self.test_obj_dict.add_image(new_data_vol_temp)
                    self.latest_obj = new_data_vol_temp

                elif action == TA.delete_image:
                    robot_uuid = action_obj.get_action()[IMAGE]
                    obj = self.obj_map.get_map(robot_uuid)
                    obj.delete()
                    self.test_obj_dict.rm_image(obj)

                elif action == TA.attach_volume:
                    robot_vm_uuid = action_obj.get_action()[VM]
                    vm_obj = self.obj_map.get_map(robot_vm_uuid)
                    robot_volume_uuid = action_obj.get_action()[VOLUME]
                    volume_obj =  self.obj_map.get_map(robot_volume_uuid)
                    volume_obj.attach(vm_obj)

                elif action == TA.detach_volume:
                    robot_volume_uuid = action_obj.get_action()[VOLUME]
                    volume_obj =  self.obj_map.get_map(robot_volume_uuid)
                    volume_obj.detach()

                elif action == TA.delete_volume:
                    robot_volume_uuid = action_obj.get_action()[VOLUME]
                    volume_obj =  self.obj_map.get_map(robot_volume_uuid)
                    volume_obj.delete()
                    self.test_obj_dict.rm_volume(volume_obj)

                elif action == TA.create_data_volume_from_image:
                    robot_image_uuid = action_obj.get_action()[IMAGE]
                    image_obj = self.obj_map.get_map(robot_image_uuid)
                    volume_obj = test_lib.lib_create_data_volume_from_image(image_obj)
                    self.latest_obj = volume_obj
                    self.test_obj_dict.add_volume(volume_obj)

                elif action == TA.create_volume_snapshot:
                    robot_vm_uuid = action_obj.get_action()[VM]
                    if robot_vm_uuid:
                        #root volume
                        vm_obj = self.obj_map.get_map(robot_vm_uuid)
                        vm_root_vol_uuid = test_lib.lib_get_root_volume(vm_obj.get_vm()).uuid
                        target_volume_snapshots = self.test_obj_dict.get_volume_snapshot(vm_root_vol_uuid)
                    else:
                        robot_volume_uuid = action_obj.get_action()[VOLUME]
                        volume_obj = self.obj_map.get_map(robot_volume_uuid)
                        target_volume_snapshots = self.test_obj_dict.get_volume_snapshot(volume_obj.get_volume().uuid)
                    new_snapshot = test_lib.lib_create_volume_snapshot_from_volume(target_volume_snapshots, self.robot_test_obj, self.test_obj_dict)
                    self.latest_obj = new_snapshot

                elif action == TA.create_volume_from_snapshot:
                    robot_snapshot_uuid = action_obj.get_action()[SP]
                    snapshot_obj = self.obj_map.get_map(robot_snapshot_uuid)
                    new_volume_obj = snapshot_obj.create_data_volume()
                    self.test_obj_dict.add_volume(new_volume_obj)
                    self.latest_obj = new_volume_obj

                elif action == TA.use_volume_snapshot:
                    robot_snapshot_uuid = action_obj.get_action()[SP]
                    snapshot_obj = self.obj_map.get_map(robot_snapshot_uuid)
                    robot_volume_uuid = action_obj.get_action()[VOLUME]
                    target_volume_snapshots = self.test_obj_dict.get_volume_snapshot(robot_volume_uuid)
                    target_volume_snapshots.use_snapshot(snapshot_obj)

                elif action == TA.create_image_from_snapshot:
                    robot_snapshot_uuid = action_obj.get_action()[SP]
                    snapshot_obj = self.obj_map.get_map(robot_snapshot_uuid)
                    new_image_obj = test_lib.lib_create_image_from_snapshot(snapshot_obj)
                    self.test_obj_dict.add_image(new_image_obj)
                    self.latest_obj = new_image_obj

                elif action == TA.delete_volume_snapshot:
                    robot_snapshot_uuid = action_obj.get_action()[SP]
                    snapshot_obj = self.obj_map.get_map(robot_snapshot_uuid)
                    robot_volume_uuid = action_obj.get_action()[VOLUME]
                    target_volume_snapshots = self.test_obj_dict.get_volume_snapshot(robot_volume_uuid)
                    target_volume_snapshots.delete_snapshot(snapshot_obj)

                elif action == TA.backup_volume_snapshot:
                    robot_snapshot_uuid = action_obj.get_action()[SP]
                    snapshot_obj = self.obj_map.get_map(robot_snapshot_uuid)
                    robot_volume_uuid = action_obj.get_action()[VOLUME]
                    target_volume_snapshots = self.test_obj_dict.get_volume_snapshot(robot_volume_uuid)
                    target_volume_snapshots.backup_snapshot(snapshot_obj)

                elif action == TA.delete_backup_volume_snapshot:
                    robot_snapshot_uuid = action_obj.get_action()[SP]
                    snapshot_obj = self.obj_map.get_map(robot_snapshot_uuid)
                    robot_volume_uuid = action_obj.get_action()[VOLUME]
                    target_volume_snapshots = self.test_obj_dict.get_volume_snapshot(robot_volume_uuid)
                    target_volume_snapshots.delete_backuped_snapshot(snapshot_obj)

                else:
                    print "skip action: %s in line: %d" % (action, line_num)

            elif action_line.startswith(ACTION_RESULT):
                action = action_line.split(';')[0].split(':')[1]
                action_obj = ActionParser(action_line)
                self.obj_map.add_map(action_obj.get_new_obj(), self.latest_obj)
                self.latest_obj = None


def main():
    parser = optparse.OptionParser()

    parser.add_option(
            "-f", 
            dest="robot_action_file", 
            action='store', 
            help="Robot Action File Log")

    (options, args) = parser.parse_args()
    robot = Robot(options)
    robot.run()

if __name__ == '__main__':
    main()
