'''

Define Test State. The state will be used for generating possible test action.
It is mainly for robot testing. The state will also be used for test case
automation cleanup. 

@author: Youyk
'''
import apibinding.inventory as inventory
import random
import test_util
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.volume as volume_header
import zstackwoodpecker.header.image as image_header
import zstackwoodpecker.header.vip as vip_header
import zstackwoodpecker.header.eip as eip_header
import zstackwoodpecker.header.port_forwarding as pf_header
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops

import zstacklib.utils.list_ops as list_ops
#Define general test actions
class TestAction(object):
    '''
        Possible test Actions defination.
    '''
    #actions
    change_global_config_sp_depth = 'change_global_config_sp_depth'
    recover_global_config_sp_depth = 'recover_global_config_sp_depth'
    cleanup_imagecache_on_ps = "cleanup_imagecache_on_ps"
    idel = 'idel'
    create_vm = 'create_vm'
    create_vm_by_image = 'create_vm_by_image'
    stop_vm = 'stop_vm'
    start_vm = 'start_vm'
    suspend_vm = 'suspend_vm'
    resume_vm = 'resume_vm'
    reboot_vm = 'reboot_vm'
    destroy_vm = 'destroy_vm'
    migrate_vm = 'migrate_vm'
    expunge_vm = 'expunge_vm'
    reinit_vm = 'reinit_vm'
    clone_vm = 'clone_vm'
    change_vm_image = 'change_vm_image'
    create_vm_backup = 'create_vm_backup'
    use_vm_backup = 'use_vm_backup'
    recover_volume_backup_from_remote = 'recover_volume_backup_from_remote'
    sync_backup_to_remote = 'sync_backup_to_remote'
    create_volume_backup = 'create_volume_backup'
    use_volume_backup = 'use_volume_backup'
    create_vm_from_vmbackup = 'create_vm_from_vmbackup'
    create_volume = 'create_volume'
    create_scsi_volume = 'create_scsi_volume'
    attach_volume = 'attach_volume'
    delete_volume = 'delete_volume'
    detach_volume = 'detach_volume'
    expunge_volume = 'expunge_volume'
    migrate_volume = 'migrate_volume'
    resize_volume = 'resize_volume'
    resize_data_volume = 'resize_data_volume'

    create_data_vol_template_from_volume = \
            'create_data_volume_template_from_volume'
    create_data_volume_from_image = 'create_data_volume_from_image'

    create_image_from_volume = 'create_image_from_volume'
    delete_image = 'delete_image'
    expunge_image = 'expunge_image'
    create_data_template_from_backup = 'create_data_template_from_backup'
    add_image = 'add_image'
    export_image = 'export_image'
    sync_image_from_imagestore = 'sync_image_from_imagestore'

    reconnect_bs = 'reconnect_bs'
    reclaim_space_from_bs = 'reclaim_space_from_bs'

    ps_migrage_vm = 'ps_migrage_vm'

    create_sg = 'create_security_group'
    delete_sg = 'delete_security_group'
    sg_rule_operations = 'security_group_rules_operations'

    create_vip = 'create_vip'
    delete_vip = 'delete_vip'
    vip_operations = 'vip_operations'

    create_volume_snapshot = 'create_volume_snapshot'
    delete_volume_snapshot = 'delete_volume_snapshot'
    use_volume_snapshot = 'use_volume_snapshot'
    batch_delete_volume_snapshot = 'batch_delete_volume_snapshot'
    backup_volume_snapshot = 'backup_volume_snapshot'
    delete_backup_volume_snapshot = 'delete_backup_volume_snapshot'
    create_volume_from_snapshot = 'create_volume_from_snapshot'
    create_image_from_snapshot = 'create_image_from_snapshot'

    create_zone = 'create_zone'
    delete_zone = 'delete_zone'

    create_cluster = 'create_cluster'
    delete_cluster = 'delete_cluster'

    create_l2 = 'create_l2'
    delete_l2 = 'delete_l2'
    detach_l2 = 'detach_l2_from_zone'
    attach_l2 = 'attach_l2_to_zone'

    create_l3 = 'create_l3'
    delete_l3 = 'delete_l3'

    attach_iso = 'attach_iso'
    detach_iso = 'detach_iso'

    attach_primary_storage = 'attach_primary_storage_to_cluster'
    detach_primary_storage = 'detach_primary_storage_from_cluster'    

    cleanup_ps_cache = 'cleanup_ps_cache'
    ps_migrate_volume = 'ps_migrate_volume'

    vm_actions = [create_vm, stop_vm, start_vm, reboot_vm, destroy_vm, \
            migrate_vm, expunge_vm]

    volume_actions = [create_scsi_volume, create_volume, attach_volume, delete_volume, \
            detach_volume, create_data_vol_template_from_volume, expunge_volume]

    image_actions = [create_image_from_volume, delete_image, \
            create_data_volume_from_image, expunge_image]

    sg_actions = [create_sg, delete_sg, sg_rule_operations]
    vip_actions = [create_vip, delete_vip, vip_operations]

    snapshot_actions = [create_volume_snapshot, delete_volume_snapshot, \
            use_volume_snapshot, backup_volume_snapshot, \
            delete_backup_volume_snapshot, create_volume_from_snapshot, \
            create_image_from_snapshot]

    resource_actions = [ create_zone, delete_zone, create_cluster, \
            delete_cluster, create_l2, delete_l2, detach_l2, attach_l2, \
            create_l3, delete_l3, attach_primary_storage, \
            detach_primary_storage ]

