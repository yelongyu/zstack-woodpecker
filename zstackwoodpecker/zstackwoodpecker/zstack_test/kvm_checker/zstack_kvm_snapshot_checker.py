import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
import zstackwoodpecker.header.volume as vl_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.snapshot as sp_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as cfg_ops
import apibinding.inventory as inventory

class zstack_kvm_backuped_snapshot_checker(checker_header.TestChecker):
    def check(self):
        '''
        will check if backuped snapshot existed.
        '''
        super(zstack_kvm_backuped_snapshot_checker, self).check()
        backuped_snapshots = self.test_obj.get_backuped_snapshots()
        for sp in backuped_snapshots:
            sp_bs_refs = sp.get_snapshot().backupStorageRefs
            for sp_bs_ref in sp_bs_refs:
                bs_uuid = sp_bs_ref.backupStorageUuid
                sp_path = sp_bs_ref.installPath
                sp_uuid = sp_bs_ref.volumeSnapshotUuid
                bs_host = test_lib.lib_get_backup_storage_host(bs_uuid)
                bs = test_lib.lib_get_backup_storage_by_uuid(sp_bs_ref.backupStorageUuid)
                if hasattr(inventory, 'IMAGE_STORE_BACKUP_STORAGE_TYPE') and bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
                    sp_info = sp_path.split('://')[1].split('/')
                    sp_path = '%s/registry/v1/repos/public/%s/manifests/revisions/%s' % (bs.url, sp_info[0], sp_info[1])
                if test_lib.lib_check_file_exist(bs_host, sp_path):
                    test_util.test_logger('Checker result: backuped snapshot:%s is found in backup storage:%s in path: %s' % (sp_uuid, bs_uuid, sp_path))
                    if self.exp_result == False:
                        return self.judge(True)
                else:
                    test_util.test_logger('Checker result: backuped snapshot:%s is NOT found in backup storage:%s in path: %s' % (sp_uuid, bs_uuid, sp_path))
                    if self.exp_result == True:
                        return self.judge(False)

        test_util.test_logger('Checker result: Finish backuped snapshot checking')
        return self.judge(self.exp_result)


class zstack_kvm_snapshot_checker(checker_header.TestChecker):
    def check(self):
        '''
        Will use snapshot:createDataVolumeFromSnapshot function to do checking.
        '''
        super(zstack_kvm_snapshot_checker, self).check()
        target_volume = self.test_obj.get_target_volume()
        if target_volume.get_volume().type == 'Root':
            test_util.test_logger('Checking Result: skip snapshot checking, since target volume: %s is Root volme' % target_volume.get_volume().uuid)
            return self.judge(self.exp_result)

        if 'ebs://' in  target_volume.get_volume().installPath:
            test_util.test_logger('Checking Result: skip snapshot checking, since target volume: %s is EBS volume' % target_volume.get_volume().uuid)
            return self.judge(self.exp_result)

        #snapshots = self.test_obj.get_snapshot_list()
        sp = self.test_obj.get_current_snapshot()
        if not sp:
            test_util.test_logger('Checker result: no available current snapshot to be checked')
            return self.judge(self.exp_result)

        utility_vm = self.test_obj.get_utility_vm()
        vm_inv = utility_vm.get_vm()

        result = True
        #only need to test latest current snapshot, since previouse snapshot
        #operations should be checked already and assumed won't be changed. 
        #If there is not true, change following 2 lines to next line:
        #for sp in snapshots.get_snapshot_list():
        if sp.get_state() == sp_header.DELETED:
            #continue
            test_util.test_logger('Checking Result: snapshot status is Deleted, it should not be tested')
            return self.judge(self.exp_result)

        #calculate checking point
        checking_points_list = self.test_obj.get_checking_points(sp)

        volume_obj = sp.create_data_volume()
        volume_obj.attach(utility_vm)
        import tempfile
        with tempfile.NamedTemporaryFile() as script:
            script.write('''
device=/dev/`ls -ltr --file-type /dev | grep disk | awk '{print $NF}' | grep -v '[[:digit:]]' | tail -1`1
mkdir -p %s >/dev/null
mount $device %s >/dev/null
mkdir -p %s >/dev/null
checking_result=''
ls %s
umount %s >/dev/null
            ''' % (test_lib.WOODPECKER_MOUNT_POINT, \
                    test_lib.WOODPECKER_MOUNT_POINT, \
                    zstack_sp_header.checking_point_folder, \
                    zstack_sp_header.checking_point_folder, \
                    test_lib.WOODPECKER_MOUNT_POINT))
            script.flush()
            rsp = test_lib.lib_execute_shell_script_in_vm(vm_inv, \
                    script.name)

        volume_obj.detach()
        volume_obj.delete()
        if rsp:
            result_list = rsp.result.split()
            temp_checking_list = list(result_list)
            temp_exp_list = list(checking_points_list)
            for item in result_list:
                if item in checking_points_list:
                    temp_checking_list.remove(item)
                    temp_exp_list.remove(item)

            if len(temp_exp_list) == 0:
                if len(temp_checking_list) == 0:
                    test_util.test_logger('Checker result: snapshot: %s integrity checking pass' % sp.get_snapshot().uuid)
                else:
                    test_util.test_logger('Checker result: snapshot: %s integrity checking fail, there are something more than expected : %s' % (sp.get_snapshot().uuid, temp_checking_list))
                    zstack_sp_header.print_snapshot_chain_checking_point(zstack_sp_header.get_all_ancestry(sp))
                    result = False
            else:
                if len(temp_checking_list) == 0:
                    test_util.test_logger('Checker result: snapshot: %s integrity checking fail, there are something less than expected: %s' % (sp.get_snapshot().uuid, temp_exp_list))
                    zstack_sp_header.print_snapshot_chain_checking_point(zstack_sp_header.get_all_ancestry(sp))
                    result = False
                else:
                    test_util.test_logger('Checker result: snapshot: %s integrity checking fail, there are something more than expected : %s and there are something less than expected: %s ' % (sp.get_snapshot().uuid, temp_checking_list, temp_exp_list))
                    zstack_sp_header.print_snapshot_chain_checking_point(zstack_sp_header.get_all_ancestry(sp))
                    result = False
        else:
            test_util.test_logger('Checker result: check snapshot: %s failed with checking script.' % sp.get_snapshot().uuid)
            zstack_sp_header.print_snapshot_chain_checking_point(zstack_sp_header.get_all_ancestry(sp))
            result = False

        return self.judge(result)