class TestStage(object):
    '''
        Test states definition and Test state transition matrix. 
    '''
    def __init__(self):
        self.vm_current_state = 0
        self.vm_volume_current_state = 0
        self.volume_current_state = 0
        self.image_current_state = 0
        self.vm_live_migration_cap = 0
        self.volume_migration_cap = 0
        self.sg_current_state = 0
        self.vip_current_state = 0
        self.sp_current_state = 0
        self.snapshot_live_cap = 0
        self.vm_live_template_cap = 0
        #the volume snapshot target VM might be not the VM testing picks up.
        #so we need to define a new VM state, which is for volume snapshot. 
        self.volume_vm_current_state = 0 

    #states
    vm_state = 'vm_state'
    vm_volume_state = 'vm_volume_state'
    volume_state = 'volume_state'
    image_state = 'image_state'
    sg_state = 'sg_state'
    vip_state = 'vip_state'
    sp_state = 'sp_state'
    sp_live_cap = 'sp_live_cap'
    vm_live_sp_cap = 'vm_live_sp_cap'
    volume_vm_state = 'volume_vm_state'

    Any = 'Any'
    #vm volume state
    vm_no_volume_att = 'vm_no_volume_attached_to_vm'
    vm_volume_att_not_full = 'vm_has_free_volume_slot_to_be_attached'
    vm_volume_att_full = 'vm_all_volume_slots_are_attached'
    #all volumes state
    free_volume = 'has_free_volume'
    no_free_volume = 'no_free_volume'
    deleted_volume = 'deleted_volume'

    new_template_image = 'new_created_template_image'
    no_new_template_image = 'no_new_created_template_image'
    deleted_image = 'deleted_image'

    vm_live_migration = 'support_vm_live_migration'
    no_vm_live_migration = 'no_support_vm_live_migration'

    template_live_creation = 'template_supports_live_creation'
    template_no_live_creation = 'template_does_not_support_live_creation'

    volume_migration = 'support_volume_migration'
    no_volume_migration = 'no_support_volume_migration'

    no_sg = 'no_security_group'
    has_sg = 'has_defined_security_group'

    no_vip_res = 'no_vip_resource'
    no_more_vip_res = 'has_free_or_used_vip_but_can_not_create_more_vip'
    has_vip = 'has_free_or_used_vip'
    no_vip = 'no_created_vip_but_system_has_vip_resource'

    no_volume_file = 'volume_is_not_attached_after_creation'
    data_snapshot_in_ps = 'data_snapshot_in_ps'
    data_snapshot_in_bs = 'data_snapshot_in_bs'
    data_snapshot_in_both_ps_bs = 'data_snapshot_in_both_ps_bs'
    root_snapshot_in_ps = 'root_snapshot_in_ps'
    root_snapshot_in_bs = 'root_snapshot_in_bs'
    root_snapshot_in_both_ps_bs = 'root_snapshot_in_both_ps_bs'
    no_snapshot = 'volume_does_not_have_snapshot'

    snapshot_live_creation = 'snapshot_supports_live_creation'
    snapshot_no_live_creation = 'snapshot_does_not_support_live_creation'

    vm_state_dict = {
            Any: 1 , 
            vm_header.RUNNING: 2, 
            vm_header.STOPPED: 3, 
            vm_header.DESTROYED: 4,
            vm_header.EXPUNGED: 5
            }

    vm_volume_state_dict = {
            Any: 10, 
            vm_no_volume_att: 20, 
            vm_volume_att_not_full: 30, 
            vm_volume_att_full: 40 
            }

    volume_state_dict = {
            Any: 100, 
            free_volume: 200, 
            no_free_volume: 300,
            deleted_volume: 400
            }

    image_state_dict = {
            Any: 1000, 
            no_new_template_image: 2000, 
            new_template_image: 3000,
            deleted_image: 4000
            }

    #If primary storage is local storage and hypervisor is kvm, vm live 
    # migration is not allowed, otherwise vm might break disk. 
    vm_live_migration_cap_dict = {
            Any: 10000,
            vm_live_migration: 20000,
            no_vm_live_migration: 30000
            }

    volume_migration_cap_dict = {
            Any: 100000,
            volume_migration: 200000,
            no_volume_migration: 300000
            }

    vm_live_template_cap_dict = {
            Any: 1000000,
            template_live_creation: 2000000,
            template_no_live_creation: 3000000
            }

    snapshot_state_dict = {
            Any: 10,
            data_snapshot_in_ps: 20,
            data_snapshot_in_bs: 30,
            data_snapshot_in_both_ps_bs: 40,
            root_snapshot_in_ps: 50,
            root_snapshot_in_bs: 60,
            root_snapshot_in_both_ps_bs: 70,
            no_snapshot: 80,
            no_volume_file: 90
            }

    #If Hypervisor support create snapshot when VM is running
    snapshot_live_cap_dict = {
            Any: 100,
            snapshot_live_creation: 200,
            snapshot_no_live_creation: 300
            }
    #any_any = vm_state_dict[Any] + vm_volume_state_dict[Any] + volume_state_dict[Any] + image_state_dict[Any] + sg_state_dict[Any]

    ta = TestAction

    #state transition table for vm_state, volume_state and image_state
    normal_action_transition_table = {
        Any: [ta.create_vm, ta.create_scsi_volume, ta.create_volume, ta.idel], 
    20002: [ta.stop_vm, ta.reboot_vm, ta.destroy_vm, ta.migrate_vm],
    30002: [ta.stop_vm, ta.reboot_vm, ta.destroy_vm],
    20003: [ta.start_vm, ta.destroy_vm, ta.create_data_vol_template_from_volume], 
    30023: [ta.start_vm, ta.destroy_vm, ta.create_data_vol_template_from_volume, ta.migrate_volume], 
  2000002: [ta.create_image_from_volume],
  2000003: [ta.create_image_from_volume],
  3000003: [ta.create_image_from_volume],
        4: [ta.expunge_vm],
        5: [],
      211: [ta.delete_volume], 
      222: [ta.attach_volume, ta.delete_volume],
      223: [ta.attach_volume, ta.delete_volume], 
      224: [ta.delete_volume],
      232: [ta.attach_volume, ta.detach_volume, ta.delete_volume],
      233: [ta.attach_volume, ta.detach_volume, ta.delete_volume],
      234: [ta.delete_volume], 
      244: [ta.delete_volume], 
      321: [],
      332: [ta.detach_volume, ta.delete_volume], 
      333: [ta.detach_volume, ta.delete_volume], 
      334: [],
      342: [ta.detach_volume, ta.delete_volume], 
      343: [ta.detach_volume, ta.delete_volume], 
      344: [],
      400: [ta.expunge_volume],
     3000: [ta.delete_image, ta.create_data_volume_from_image],
     4000: [ta.expunge_image]
    }

    #snapshot state transition table
    #define some general actions. 
    #data volume actions
    #vm running
    d_sp_in_ps_action1 = [ta.backup_volume_snapshot,\
            ta.create_volume_from_snapshot]
    d_sp_in_bs_action1 = [ta.create_volume_from_snapshot, \
            ta.delete_backup_volume_snapshot]
    d_sp_in_both_ps_bs_action1 = [ta.create_volume_from_snapshot, \
            ta.delete_backup_volume_snapshot]

    #vm stopped
    d_sp_in_ps_action2 = list(d_sp_in_ps_action1)
    d_sp_in_ps_action2.extend([ta.create_volume_snapshot, \
            ta.delete_volume_snapshot, ta.use_volume_snapshot])
    #FIXME: if snapshot is only in backup storage, it means its volume and 
    # primary storage is deleted. This might be changed, if ZStack add new 
    # primary storage snapshot delete API. 
    #FIXME: add volume state to snapshot state dict, when snapshots are only in
    # backup storage. 
    #d_sp_in_bs_action2 = list(d_sp_in_bs_action1)
    #d_sp_in_bs_action2.append(ta.use_volume_snapshot)
    d_sp_in_bs_action2 = list(d_sp_in_bs_action1)
    d_sp_in_bs_action2.append(ta.delete_volume_snapshot) 
    d_sp_in_both_ps_bs_action2 = list(d_sp_in_both_ps_bs_action1)
    d_sp_in_both_ps_bs_action2.extend([ta.create_volume_snapshot, \
            ta.delete_volume_snapshot, \
            ta.use_volume_snapshot])

    #vm running when hv supports living vm snapshot creating
    d_sp_in_ps_action3 = list(d_sp_in_ps_action1)
    d_sp_in_ps_action3.extend([ta.delete_volume_snapshot, \
            ta.create_volume_snapshot])
    # FIXME: as above.
    #d_sp_in_bs_action3 = list(d_sp_in_bs_action1)
    #d_sp_in_bs_action3.append(ta.create_volume_snapshot)
    d_sp_in_bs_action3 = list(d_sp_in_bs_action1)
    d_sp_in_bs_action3.append(ta.delete_volume_snapshot)
    d_sp_in_both_ps_bs_action3 = list(d_sp_in_both_ps_bs_action1)
    d_sp_in_both_ps_bs_action3.extend([ta.delete_volume_snapshot, \
            ta.create_volume_snapshot])

    #root volume actions
    #vm running
    r_sp_in_ps_action1 = [ta.backup_volume_snapshot,\
            ta.create_volume_from_snapshot, ta.create_image_from_snapshot]

    r_sp_in_bs_action1 = [ta.create_volume_from_snapshot, \
            ta.create_image_from_snapshot,\
            ta.delete_backup_volume_snapshot]

    r_sp_in_both_ps_bs_action1 = [ta.create_volume_from_snapshot, \
            ta.create_image_from_snapshot,\
            ta.delete_backup_volume_snapshot]

    #vm stopped
    r_sp_in_ps_action2 = list(r_sp_in_ps_action1)
    r_sp_in_ps_action2.extend([ta.create_volume_snapshot, \
            ta.delete_volume_snapshot, ta.use_volume_snapshot])
    # FIXME: as above.
    #r_sp_in_bs_action2 = list(r_sp_in_bs_action1)
    #r_sp_in_bs_action2.append(ta.use_volume_snapshot)
    r_sp_in_bs_action2 = list(r_sp_in_bs_action1)
    r_sp_in_bs_action2.append(ta.delete_volume_snapshot)
    r_sp_in_both_ps_bs_action2 = list(r_sp_in_both_ps_bs_action1)
    r_sp_in_both_ps_bs_action2.extend([ta.create_volume_snapshot, \
            ta.delete_volume_snapshot, ta.use_volume_snapshot])

    #vm running when hv supports living vm snapshot creating
    r_sp_in_ps_action3 = list(r_sp_in_ps_action1)
    r_sp_in_ps_action3.extend([ta.create_volume_snapshot, \
            ta.delete_volume_snapshot])
    # FIXME: as above.
    #r_sp_in_bs_action3 = list(r_sp_in_bs_action1)
    #r_sp_in_bs_action3.append(ta.create_volume_snapshot)
    r_sp_in_bs_action3 = list(r_sp_in_bs_action1)
    r_sp_in_bs_action3.append(ta.delete_volume_snapshot)
    r_sp_in_both_ps_bs_action3 = list(r_sp_in_both_ps_bs_action1)
    r_sp_in_both_ps_bs_action3.extend([ta.create_volume_snapshot, \
            ta.delete_volume_snapshot])

    sp_state_dict = {
            322: d_sp_in_ps_action1,
            332: d_sp_in_bs_action1,
            342: d_sp_in_both_ps_bs_action1,
            323: d_sp_in_ps_action2,
            333: d_sp_in_bs_action2,
            343: d_sp_in_both_ps_bs_action2,
            352: r_sp_in_ps_action1,
            362: r_sp_in_bs_action1,
            372: r_sp_in_both_ps_bs_action1,
            353: r_sp_in_ps_action2,
            363: r_sp_in_bs_action2,
            373: r_sp_in_both_ps_bs_action2,
            382: [],
            383: [ta.create_volume_snapshot],
            222: d_sp_in_ps_action3,
            232: d_sp_in_bs_action3,
            242: d_sp_in_both_ps_bs_action3,
            223: d_sp_in_ps_action2,
            233: d_sp_in_bs_action2,
            243: d_sp_in_both_ps_bs_action2,
            252: r_sp_in_ps_action3,
            262: r_sp_in_bs_action3,
            272: r_sp_in_both_ps_bs_action3,
            253: r_sp_in_ps_action2,
            263: r_sp_in_bs_action2,
            283: [ta.create_volume_snapshot],
            282: [ta.create_volume_snapshot],
            273: r_sp_in_both_ps_bs_action2
            }

    #network related state
    sg_state_dict = {
            Any: 10, 
            no_sg: 20, 
            has_sg: 30}

    vip_state_dict = {
            Any: 100, 
            no_vip: 200, 
            has_vip: 300, 
            no_more_vip_res:400, 
            no_vip_res:500
            }

    #network related operations
    #vm_state + other network state
    net_action_transition_table = {
        Any: [ta.create_sg, ta.create_vip],
        31: [ta.delete_sg],
        32: [ta.sg_rule_operations, ta.delete_sg],
        33: [ta.sg_rule_operations, ta.delete_sg],
        34: [ta.delete_sg],
       301: [ta.delete_vip],
       302: [ta.delete_vip, ta.vip_operations],
       303: [ta.delete_vip, ta.vip_operations],
       304: [ta.delete_vip],
       401: [ta.delete_vip],
       402: [ta.delete_vip, ta.vip_operations],
       403: [ta.delete_vip, ta.vip_operations],
       404: [ta.delete_vip],
       501: []
    }

    def get_state(self):
        state = '%s: %s ; \
                %s: %s; \
                %s: %s; \
                %s: %s; \
                %s: %s; \
                %s: %s; \
                %s: %s; \
                %s: %s; \
                %s: %s; \
                %s: %s' % \
                (self.vm_state, self.vm_current_state, \
                self.vm_volume_state, self.vm_volume_current_state, \
                self.volume_state, self.volume_current_state, \
                self.image_state, self.image_current_state, \
                self.sg_state, self.sg_current_state, \
                self.vip_state, self.vip_current_state, \
                self.sp_state, self.sp_current_state, \
                self.sp_live_cap, self.snapshot_live_cap, \
                self.vm_live_sp_cap, self.vm_live_template_cap, \
                self.volume_vm_state, self.volume_vm_current_state)
        return state

    def set_vm_state(self, state):
        self.vm_current_state = self.vm_state_dict[state]

    def get_vm_state(self):
        return self.vm_current_state

    def set_vm_volume_state(self, state):
        self.vm_volume_current_state = self.vm_volume_state_dict[state]

    def get_vm_volume_state(self):
        return self.vm_volume_current_state

    def set_vm_live_migration_cap(self, state):
        self.vm_live_migration_cap = self.vm_live_migration_cap_dict[state]

    def get_vm_live_migration_cap(self):
        return self.vm_live_migration_cap

    def set_volume_state(self, state):
        self.volume_current_state = self.volume_state_dict[state]

    def get_volume_state(self):
        return self.volume_current_state

    def set_image_state(self, state):
        self.image_current_state = self.image_state_dict[state]

    def get_image_state(self):
        return self.image_current_state

    def set_sg_state(self, state):
        self.sg_current_state = self.sg_state_dict[state]

    def get_sg_state(self):
        return self.sg_current_state

    def set_vip_state(self, state):
        self.vip_current_state = self.vip_state_dict[state]

    def get_vip_state(self):
        return self.vip_current_state

    def set_snapshot_state(self, state):
        self.sp_current_state = self.snapshot_state_dict[state]

    def get_snapshot_state(self):
        return self.sp_current_state

    def set_snapshot_live_cap(self, state):
        self.snapshot_live_cap = self.snapshot_live_cap_dict[state]

    def get_snapshot_live_cap(self):
        return self.snapshot_live_cap

    def set_vm_live_template_cap(self, state):
        self.vm_live_template_cap = self.vm_live_template_cap_dict[state]

    def get_vm_live_template_cap(self):
        return self.vm_live_template_cap

    def set_volume_vm_state(self, state):
        self.volume_vm_current_state  = self.vm_state_dict[state]

    def get_volume_vm_state(self):
        return self.volume_vm_current_state

    def _get_network_actions(self, state_value):
        if self.net_action_transition_table.has_key(state_value):
            return self.net_action_transition_table[state_value]
        else:
            return []

    def get_general_network_actions(self):
        return self._get_network_actions(self.Any)

    def get_sg_actions(self):
        state = self.vm_current_state + self.sg_current_state
        return self._get_network_actions(state)

    def get_vip_actions(self):
        state = self.vm_current_state + self.vip_current_state
        return self._get_network_actions(state)

    def get_snapshot_actions(self):
        state = self.volume_vm_current_state + self.sp_current_state + self.snapshot_live_cap
        if self.sp_state_dict.has_key(state):
            return self.sp_state_dict[state]
        else:
            return []

    def _get_normal_actions(self, state_value):
        if self.normal_action_transition_table.has_key(state_value):
            return self.normal_action_transition_table[state_value]
        else:
            return []

    def get_general_actions(self):
        return self._get_normal_actions(self.Any)

    def get_vm_actions(self):
        vm_action1 = self._get_normal_actions(self.vm_current_state)
        vm_action2 = self._get_normal_actions(self.vm_current_state + self.vm_live_migration_cap)
        vm_action3 = self._get_normal_actions(self.vm_current_state + self.vm_live_migration_cap + self.vm_volume_current_state)
        vm_action4 = self._get_normal_actions(self.vm_current_state + self.vm_live_template_cap)
        return vm_action1 + vm_action2 + vm_action3 + vm_action4

    def get_volume_actions(self):
        #if state is deleted state, will directly return. 
        delete_state = self._get_normal_actions(self.volume_current_state)
        if delete_state:
            return delete_state

        state = self.vm_current_state + self.vm_volume_current_state + \
                self.volume_current_state

        return self._get_normal_actions(state)

    def get_image_actions(self):
        return self._get_normal_actions(self.image_current_state)


class TestStateDict(object):
    '''
        Track Test State.
        The test state is a collection for tracking VM states, Volume states, Image states and SG status. 
    '''
    import zstackwoodpecker.header.vip as vip_header
    vm_dict_desc = "vm_dict = \
            {'running':[vm1_obj,], \
            'stopped':[vm2_obj], \
            'destroyed':[vm3_obj], \
            'expunged':[vm4_obj]\
            }"

    volume_dict_desc = "volume_dict = \
            {vm_uuid1:[volume1_obj], \
            vm_uuid2:[], \
            'free_volume':[], \
            'deleted_volume':[], \
            'new_created_template_image':[]\
            }"

    sg_list_desc = "sg_list = [sg_uuid1, sg_uuid2]"
    sg_vm_desc = "sg_vm = zstack_test.zstack_test_sg_vm.ZstackTestSgVm()"
    vip_dict_desc = "vip_dict = \
            {'Detach' : [vip_test_obj, ], \
            'PF_detach' : [vip_test_obj,], \
            'EIP_detach' : [vip_test_obj], \
            'PF_attached' : [vip_test_obj, ], \
            'EIP_attached' : [vip_test_obj,], \
            'vm_uuid1: [vip_test_obj1, vip_test_obj2], \
            'vm_uuid2: [vip_test_obj], \
            }"
    volume_snapshot_desc = " volume_snapshot_dict = { \
            volume_uuid1: volume_snapshots_object, \
            Deleted': [volume_uuid] \
            }"

    #for test facility, like doing snapshot test. SG utility vm is in sg_vm()
    utility_vm_desc = " utility_vm_dict = {\
            cluster_uuid1: utiltiy_vm_object, \
            cluster_uuid2: utiltiy_vm_object \
            }"

    account_desc = " account_dict = {\
            'account_uuid': {'account': account_obj, 'user': [user_obj]},\
            'Deleted': [account_uuid] \
            }"

    instance_offering_desc = " instance_offering_dict = {\
            'instance_offering_uuid': instance_offering_inv, \
            'Deleted': [instance_offering_inv]\
            }"

    disk_offering_desc = " disk_offering_dict = {\
            'disk_offering_uuid': disk_offering_inv, \
            'Deleted': [disk_offering_inv]\
            }"

    def __init__(self):
        self.vm_dict = {
                vm_header.RUNNING:[], 
                vm_header.STOPPED:[], 
                vm_header.DESTROYED:[],
                vm_header.EXPUNGED:[],
                vm_header.PAUSED:[]
                }

        self.volume_dict = {
                TestStage.free_volume:[], 
                TestStage.deleted_volume:[]
                }

        self.image_dict = {
                TestStage.new_template_image:[], 
                TestStage.deleted_image:[]
                }

        self.hybrid_obj = None

        #sg_list is deprecated. all sg should be managed in sg_vm.
        self.sg_list = []
        #[Inlined import]
        import zstackwoodpecker.zstack_test.zstack_test_sg_vm as zstack_sg_vm_header
        self.sg_vm = zstack_sg_vm_header.ZstackTestSgVm()
        self.vip_dict = {
                vip_header.DETACHED:[], 
                pf_header.DETACHED:[], 
                eip_header.DETACHED:[], 
                pf_header.ATTACHED:[], 
                eip_header.ATTACHED:[]
                }

        self.volume_snapshot_dict = {'Deleted': []}
        self.utility_vm_dict = {}
        self.account_dict = {'Deleted': []}
        self.load_balancer_dict = {'Deleted': []}
        self.instance_offering_dict = {'Deleted': []}
        self.disk_offering_dict = {'Deleted': []}
        self.backup_dict = {}
        self.backup_list = []
    
    def __repr__(self):
        return str({
                'vm_dict': self.vm_dict,
                'volume_dict': self.volume_dict,
                'image_dict': self.image_dict,
                'sg_list': self.sg_list,
                'sg_vm': self.sg_vm,
                'vip_dict': self.vip_dict,
                'volume_snapshot_dict': self.volume_snapshot_dict,
                'utiltiy_vm_dict': self.utility_vm_dict,
                'accout_dict': self.account_dict,
                'backup_dict': self.backup_dict
        })

    def add_vm(self, vm, state=vm_header.RUNNING, create_snapshots = True):
        def add_vm_volume_snapshot(volume, data = True):
            if not self.get_volume_snapshot(volume.uuid):
                import zstackwoodpecker.zstack_test.zstack_test_snapshot \
                        as zstack_sp_header
                import zstackwoodpecker.zstack_test.zstack_test_volume \
                        as zstack_volume_header

                volume_obj = zstack_volume_header.ZstackTestVolume()
                volume_obj.set_volume(volume)
                volume_obj.set_state(volume_header.ATTACHED)
                volume_obj.set_target_vm(vm)
                #TODO: only add data volume so far, we could add root volume
                # later. Since root volume could be used to create data
                # volume template.
                if data:
                    self.add_volume(volume_obj, state = vm.get_vm().uuid)
                volume_snapshots = zstack_sp_header.ZstackVolumeSnapshot()
                volume_snapshots.set_target_volume(volume_obj)
                self.add_volume_snapshot(volume_snapshots)

        if not vm in self.vm_dict[state]:
            self.vm_dict[state].append(vm)
            if create_snapshots:
                import zstackwoodpecker.test_lib as test_lib
                root_volume = test_lib.lib_get_root_volume(vm.get_vm())
                add_vm_volume_snapshot(root_volume, data = False)
                data_volumes = test_lib.lib_get_data_volumes(vm.get_vm())
                for data_volume in data_volumes:
                    add_vm_volume_snapshot(data_volume)

    def mv_vm(self, vm, src_state, dst_state):
        self.rm_vm(vm, src_state)
        self.add_vm(vm, dst_state, False)

    def rm_vm(self, vm, state=None):
        '''
        Depends on delete policy. Destroy VM and Expunge VM will all call this
        function to change vm state. So we need to check vm's real status to
        decide what we need to do. 
        '''
        vm_inv = vm.get_vm()
        #move all attached data volume to free stage.
        if vm.get_state() == vm_header.EXPUNGED or \
                vm.get_state() == vm_header.DESTROYED:
            #currently we don't add root volume into volume list, so we need this judgment.
            if self.get_volume_list(vm_inv.uuid):
                for volume in self.get_volume_list(vm_inv.uuid):
                    if volume.get_volume().type != volume_header.ROOT_VOLUME:
                        self.mv_volume(volume, vm_inv.uuid, TestStage.free_volume)

        if vm.get_state() == vm_header.EXPUNGED:
            import zstackwoodpecker.test_lib as test_lib
            volume_uuid = test_lib.lib_get_root_volume(vm_inv).uuid
            self.rm_volume_snapshots_by_rm_volume(volume_uuid)
            #clean root volume and vm_inv relationship in volume dict.
            if self.volume_dict.has_key(vm_inv.uuid):
                self.volume_dict.pop(vm_inv.uuid)

        if state:
            if vm in self.vm_dict[state]:
                self.vm_dict[state].remove(vm)
                if vm.get_state() == vm_header.DESTROYED:
                    self.vm_dict[vm_header.DESTROYED].append(vm)
                elif vm.get_state() == vm_header.EXPUNGED:
                    self.vm_dict[vm_header.EXPUNGED].append(vm)
                return True
            return False

        for key,values in self.vm_dict.iteritems():
            if vm in values:
                self.vm_dict[key].remove(vm)
                if vm.get_state() == vm_header.DESTROYED:
                    self.vm_dict[vm_header.DESTROYED].append(vm)
                elif vm.get_state() == vm_header.EXPUNGED:
                    self.vm_dict[vm_header.EXPUNGED].append(vm)
                return True

        return False

    def add_hybrid_obj(self, hybrid_obj):
        self.hybrid_obj = hybrid_obj

    def get_vm_list(self, state=vm_header.RUNNING):
        return self.vm_dict[state]

    def get_all_vm_list(self):
        vm_list = []
        for values in self.vm_dict.itervalues():
            vm_list.extend(values)

        return vm_list

    def add_volume(self, volume, state=TestStage.free_volume):
        if not self.volume_dict.has_key(state):
            self.volume_dict[state] = []

        if not volume in self.volume_dict[state]:
            self.volume_dict[state].append(volume)
            if not self.get_volume_snapshot(volume.get_volume().uuid):
                import zstackwoodpecker.zstack_test.zstack_test_snapshot \
                        as zstack_sp_header
                volume_snapshots = zstack_sp_header.ZstackVolumeSnapshot()
                volume_snapshots.set_target_volume(volume)
                self.add_volume_snapshot(volume_snapshots)

    def rm_volume(self, volume, state=None):
        '''
        Depends on delete policy. Both delete volume and expunge volume might 
        call this function to remove volume object from test state.
        '''
        #need to delete empty snapshots, when volume is expunged. 
        self.rm_volume_snapshots_by_rm_volume(volume.get_volume().uuid)

        if state:
            if volume in self.volume_dict[state]:
                self.volume_dict[state].remove(volume)
                if volume.get_state() == volume_header.DELETED:
                    self.add_volume(volume, TestStage.deleted_volume)
                return True
            return False

        for key,values in self.volume_dict.iteritems():
            if volume in values:
                self.volume_dict[key].remove(volume)
                if volume.get_state() == volume_header.DELETED:
                    self.add_volume(volume, TestStage.deleted_volume)
                return True
        else:
            return False

    def mv_volume(self, volume, src_state, dst_state):
        self.rm_volume(volume, src_state)
        self.add_volume(volume, dst_state)

    def add_volume_with_snapshots(self, volume, state=TestStage.free_volume):
        if not self.volume_dict.has_key(state):
            self.volume_dict[state] = []

        if not volume in self.volume_dict[state]:
            self.volume_dict[state].append(volume)

    def rm_volume_with_snapshots(self, volume, state=None):
        if state:
            if volume in self.volume_dict[state]:
                self.volume_dict[state].remove(volume)
                if volume.get_state() == volume_header.DELETED:
                    self.add_volume(volume, TestStage.deleted_volume)
                return True
            return False

        for key,values in self.volume_dict.iteritems():
            if volume in values:
                self.volume_dict[key].remove(volume)
                if volume.get_state() == volume_header.DELETED:
                    self.add_volume(volume, TestStage.deleted_volume)
                return True
        else:
            return False

    def mv_volume_with_snapshots(self, volume, src_state, dst_state):
        self.rm_volume_with_snapshots(volume, src_state)
        self.add_volume_with_snapshots(volume, dst_state)

    def mv_volumes(self, src_state, dst_state):
        '''
        move all volumes from source state to destination state.
        '''
        if self.volume_dict.has_key(src_state):
            if self.volume_dict.has_key(dst_state):
                self.volume_dict[dst_state].extend(self.get_volume_list(src_state))
                self.volume_dict.pop(src_state)
            else:
                self.volume_dict[dst_state] = self.get_volume_list(src_state)
                self.volume_dict.pop(src_state)

    def create_empty_volume_list(self, vm_uuid):
        if not self.volume_dict.has_key(vm_uuid):
            self.volume_dict[vm_uuid] = []

    def attach_volume(self, volume, vm_uuid):
        self.mv_volume_with_snapshots(volume, TestStage.free_volume, vm_uuid)

    def detach_volume(self, volume):
        vm_uuid = volume.target_vm.vm.uuid
        self.mv_volume_with_snapshots(volume, vm_uuid, TestStage.free_volume)

    def get_volume_list(self, volume_state=TestStage.free_volume):
        if self.volume_dict.has_key(volume_state):
            return self.volume_dict[volume_state]

    def get_all_volume_list(self):
        volume_list = []
        for vl in self.volume_dict.values():
            volume_list.extend(vl)
        return volume_list

    def add_image(self, image, state=TestStage.new_template_image):
        if not image in self.image_dict[state]:
            self.image_dict[state].append(image)

    def get_image_list(self, state=TestStage.new_template_image):
        return self.image_dict[state]

    def rm_image(self, image, state=None):
        '''
        rm_image might be called when delete image. So need to check image state
        '''
        if state:
            if image in self.image_dict[state]:
                if image.get_state() == image_header.DELETED:
                    self.image_dict[state].remove(image)
                    self.add_image(image, TestStage.deleted_image)
                else:
                    self.image_dict[state].remove(image)
                return True
        else:
            for state in self.image_dict.iterkeys():
                if image in self.image_dict[state]:
                    if image.get_state() == image_header.DELETED:
                        self.image_dict[state].remove(image)
                        self.add_image(image, TestStage.deleted_image)
                        return True
                    else:
                        self.image_dict[state].remove(image)
                        return True
        return False

    def get_sg_list(self):
        return self.sg_vm.get_all_sgs()

    #Deprecated
    def add_sg(self, sg_uuid):
        if not sg_uuid in self.sg_list:
            self.sg_list.append(sg_uuid)

    #Deprecated
    def rm_sg(self, sg_uuid):
        if sg_uuid in self.sg_list:
            self.sg_list.remove(sg_uuid)

    def get_sg_vm(self):
        return self.sg_vm

    def set_sg_vm(self, sg_vm):
        self.sg_vm = sg_vm

    def add_vip(self, vip, state=vip_header.DETACHED):
        if not self.vip_dict.has_key(state):
            self.vip_dict[state] = [vip]
            return

        if not vip in self.vip_dict[state]:
            self.vip_dict[state].append(vip)

    def rm_vip(self, vip, state=None):
        if state:
            if vip in self.vip_dict[state]:
                self.vip_dict[state].remove(vip)
                return True
            return False

        result = False
        for key,values in self.vip_dict.iteritems():
            if vip in values:
                self.vip_dict[key].remove(vip)
                result = True

        return result

    def mv_vip(self, vip, dst_state, src_state=None):
        self.rm_vip(vip, src_state)
        self.add_vip(vip, dst_state)

    def get_vip_list(self, state=vip_header.DETACHED):
        if self.vip_dict.has_key(state):
            return self.vip_dict[state]
        else:
            return []

    def get_vip_dict(self):
        return self.vip_dict

    def get_all_vip_list(self):
        vip_list = []
        vip_list.extend(self.get_vip_list(vip_header.DETACHED))
        vip_list.extend(self.get_vip_list(eip_header.DETACHED))
        vip_list.extend(self.get_vip_list(pf_header.DETACHED))
        vip_list.extend(self.get_vip_list(eip_header.ATTACHED))
        vip_list.extend(self.get_vip_list(pf_header.ATTACHED))
        return vip_list

    def add_volume_snapshot(self, snapshots):
        '''
        There are 2 ways to do snapshot testing and call this function:

        1. This function will be called twice, when doing snapshot testing. 
        
        It will be 1stly called when a volume is created.
        The 2nd calling will be at doing real snapshots creating. The 2nd 
        calling will update volume_snapshot dict with the right one.
        (this is not recommended).

        2. [Recommended] This function will only be called once, when volume
        is created. When create snapshots, the volume_snapshots object should be
        get from self.get_volume_snapshot(volume_uuid). But before creating 
        snapshot, don't forget to set volume_snapshots.utiltiy_vm . So this 
        function is not recommended to be called by test case directly. 
        '''
        if not snapshots.get_target_volume():
            test_util.test_fail('Can not add volume_snapshot, before setting target_volume for it.')

        volume_uuid = snapshots.get_target_volume().get_volume().uuid
        if not self.volume_snapshot_dict.has_key(volume_uuid):
            self.volume_snapshot_dict[volume_uuid] = snapshots



    def rm_volume_snapshot(self, snapshots):
        '''
        Is recommended to be called when volume_snapshots.delete() is called.
        '''
        if not snapshots.get_target_volume():
            test_util.test_fail('Can not remove volume_snapshot, before setting target_volume for it.')
        volume_uuid = snapshots.get_target_volume().get_volume().uuid
        if not volume_uuid in self.volume_snapshot_dict['Deleted']:
            self.volume_snapshot_dict['Deleted'].append(volume_uuid)

    def rm_volume_snapshots_by_rm_volume(self, volume_uuid):
        snapshots = self.get_volume_snapshot(volume_uuid)
        if snapshots:
            #only hypervisor based snapshots will be deleted, when volume
            # is removed. 
            # snapshot.type has 2 options: Hypervisor and Storage
            snapshot_head = snapshots.get_snapshot_head()
            if snapshot_head and 'Storage' == snapshot_head.get_snapshot().type:
                return
            #If no snapshots is backuped, delete volume will remove all SPs.
            if not snapshots.get_backuped_snapshots():
                self.rm_volume_snapshot(snapshots)
            else:
                #otherwsie make sure volume is in Expunge state, especially for 
                #Root Volume
                root_volume_obj = snapshots.get_target_volume()
                root_volume_obj.update_volume()
                root_volume_obj.set_state(volume_header.EXPUNGED)
                self.rm_volume(root_volume_obj)

    def get_all_snapshots(self):
        all_items = []
        for key,value in self.volume_snapshot_dict.iteritems():
            if key != 'Deleted':
                all_items.append(value)
        return all_items

    def get_all_available_snapshots(self):
        all_items = []
        for key,value in self.volume_snapshot_dict.iteritems():
            if key != 'Deleted' and not key in self.volume_snapshot_dict['Deleted']:
                all_items.append(value)
        return all_items

    def get_volume_snapshot(self, volume_uuid):
        if self.volume_snapshot_dict.has_key(volume_uuid):
            return self.volume_snapshot_dict[volume_uuid]

    def add_utility_vm(self, utility_vm):
        '''
        Utility VM is for helping test. For example, used for snapshot.
        It should also be tracked in robot obj and cleanuped when robot test
        finished. Make sure it is different with 
        test_util.Robot_Test_Object().set_utility_vm()
        '''
        cluster_uuid = utility_vm.get_vm().clusterUuid
        self.utility_vm_dict[cluster_uuid] = utility_vm

    def rm_utility_vm(self, utility_vm):
        cluster_uuid = utility_vm.get_vm().clusterUuid
        if self.utility_vm_dict.has_key(cluster_uuid):
            self.utility_vm_dict.pop(cluster_uuid)

    def get_all_utility_vm(self):
        return self.utility_vm_dict.values()

    def add_account(self, account):
        acc_uuid = account.get_account().uuid
        if not self.account_dict.has_key(acc_uuid):
            self.account_dict[acc_uuid] = {'account': account, 'user': [], \
                    'deleted_user': []}
            return self.account_dict
        #else:
        #    self.account_dict[acc_uuid]['account'] = account

    def rm_account(self, account):
        acc_uuid = account.get_account().uuid
        if not acc_uuid in self.account_dict['Deleted']:
            self.account_dict['Deleted'].append(acc_uuid)
            return self.account_dict

    def get_all_accounts(self):
        all_accounts = []
        for key,value in self.account_dict.iteritems():
            if key != 'Deleted' and not key in self.account_dict['Deleted']:
                all_accounts.append(self.account_dict[key]['account'])
        return all_accounts

    def get_deleted_account(self):
        all_items = []
        for item in self.account_dict['Deleted']:
            all_items.append(self.account_dict[item])

        return all_items

    def add_user(self, user):
        acc_uuid = user.get_user().accountUuid
        if not user in self.account_dict[acc_uuid]['user']:
            self.account_dict[acc_uuid]['user'].append(user)

    def rm_user(self, user):
        acc_uuid = user.get_user().accountUuid
        if user in self.account_dict[acc_uuid]['user']:
            self.account_dict[acc_uuid]['user'].remove(user)
        if not user in self.account_dict[acc_uuid]['deleted_user']:
            self.account_dict[acc_uuid]['user'].append(user)

    def add_load_balancer(self, lb):
        lb_uuid = lb.get_load_balancer().uuid
        if not lb_uuid in self.load_balancer_dict.keys():
            self.load_balancer_dict[lb_uuid] = lb

    def rm_load_balancer(self, lb):
        lb_uuid = lb.get_load_balancer().uuid
        if not lb_uuid in self.load_balancer_dict['Deleted']:
            self.load_balancer_dict['Deleted'].append(lb_uuid)
            return self.load_balancer_dict

    def get_all_load_balancers(self):
        all_items = []
        for key,value in self.load_balancer_dict.iteritems():
            if key != 'Deleted' and not key in self.load_balancer_dict['Deleted']:
                all_items.append(value)
        return all_items

    def get_deleted_load_balancers(self):
        all_items = []
        for item in self.load_balancer_dict['Deleted']:
            all_items.append(self.load_balancer_dict[item])

        return all_items

    def add_instance_offering(self, instance_offering):
        instance_offering_uuid = instance_offering.uuid
        if not instance_offering_uuid in self.instance_offering_dict.keys():
            self.instance_offering_dict[instance_offering_uuid] = instance_offering

    def rm_instance_offering(self, instance_offering):
        instance_offering_uuid = instance_offering.uuid
        if not instance_offering_uuid in self.instance_offering_dict['Deleted']:
            self.instance_offering_dict['Deleted'].append(instance_offering_uuid)
            return self.instance_offering_dict

    def get_all_instance_offerings(self):
        all_items = []
        for key,value in self.instance_offering_dict.iteritems():
            if key != 'Deleted' and not key in self.instance_offering_dict['Deleted']:
                all_items.append(value)
        return all_items

    def get_deleted_instance_offerings(self):
        all_items = []
        for item in self.instance_offering_dict['Deleted']:
            all_items.append(self.instance_offering_dict[item])

        return all_items

    def add_disk_offering(self, disk_offering):
        disk_offering_uuid = disk_offering.uuid
        if not disk_offering_uuid in self.disk_offering_dict.keys():
            self.disk_offering_dict[disk_offering_uuid] = disk_offering

    def rm_disk_offering(self, disk_offering):
        disk_offering_uuid = disk_offering.uuid
        if not disk_offering_uuid in self.disk_offering_dict['Deleted']:
            self.disk_offering_dict['Deleted'].append(disk_offering_uuid)
            return self.disk_offering_dict

    def get_all_disk_offerings(self):
        all_items = []
        for key,value in self.disk_offering_dict.iteritems():
            if key != 'Deleted' and not key in self.disk_offering_dict['Deleted']:
                all_items.append(value)
        return all_items

    def get_deleted_disk_offerings(self):
        all_items = []
        for item in self.disk_offering_dict['Deleted']:
            all_items.append(self.disk_offering_dict[item])
        return all_items

    def update_vm_delete_policy(self, policy):
        for vm in self.get_all_vm_list():
            if vm.get_state() != vm_header.EXPUNGED:
                vm.set_delete_policy(policy)

    def update_vm_delete_delay_time(self, delay_time):
        for vm in self.get_all_vm_list():
            if vm.get_state() != vm_header.EXPUNGED:
                vm.set_delete_delay_time(delay_time)

    def update_volume_delete_policy(self, policy):
        for volume in self.get_all_volume_list():
            if volume.get_state() != volume_header.EXPUNGED:
                volume.set_delete_policy(policy)

    def update_volume_delete_delay_time(self, delay_time):
        for volume in self.get_all_volume_list():
            if volume.get_state() != volume_header.EXPUNGED:
                volume.set_delete_delay_time(delay_time)

    def update_image_delete_policy(self, policy):
        for image in self.get_image_list():
            if image.get_state() != image_header.EXPUNGED:
                image.set_delete_policy(policy)

    def update_image_delete_delay_time(self, delay_time):
        for image in self.get_image_list():
            if image.get_state() != image_header.EXPUNGED:
                image.set_delete_delay_time(delay_time)

    def add_backup(self, backup_uuid):
        cond = res_ops.gen_query_conditions("uuid", '=', backup_uuid)
        volume_uuid = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)[0].volumeUuid
        if not self.backup_dict.has_key(volume_uuid):
            self.backup_dict[volume_uuid] = []
        self.backup_dict[volume_uuid].append(backup_uuid)
        self.backup_list.append(backup_uuid)
 
    def get_volume_backup(self, volume_uuid):
        if self.backup_dict.has_key(volume_uuid):
            return self.backup_dict[volume_uuid]

    def rm_backup(self, uuid):
        if uuid in self.backup_list:
            self.backup_list.remove(uuid)

    def get_backup_list(self):
        return self.backup_list

    def add_backup_md5sum(self, backup_uuid, md5sum):
        self.backup_dict[backup_uuid] = md5sum

    def get_backup_md5sum(self, backup_uuid):
        return self.backup_dict[backup_uuid]