class zstack_kvm_snapshot_tree_checker(checker_header.TestChecker):
    def check(self):
        '''
        Will check snapshot tree correctness  

        To be noticed. The tree depth changing will impact the snapshots who
        have been created. So if the snapshots are created before 
        incrementalSnapshot.maxNum is changed. The checker results will be 
        untrustable. 
        '''
        import json
        import zstacklib.utils.jsonobject as jsonobject
        super(zstack_kvm_snapshot_tree_checker, self).check()
        snapshots = self.test_obj.get_snapshot_list()
        if not self.test_obj.get_snapshot_head():
            test_util.test_logger('Snapshot is not created, skipped checking')
            return self.judge(self.exp_result)
        utility_vm = self.test_obj.get_utility_vm()
        vm_inv = utility_vm.get_vm()
        volume_obj = self.test_obj.get_target_volume()
        volume_uuid = volume_obj.get_volume().uuid

        if volume_obj.get_state() == vl_header.DELETED or \
                (volume_obj.get_volume().type == 'Root' and \
                volume_obj.get_target_vm().get_state() == vm_header.DESTROYED):
            test_util.test_logger('Checker result: target volume is deleted, can not get get and check snapshot tree status')
            return self.judge(self.exp_result)

        vol_trees = test_lib.lib_get_volume_snapshot_tree(volume_uuid)
        tree_allowed_depth = cfg_ops.get_global_config_value('volumeSnapshot', \
                'incrementalSnapshot.maxNum')

        for vol_tree in vol_trees:
            tree = json.loads(jsonobject.dumps(vol_tree))['tree']
            tree_max_depth = find_tree_max_depth(tree)
            if tree_max_depth > (int(tree_allowed_depth) + 1):
                test_util.test_logger(\
'Checker result: volume: %s snapshot tree: %s  depth checking failure. The max \
allowed depth is : %s. But we get: %s' % (volume_uuid, tree['inventory'].uuid, \
    tree_allowed_depth, str(tree_max_depth - 1)))
                return self.judge(False)

            test_util.test_logger(\
'Checker result: volume: %s snapshot tree depth checking pass. The max allowed \
depth is : %s. The real snapshot max depth is: %s' % \
            (volume_uuid, tree_allowed_depth, str(tree_max_depth - 1)))
        return self.judge(True)

def find_tree_max_depth(tree):
    '''
    tree is a dictionary. Its children were put under keyword of 'children'.
    '''
    if not tree:
        return 0

    child_depth = 0

    if not tree.has_key('children'):
        test_util.test_fail('Snapshot tree has invalid format, it does not has key for children.')

    if tree['children']:
        child_depth = 1
        for child in tree['children']:
            current_child_depth = find_tree_max_depth(child)
            child_depth = max(child_depth, current_child_depth)

    return child_depth + 1