class Port(object):
    '''
    Predefined ports for network testing. 
    '''
    rule1_ports = 'rule1_ports'
    rule2_ports = 'rule2_ports'
    rule3_ports = 'rule3_ports'
    rule4_ports = 'rule4_ports'
    rule5_ports = 'rule5_ports'
    denied_ports = 'denied_ports'
    default_ports = 'default_ports'
    icmp_ports = 'icmp_ports'

    allowed_port_rules = [rule1_ports, rule2_ports, rule3_ports, rule4_ports, rule5_ports]

    #item[0] -> start_port, item[1] -> end_port
    #ports_range_dict = {rule1_ports:[1, 100], rule2_ports:[5000, 6000], rule3_ports:[9000, 10000], rule4_ports:[20000, 30000], rule5_ports:[60000, 65535], icmp_ports:[-1, -1], default_ports:[22]}
    ports_range_dict = {
            rule1_ports:[1, 100], 
            rule2_ports:[5001, 5100], 
            rule3_ports:[9001, 9100], 
            rule4_ports:[20501, 20600], 
            rule5_ports:[65436, 65535], 
            icmp_ports:[-1, -1], 
            default_ports:[22]
            }
    #ports_check_dict = {rule1_ports:[1, 55, 100], rule3_ports:[9000, 9999, 10000], rule5_ports:[60000, 60010, 65535], rule2_ports:[5000, 5201, 6000], rule4_ports:[20000, 23456, 28999, 30000], denied_ports:[101, 4999, 8990, 15000, 30001, 45678, 59999], default_ports:[22]}
    #ports_check_dict = {rule1_ports:[1, 55, 100], rule2_ports:[5000, 5998], rule3_ports:[9001, 9999], rule4_ports:[23456, 28999], rule5_ports:[60000, 65535], denied_ports:[101, 8990, 30001, 59999]}
    #port 0 is reserved and can't be used for testing.

    #FIXME:!!!each rule's ports should be similar, as they will be used for
    #port forwarding testing. In port forward test, the vip start/end might
    #be different compared with private start/end. So when telnet port 55, 
    #it might need to connect to port 5055.!!! 
    #This might be not true, but will be updated later.  

    ports_check_dict = {
            rule1_ports:[1, 55, 100], 
            rule2_ports:[5001, 5055, 5100], 
            rule3_ports:[9001, 9055, 9100], 
            rule4_ports:[20501, 20555, 20600], 
            rule5_ports:[65436, 65490, 65535], 
            denied_ports:[101, 8999, 30001, 59999]
            }

    all_ports = []
    for item in ports_check_dict.itervalues():
        all_ports.extend(item)

    @staticmethod
    def get_start_end_ports(rule):
        return Port.ports_range_dict[rule]

    @staticmethod
    def get_default_ports():
        return Port.ports_range_dict[Port.default_ports]

    @staticmethod
    def get_icmp_ports():
        return Port.ports_range_dict[Port.icmp_ports]

    @staticmethod
    def get_port_rule(start_port, end_port=None):
        '''
        It is used for get related port rule key. By using rule key could
        get available checking ports.

        @return:
            port_rule_key, like rule1_ports, rule2_ports
        '''
        for port_rule in Port.ports_range_dict.keys():
            if start_port in Port.ports_range_dict[port_rule]:
                if end_port and not end_port in Port.ports_range_dict[port_rule]:
                    continue
                return port_rule

    @staticmethod
    def get_denied_ports():
        return Port.ports_check_dict[Port.denied_ports]

    @staticmethod
    def get_ports(port_key):
        return Port.ports_check_dict[port_key]

class SgRule(object):
    #sg actions
    add_rule_to_sg = 'add_rule_to_security_group'
    remove_rule_from_sg = 'remove_rule_from_security_group'
    add_sg_to_vm = 'add_security_group_to_vm'
    remove_sg_from_vm = 'remove_security_group_from_vm'
    sg_operations = [add_rule_to_sg, remove_rule_from_sg, add_sg_to_vm, remove_sg_from_vm]

    #sg dict keys
    sg_rule_key = 'rules'
    sg_vm_nics_key = 'vm_nics'

    #enable default 22 port. The src_ip usually should be VR IMG internal ip address
    @staticmethod
    def get_default_sg_rules(src_ip, direction):
        if direction == inventory.INGRESS:
            rule = inventory.SecurityGroupRuleAO()
            rule.allowedCidr = '%s/32' % src_ip
            rule.protocol = inventory.TCP
            rule.startPort = Port.get_default_ports()[0]
            rule.endPort = Port.get_default_ports()[0]
            rule.type = inventory.INGRESS
        else:
            rule = inventory.SecurityGroupRuleAO()
            rule.allowedCidr = '%s/32' % src_ip
            rule.protocol = inventory.ICMP
            rule.startPort, rule.endPort = Port.get_icmp_ports()
            rule.type = inventory.EGRESS
        return rule

    @staticmethod
    def get_rule_ip(rule):
        return rule.allowedCidr.split('/')[0]

    #type will be inventory.INGRESS or EGRESS.
    @staticmethod
    def generate_sg_rule(target_ip, protocol=None, target_rule=None, type=None):
        '''
        This is for generate random sg rule.
        '''
        rule = inventory.SecurityGroupRuleAO()
        rule.allowedCidr = '%s/32' % target_ip
        if not protocol:
            protocol = random.choice([inventory.TCP, inventory.UDP, inventory.ICMP])
        rule.protocol = protocol
        if protocol == inventory.ICMP:
            rule.startPort, rule.endPort = Port.get_icmp_ports()
        else:
            if not target_rule:
                target_rule = random.choice(Port.allowed_port_rules)
            rule.startPort, rule.endPort = \
                    Port.get_start_end_ports(target_rule)

        if not type:
            type = random.choice([inventory.INGRESS, inventory.EGRESS])
        rule.type = type
        return rule

    @staticmethod
    def get_cidr_ip(cidr):
        '''
        The cidr address is like 192.168.0.1/24
        @return: 192.168.0.1
        '''
        return cidr.split('/')[0]

    @staticmethod
    def generate_random_sg_action(sg_vm, target_vm_nics):
        action_list = []
        action_list = [SgRule.add_rule_to_sg]
        #pickup 1 SG.
        target_sg = random.choice(sg_vm.get_all_sgs())
        target_nic = random.choice(target_vm_nics)
        target_rule_uuid = None

        #check if sg has rules
        sg_all_rules = target_sg.get_all_rules()
        if sg_all_rules:
            action_list.append(SgRule.remove_rule_from_sg)
            target_rule_uuid = random.choice(sg_all_rules).uuid

        sg_all_attached_nic = target_sg.get_all_attached_nics()
        if target_nic.uuid in sg_all_attached_nic:
            action_list.append(SgRule.remove_sg_from_vm)
        else:
            import zstackwoodpecker.test_lib as test_lib
            l3_service_types = \
                    test_lib.lib_get_l3_service_type(target_nic.l3NetworkUuid)
            if 'SecurityGroup' in l3_service_types:
                action_list.append(SgRule.add_sg_to_vm)
        
        return [random.choice(action_list), target_sg, target_nic, target_rule_uuid]

class VipAction(object):
    def __init__(self, test_state, target_vm):
        self.test_state = test_state
        self.vip_state_dict = test_state.get_vip_dict()
        self.target_vm = target_vm
        self.action = None
        self.target_vip = None
        self.action_dict = {}
        self.vm_nic_uuid = None
        self.vip_action_dict = {
            EipAction.create_eip: EipAction.create_eip_api,
            EipAction.create_attach_eip : EipAction.create_attach_eip_api,
            EipAction.delete_eip : EipAction.delete_eip_api,
            EipAction.attach_eip : EipAction.attach_eip_api,
            EipAction.detach_eip : EipAction.detach_eip_api,
            PfRule.create_pf : PfRule.create_pf_api,
            PfRule.create_attach_pf : PfRule.create_attach_pf_api,
            PfRule.delete_pf : PfRule.delete_pf_api,
            PfRule.attach_pf : PfRule.attach_pf_api,
            PfRule.detach_pf : PfRule.detach_pf_api
            }

    def execute_random_vip_ops(self):
        self._get_possible_actions()
        self._generate_random_action()
        if not self.action:
            test_util.test_logger('No available VIP operation could be execued')
            return

        test_util.test_dsc('Target VIP action is : %s, target_vm: %s, target_vm_nic: %s, target_vip: %s' % (self.action, self.target_vm.get_vm().uuid, self.vm_nic_uuid, self.target_vip.get_vip().uuid))
        if self.action == EipAction.create_eip:
            test_util.test_dsc('Robot Action: %s; on VIP: %s' % \
                (self.action, self.target_vip.get_vip().uuid))

            new_eip = EipAction.create_eip_api(self.target_vip)
            self.test_state.mv_vip(self.target_vip, \
                    eip_header.DETACHED, \
                    vip_header.DETACHED)
            test_util.test_dsc(\
                    'Robot Action Result: %s; new EIP: %s; on VIP: %s' % \
                    (self.action, new_eip.get_eip().uuid, \
                    self.target_vip.get_vip().uuid))

        elif self.action == EipAction.delete_eip:
            test_util.test_dsc('Robot Action: %s; on EIP: %s, on VIP: %s' % \
                (self.action, self.target_vip.get_eip().get_eip().uuid, \
                self.target_vip.get_vip().uuid))

            EipAction.delete_eip_api(self.target_vip)
            self.test_state.rm_vip(self.target_vip)

        elif self.action == EipAction.create_attach_eip:
            test_util.test_dsc(\
                    'Robot Action: %s; on VIP: %s; on VM: %s; on NIC: %s' % \
                    (self.action, self.target_vip.get_vip().uuid,\
                    self.target_vm.get_vm().uuid, self.vm_nic_uuid))

            eip = EipAction.create_attach_eip_api(self.target_vip, self.vm_nic_uuid, \
                    self.target_vm)
            self.test_state.mv_vip(self.target_vip, eip_header.ATTACHED, \
                    vip_header.DETACHED)
            self.test_state.add_vip(self.target_vip, \
                    self.target_vm.get_vm().uuid)
            test_util.test_dsc(\
'Robot Action Result: %s; new EIP: %s; on VIP: %s; on VM: %s; on NIC: %s' % \
                    (self.action, eip.get_eip().uuid, \
                    self.target_vip.get_vip().uuid, 
                    self.target_vm.get_vm().uuid, self.vm_nic_uuid))
            
        elif self.action == EipAction.detach_eip:
            test_util.test_dsc('Robot Action: %s; on EIP: %s, on VIP: %s' % \
                (self.action, self.target_vip.get_eip().get_eip().uuid, \
                self.target_vip.get_vip().uuid))

            EipAction.detach_eip_api(self.target_vip)
            self.test_state.mv_vip(self.target_vip, eip_header.DETACHED)

        elif self.action == EipAction.attach_eip:
            test_util.test_dsc(\
'Robot Action: %s; on VIP: %s; on EIP: %s; on VM: %s; on NIC: %s' % \
                    (self.action, self.target_vip.get_vip().uuid,\
                    self.target_vip.get_eip().get_eip().uuid, \
                    self.target_vm.get_vm().uuid, self.vm_nic_uuid))

            EipAction.attach_eip_api(self.target_vip, self.vm_nic_uuid, \
                    self.target_vm)
            self.test_state.mv_vip(self.target_vip, eip_header.ATTACHED)
            self.test_state.add_vip(self.target_vip, \
                    self.target_vm.get_vm().uuid)

        elif self.action == PfRule.create_pf:
            test_util.test_dsc('Robot Action: %s; on VIP: %s' % \
                (self.action, self.target_vip.get_vip().uuid))

            new_pf = PfRule.create_pf_api(self.target_vip)
            self.test_state.mv_vip(self.target_vip, pf_header.DETACHED, \
                    vip_header.DETACHED)
            test_util.test_dsc(\
                    'Robot Action Result: %s; new PF: %s; on VIP: %s' % \
                    (self.action, new_pf.get_port_forwarding().uuid, \
                    self.target_vip.get_vip().uuid))

        elif self.action == PfRule.delete_pf:
            pf = random.choice(self.target_vip.get_pf_list())
            test_util.test_dsc('Robot Action: %s; on PF: %s, on VIP: %s' % \
                (self.action, pf.get_port_forwarding().uuid, \
                self.target_vip.get_vip().uuid))

            PfRule.delete_pf_api(pf)
            self.test_state.rm_vip(self.target_vip)

        elif self.action == PfRule.create_attach_pf:
            test_util.test_dsc(\
                    'Robot Action: %s; on VIP: %s; on VM: %s; on NIC: %s' % \
                    (self.action, self.target_vip.get_vip().uuid,\
                    self.target_vm.get_vm().uuid, self.vm_nic_uuid))

            pf = PfRule.create_attach_pf_api(self.target_vip, self.vm_nic_uuid,\
                    self.target_vm)
            if not self.target_vip in \
                    self.test_state.get_vip_list(self.target_vm.get_vm().uuid):
                self.test_state.mv_vip(self.target_vip, pf_header.ATTACHED)
                self.test_state.add_vip(self.target_vip, \
                        self.target_vm.get_vm().uuid)
            test_util.test_dsc(\
'Robot Action Result: %s; new PF: %s; on VIP: %s; on VM: %s; on NIC: %s' % \
                    (self.action, pf.get_port_forwarding().uuid, \
                    self.target_vip.get_vip().uuid, 
                    self.target_vm.get_vm().uuid, self.vm_nic_uuid))

        elif self.action == PfRule.attach_pf:
            pf_list = self.target_vip.get_pf_list()
            detached_pf_list = []
            for pf in pf_list:
                if pf.get_state() == pf_header.DETACHED:
                    detached_pf_list.append(pf)

            pf = random.choice(detached_pf_list)

            test_util.test_dsc(\
'Robot Action: %s; on VIP: %s; on PF: %s; on VM: %s; on NIC: %s' % \
                    (self.action, self.target_vip.get_vip().uuid,\
                    pf.get_port_forwarding().uuid, \
                    self.target_vm.get_vm().uuid, self.vm_nic_uuid))

            PfRule.attach_pf_api(pf, self.vm_nic_uuid, self.target_vm)

            if not self.target_vip in \
                    self.test_state.get_vip_list(self.target_vm.get_vm().uuid):
                self.test_state.mv_vip(self.target_vip, pf_header.ATTACHED)
                self.test_state.add_vip(self.target_vip, \
                        self.target_vm.get_vm().uuid)
            
        elif self.action == PfRule.detach_pf:
            pf_list = self.target_vip.get_pf_list()
            attached_pf_list = []
            for pf in pf_list:
                if pf.get_state() == pf_header.ATTACHED:
                    attached_pf_list.append(pf)

            pf = random.choice(attached_pf_list)

            test_util.test_dsc('Robot Action: %s; on PF: %s, on VIP: %s' % \
                (self.action, pf.get_port_forwarding().uuid, \
                self.target_vip.get_vip().uuid))

            PfRule.detach_pf_api(pf)
            vip_uuid = self.target_vip.get_vip().uuid
            import zstackwoodpecker.operations.resource_operations as res_ops
            condition = res_ops.gen_query_conditions('uuid', '=', vip_uuid)
            vip = res_ops.query_resource(res_ops.VIP, condition)[0]
            #no more attached pfs in this vip. 
            if not vip.peerL3NetworkUuid:
                self.test_state.mv_vip(self.target_vip, pf_header.DETACHED)

    def _get_possible_actions(self):
        '''
        based on vip state dict and self.target_vm to generate possible vip actions 
        with possible vip resource.

        @return: vip_self.action_dict, vmNicUuid

        e.g.
        {EipAction.attach_eip: [vip1, vip2], 
        EipAction.create_pf: [vip3, vip4]}, vmNicUuid

        {}, None
        '''
        import zstackwoodpecker.test_lib as test_lib
        vrs = test_lib.lib_get_all_vrs()
        #not reach minimal VR number bar for executing eip/pf checking. 
        #eip/pf needs 3 VR  to do testing: 
        # 1. the VR for hold the VIP's peerL3NetworkUuid. This VR can't be used for
        #  testing, due to ip route short circuit. 
        # 2. the VR for allowed public IP. E.g. the PF's allowedCidr
        # 3. the VR for denied public IP. E.g. not belong to PF's allowedCidr
        # EP testing, ideally just need 2 VRs. But consider possible combined SG
        # rules, it is better to use 3+ VRs as well. 
        if not vrs or len(vrs) < 3:
            return 

        if self.vip_state_dict[vip_header.DETACHED]:
            dict_add_unique_item_list(self.action_dict, EipAction.create_eip, \
                    self.vip_state_dict[vip_header.DETACHED])
            dict_add_unique_item_list(self.action_dict, PfRule.create_pf, \
                    self.vip_state_dict[vip_header.DETACHED])

        if self.vip_state_dict[eip_header.DETACHED]:
            dict_add_unique_item_list(self.action_dict, EipAction.delete_eip, \
                    self.vip_state_dict[eip_header.DETACHED])

        if self.vip_state_dict[pf_header.DETACHED]:
            dict_add_unique_item_list(self.action_dict, PfRule.delete_pf, \
                    self.vip_state_dict[pf_header.DETACHED])

        if not self.target_vm:
            return

        vm_uuid = self.target_vm.get_vm().uuid
        #randomly pick up 1 vm nic.
        vmNic = random.choice(self.target_vm.get_vm().vmNics)
        self.vm_nic_uuid = vmNic.uuid
        l3_net_uuid = vmNic.l3NetworkUuid
        l3_service_type = test_lib.lib_get_l3_service_type(l3_net_uuid)
        if pf_header.SERVICE in l3_service_type:
            pf_flag = True
        else:
            pf_flag = False

        if eip_header.SERVICE in l3_service_type:
            eip_flag = True
        else:
            eip_flag = False

        vr = test_lib.lib_find_vr_by_pri_l3(l3_net_uuid)
        if not vr:
            return
        vr_ip = test_lib.lib_find_vr_pub_ip(vr)

        if not self.vip_state_dict.has_key(vm_uuid):
            #vm didn't have any pf or eip.
            if self.vip_state_dict[vip_header.DETACHED]:
                if eip_flag:
                    dict_add_unique_item_list(self.action_dict, \
                            EipAction.create_attach_eip, \
                            self.vip_state_dict[vip_header.DETACHED])
                if pf_flag:
                    dict_add_unique_item_list(self.action_dict, \
                            PfRule.create_attach_pf, \
                            self.vip_state_dict[vip_header.DETACHED])

            if self.vip_state_dict[eip_header.DETACHED]:
                if eip_flag:
                    dict_add_unique_item_list(self.action_dict, \
                            EipAction.attach_eip, \
                            self.vip_state_dict[eip_header.DETACHED])

            if self.vip_state_dict[pf_header.DETACHED]:
                if pf_flag:
                    for vip in self.vip_state_dict[pf_header.DETACHED]:
                        #judge if vm could be attached with detached pf rule.
                        if not vip.get_vip().peerL3NetworkUuid:
                            pf_list = vip.get_pf_list()
                            cidr = pf_list[0].get_creation_option().get_allowedCidr()
                            #The target vm's vr ip is same with allowed Cird.
                            #It can't be testable. So skip. 
                            if vr_ip == SgRule.get_cidr_ip(cidr):
                                continue
                        #else the vip has some pf, and it is set on differnt VR. 
                        #we can't set same vip on different VR.
                        elif vip.get_vip().peerL3NetworkUuid != l3_net_uuid:
                            continue
                        dict_add_unique_item_list(self.action_dict, \
                                PfRule.attach_pf, [vip])

        else:
            #FIXME: Currently we can't support multi EIP/PF assignemnt
            # It is because it needs enabling global config snatInboundTraffic
            return
            for vip in self.vip_state_dict[vm_uuid]:
                if vip.get_use_for() == vip_header.PortForwarding:
                    dict_add_unique_item_list(self.action_dict, PfRule.detach_pf, \
                            self.vip_state_dict[vm_uuid])
                    dict_add_unique_item_list(self.action_dict, PfRule.delete_pf, \
                            self.vip_state_dict[vm_uuid])
                    #check if there are available pf ports for attaching
                    pf_list = vip.get_pf_list()
                    tcp_free_ports = PfRule.cal_free_pf_port(pf_list, \
                            inventory.TCP)
                    udp_free_ports = PfRule.cal_free_pf_port(pf_list, \
                            inventory.UDP)
                    if tcp_free_ports or udp_free_ports:
                        dict_add_unique_item_list(self.action_dict, \
                                PfRule.create_attach_pf, \
                                self.vip_state_dict[vm_uuid])

                    #check if there are aviable free (with same vip) pf rule
                    #since there are pf vip is attached, only allow same vip.
                    if self.vip_state_dict[pf_header.DETACHED]:
                        for detached_vip in self.vip_state_dict[pf_header.DETACHED]:
                            if detached_vip.get_vip().uuid == \
                                    vip.get_vip().uuid or l3_net_uuid == \
                                    detached_vip.get_vip().peerL3NetworkUuid :
                                dict_add_unique_item_list(self.action_dict, \
                                        PfRule.attach_pf, \
                                        [detached_vip])
                else:
                    dict_add_unique_item_list(self.action_dict, \
                            EipAction.detach_eip, \
                            self.vip_state_dict[vm_uuid])

                    dict_add_unique_item_list(self.action_dict, \
                            EipAction.delete_eip, \
                            self.vip_state_dict[vm_uuid])

    def _generate_random_action(self):
        '''
        Base on vip action dictionary, generate random action and related target
        vip. 

        @return: action, target_vip
        '''
        if not self.action_dict:
            return

        self.action = random.choice(self.action_dict.keys())
        self.target_vip = random.choice(self.action_dict[self.action])

class EipAction(object):
    '''
    Class for EIP related actions
    '''
    #eip actions
    create_eip = 'create_eip'
    create_attach_eip = 'create_eip_attach_to_vm'
    delete_eip = 'delete_eip'
    attach_eip = 'attach_eip'
    detach_eip = 'detach_eip'

    @staticmethod
    def create_eip_api(vip, vm_nic_uuid=None, vm=None):
        vip_uuid = vip.get_vip().uuid
        eip_option = test_util.EipOption()
        eip_option.set_name('eip for nic: %s' % vm_nic_uuid)
        eip_option.set_vip_uuid(vip_uuid)
        eip_option.set_vm_nic_uuid(vm_nic_uuid)
        new_eip_obj = vip.create_eip(eip_option, vm)
        return new_eip_obj

    @staticmethod
    def create_attach_eip_api(vip, vm_nic_uuid, vm):
        new_eip_obj = EipAction.create_eip_api(vip, vm_nic_uuid, vm)
        return new_eip_obj

    @staticmethod
    def delete_eip_api(vip, vm_nic_uuid=None, vm=None):
        eip = vip.get_eip()
        eip.delete()
        return vip

    @staticmethod
    def attach_eip_api(vip, vm_nic_uuid, vm):
        eip = vip.get_eip()
        eip.attach(vm_nic_uuid, vm)
        return eip

    @staticmethod
    def detach_eip_api(vip, vm_nic_uuid=None, vm=None):
        eip = vip.get_eip()
        eip.detach()
        return eip

class PfRule(object):
    '''
    Class for Pf related rule and actions
    '''
    #pf actions
    create_pf = 'create_pf'
    create_attach_pf = 'create_pf_attach_to_vm'
    delete_pf = 'delete_pf'
    attach_pf = 'attach_pf'
    detach_pf = 'detach_pf'

    #type will be inventory.INGRESS or EGRESS.
    @staticmethod
    def generate_pf_rule_option(target_ip, \
            protocol=None, \
            vip_target_rule=None, \
            private_target_rule=None, \
            vip_uuid=None, \
            vm_nic_uuid=None):
        '''
        Generate Portfowarding rule creation option
        '''
        pf_rule_option = test_util.PortForwardingRuleOption()
        pf_rule_option.set_allowedCidr('%s/32' % target_ip)

        if not protocol:
            #Pf doesn't support ICMP
            protocol = random.choice([inventory.TCP, inventory.UDP])
        pf_rule_option.set_protocol(protocol)

        if not vip_target_rule:
            vip_target_rule = random.choice(Port.allowed_port_rules)
        startPort, endPort = Port.get_start_end_ports(vip_target_rule)
        pf_rule_option.set_vip_ports(startPort, endPort)
        if not private_target_rule:
            private_target_rule = random.choice(Port.allowed_port_rules)
        startPort, endPort = Port.get_start_end_ports(private_target_rule)
        pf_rule_option.set_private_ports(startPort, endPort)

        pf_rule_option.set_vip_uuid(vip_uuid)
        pf_rule_option.set_vm_nic_uuid(vm_nic_uuid)
        return pf_rule_option

    @staticmethod
    def cal_free_pf_port(pf_list, protocol):
        used_rule_key = []
        for pf in pf_list:
            pf_option = pf.get_creation_option()
            if not protocol == pf_option.get_protocol():
                continue

            start_port, end_port = pf_option.get_vip_ports()
            rule_key = Port.get_port_rule(start_port, end_port)
            if not rule_key in used_rule_key:
                used_rule_key.append(rule_key)

        import zstackwoodpecker.test_lib as test_lib
        return list_ops.list_minus(Port.allowed_port_rules, used_rule_key)

    @staticmethod
    def create_pf_api(vip, vm_nic_uuid=None, vm=None):
        vip_uuid = vip.get_vip().uuid
        pf_list = vip.get_pf_list()
        protocol = random.choice([inventory.TCP, inventory.UDP])
        free_ports = PfRule.cal_free_pf_port(pf_list, protocol)
        if not free_ports:
            if protocol == inventory.TCP:
                protocol = inventory.UDP
            else:
                protocol = inventory.TCP
            free_ports = PfRule.cal_free_pf_port(pf_list, protocol)
            if not free_ports:
                test_util.test_warn("Potential bug: should not add pf rule, since there isn't port available.")

        pf_port_rule = random.choice(free_ports)
        start_port, end_port = Port.get_start_end_ports(pf_port_rule)
        pf_option = test_util.PortForwardingRuleOption()
        pf_option.set_vip_ports(start_port, end_port)
        pf_option.set_protocol(protocol)

        import zstackwoodpecker.test_lib as test_lib
        vrs = test_lib.lib_get_all_vrs()
        if vm_nic_uuid:
            l3_uuid = test_lib.lib_get_nic_by_uuid(vm_nic_uuid).l3NetworkUuid
            vm_vr = test_lib.lib_find_vr_by_pri_l3(l3_uuid)
            for vr in vrs:
                if vr.uuid != vm_vr.uuid:
                    vr_public_ip = test_lib.lib_find_vr_pub_ip(vr)
                    break
            else:
                test_util.test_warn("Did not find available VR public IP to set PF's allowedCidr. It means there are not enough VRs ready for testing")
        else:
            vr = random.choice(vrs)
            vr_public_ip = test_lib.lib_find_vr_pub_ip(vr)

        pf_option.set_allowedCidr('%s/32' % vr_public_ip)
        pf_option.set_name('pf for nic: %s' % vm_nic_uuid)
        pf_option.set_vip_uuid(vip_uuid)
        pf_option.set_vm_nic_uuid(vm_nic_uuid)
        pf_option.set_protocol
        return vip.create_pf(pf_option, vm)

    @staticmethod
    def create_attach_pf_api(vip, vm_nic_uuid, vm):
        pf = PfRule.create_pf_api(vip, vm_nic_uuid, vm)
        return pf

    @staticmethod
    def delete_pf_api(pf, vm_nic_uuid=None, vm=None):
        pf.delete()
        return pf

    @staticmethod
    def attach_pf_api(pf, vm_nic_uuid, vm):
        pf.attach(vm_nic_uuid, vm)
        return pf

    @staticmethod
    def detach_pf_api(pf, vm_nic_uuid=None, vm=None):
        pf.detach()
        return pf

def generate_action_list(test_stage, exclude_actions_list=[]):
    action_list = []
    #Add default actions
    action_list.extend(test_stage.get_general_actions())
    action_list.extend(test_stage.get_general_network_actions())
    #Add common vm actions, based on vm current state
    action_list.extend(test_stage.get_vm_actions())
    #Add volume actions
    action_list.extend(test_stage.get_volume_actions())
    #Add template image actions
    action_list.extend(test_stage.get_image_actions())

    #Add security group actions
    if test_stage.get_sg_state():
        action_list.extend(test_stage.get_sg_actions())
        #FIXME: currently manually increasing sg rule testing frequency.
        if TestAction.sg_rule_operations in action_list:
            action_list.append(TestAction.sg_rule_operations)
            action_list.append(TestAction.sg_rule_operations)

    #Add vip actions
    if test_stage.get_vip_state():
        action_list.extend(test_stage.get_vip_actions())

    #Add snapshot actions
    if test_stage.get_snapshot_state():
        action_list.extend(test_stage.get_snapshot_actions())

    #minus exclude_action_list
    if exclude_actions_list:
        for action in exclude_actions_list:
            if action in action_list:
                action_list.remove(action)
        
    return action_list

def dict_add_unique_item_list(dictionary, key, value_list):
    if dictionary.has_key(key):
        for value in value_list:
            if value in dictionary[key]:
                return
            else:
                dictionary[key].append(value)
    else:
        dictionary[key] = list(value_list)
