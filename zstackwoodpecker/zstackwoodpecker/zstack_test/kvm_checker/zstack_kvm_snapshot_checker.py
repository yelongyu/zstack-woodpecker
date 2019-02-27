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

        sp_tree_actual = []
        sp_tree_zs = []

        super(zstack_kvm_snapshot_tree_checker, self).check()
        snapshots = self.test_obj.get_snapshot_list()

        if not self.test_obj.get_snapshot_head():
            test_util.test_logger('Snapshot is not created, skipped checking')
            return self.judge(self.exp_result)
        #utility_vm = self.test_obj.get_utility_vm()
        #vm_inv = utility_vm.get_vm()
        volume_obj = self.test_obj.get_target_volume()
        volume_uuid = volume_obj.get_volume().uuid
        #volume_installPath = volume_obj.get_volume().installPath

        #if not volume_installPath:
        #    test_util.test_logger('Check result: [installPath] is Null for [volume uuid: ] %s. Can not check volume file existence' % volume.uuid)
        #    return self.judge(self.exp_result)

        if volume_obj.get_state() == vl_header.DELETED:
            test_util.test_logger('Checker result: target volume is deleted, can not get get and check snapshot tree status')
            return self.judge(self.exp_result)

        if volume_obj.get_target_vm():
            if volume_obj.get_volume().type == 'Root' and volume_obj.get_target_vm().get_state() == vm_header.DESTROYED:
                test_util.test_logger('Checker result: target volume is deleted, can not get get and check snapshot tree status')
                return self.judge(self.exp_result)

        ps_uuid = volume_obj.get_volume().primaryStorageUuid
        ps = test_lib.lib_get_primary_storage_by_uuid(ps_uuid)

        # Only Ceph has raw image format for non-Root volume
        if ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:
            for snapshot in snapshots:
                backing_list = []
                backing_file = ''
                sp_covered = 0
                activate_host = ''

                devPath = snapshot.get_snapshot().primaryStorageInstallPath.split("ceph://")[1]
                volumePath = snapshot.get_snapshot().primaryStorageInstallPath.split("ceph://")[1].split("@")[0]

                for i in sp_tree_actual:
                    if devPath in i:
                        test_util.test_logger('%s already in sp list %s' % (devPath, backing_list))
                        sp_covered = 1

                if sp_covered == 1:
                    continue
                else:
                    test_util.test_logger('%s not in current sp list, start checking its backing chain' % (devPath))

                backing_list.append(devPath)

                cmd_info = "rbd info %s" % devPath

                for host in test_lib.lib_find_hosts_by_ps_uuid(ps_uuid):
                    result = test_lib.lib_execute_ssh_cmd(host.managementIp, 'root', 'password', cmd_info)
                    if result:
                        activate_host = host.managementIp
                        break

                if not activate_host:
                    test_util.test_logger('No activate host found for %s' % (snapshot))
                    return self.judge(self.exp_result)

                while True:
                    cmd_info = "rbd info %s" % devPath

                    result = test_lib.lib_execute_ssh_cmd(activate_host, 'root', 'password', cmd_info)
                    if result:
                        tmp_list = get_snaps_for_raw_by_ip(volumePath, activate_host)
                    else:
                        test_util.test_logger('No activate host found for %s' % (snapshot))
                        return self.judge(self.exp_result)

                    if tmp_list:
                        for i in tmp_list:
                            i = i.replace("\n", "")
                            if i == snapshot.get_snapshot().primaryStorageInstallPath.split("ceph://")[1].split("@")[1]:
                                test_util.test_logger('%s is found for volume %s' % (devPath, volumePath))
                                sp_covered = 1
                    elif not tmp_list:
                        test_util.test_logger('No snapshots found for volume %s' % (volumePath))
                        return self.judge(False)

                    #backing_file = backing_file.replace("\n", "")

                    if sp_covered == 1:
                        break
                    else:
                        test_util.test_logger('%s is not found for volume %s' % (devPath, volumePath))
                        return self.judge(False)

                sp_covered = 0

                #backing_list = list(reversed(backing_list))

                if not sp_tree_actual:
                    test_util.test_logger('current sp list is empty, add %s into it' % (backing_list))
                    sp_tree_actual.append(backing_list)
                    continue

                for i in sp_tree_actual:
                    if backing_list == i:
                        sp_covered = 1

                if sp_covered == 1:
                    test_util.test_logger('%s already in current sp list %s, no need to add it anymore' % (backing_list, sp_tree_actual))
                    continue
                else:
                    test_util.test_logger('%s not in current sp list %s, start comparing detailed list items' % (backing_list, sp_tree_actual))

                for i in sp_tree_actual:
                    count = min(len(backing_list), len(i)) - 1
                    tmp_count = 0
                    while tmp_count <= count:
                        if backing_list[tmp_count] == i[tmp_count]:
                            tmp_count += 1
                            sp_covered = 1
                            continue
                        elif backing_list[tmp_count] != i[tmp_count]:
                            sp_covered = 0
                            break

                    if sp_covered == 0:
                        if i == sp_tree_actual[-1]:
                            test_util.test_logger('%s not in current sp list %s, add it into sp list' % (backing_list, sp_tree_actual))
                            sp_tree_actual.append(backing_list)
                            break
                    elif sp_covered == 1 and len(backing_list) > len(i):
                        test_util.test_logger('%s is the superset of the list %s in current sp list %s, update current sp list' % (backing_list, i, sp_tree_actual))
                        sp_tree_actual.remove(i)
                        sp_tree_actual.append(backing_list)
                        break
                    elif sp_covered == 1 and len(backing_list) <= len(i):
                        test_util.test_logger('%s already in current sp list %s, no need to add it anymore' % (backing_list, sp_tree_actual))
                        break

            test_util.test_logger('sp_tree_actual is %s' % (sp_tree_actual))
        
            vol_trees = test_lib.lib_get_volume_snapshot_tree(volume_uuid)
            tree_allowed_depth = cfg_ops.get_global_config_value('volumeSnapshot', \
                    'incrementalSnapshot.maxNum')

            for vol_tree in vol_trees:
                tree = json.loads(jsonobject.dumps(vol_tree))['tree']

                for leaf_node in get_leaf_nodes(tree):
                    backing_list = []
                    backing_file = ''
                    current_node = ''

                    backing_file = leaf_node['inventory']['primaryStorageInstallPath'].split("ceph://")[1]
                    backing_list.append(backing_file.encode('utf-8'))
                    current_node = leaf_node

                    while True:
                        parent_node = get_parent_node(tree, current_node)

                        if not parent_node:
                            break

                        backing_file = parent_node['inventory']['primaryStorageInstallPath'].split("ceph://")[1]
                        backing_list.append(backing_file.encode('utf-8'))

                        if parent_node.has_key('parentUuid'):
                            current_node = parent_node
                            continue
                        else:
                            break

                    backing_list = list(reversed(backing_list))
                    sp_tree_zs.append(backing_list)

            test_util.test_logger('sp_tree_zs is %s' % (sp_tree_zs))

            test_util.test_logger('compare the 2 sp lists - %s and %s' % (sp_tree_actual, sp_tree_zs))
            sp_covered = 0

            if len(sp_tree_actual) != len(sp_tree_zs):
                test_util.test_logger('%s is not same length as %s' % (sp_tree_actual, sp_tree_zs))
                return self.judge(False)

            for i in sp_tree_actual:
                if i in sp_tree_zs:
                    sp_covered = 1
                    test_util.test_logger('%s is in zs sp list %s' % (i, sp_tree_zs))
                    if i == sp_tree_actual[-1]:
                        test_util.test_logger('all the items in %s are in zs sp list %s' % (sp_tree_actual, sp_tree_zs))
                    continue
                elif i not in sp_tree_zs:
                    sp_covered = 0
                    test_util.test_logger('%s is not in zs sp list %s' % (i, sp_tree_zs))
                    return self.judge(False)
        elif ps.type == 'SharedBlock':
            for snapshot in snapshots:
                backing_list = []
                backing_file = ''
                sp_covered = 0
                activate_host = ''

                devPath = "/dev/" + snapshot.get_snapshot().primaryStorageInstallPath.split("sharedblock://")[1]

                for i in sp_tree_actual:
                    if devPath in i:
                        test_util.test_logger('%s already in sp list %s' % (devPath, backing_list))
                        sp_covered = 1

                if sp_covered == 1:
                    continue
                else:
                    test_util.test_logger('%s not in current sp list, start checking its backing chain' % (devPath))

                backing_list.append(devPath)

                cmd_info = "lvs --nolocking --noheadings %s | awk '{print $3}'" % devPath

                for host in test_lib.lib_find_hosts_by_ps_uuid(ps_uuid):
                    result = test_lib.lib_execute_ssh_cmd(host.managementIp, 'root', 'password', cmd_info)
                    if "-a-" in result or "-ao-" in result:
                        activate_host = host.managementIp
                        break

                if not activate_host:
                    activate_host = test_lib.lib_find_hosts_by_ps_uuid(ps_uuid)[0].managementIp

                while True:
                    cmd_info = "lvs --nolocking --noheadings %s | awk '{print $3}'" % devPath
                    cmd_activate = "lvchange -a y %s" % devPath
                    cmd_unactivate = "lvchange -a y %s" % devPath

                    result = test_lib.lib_execute_ssh_cmd(activate_host, 'root', 'password', cmd_info)
                    if "-a-" in result or "-ao-" in result:
                        backing_file = get_qcow_backing_file_by_ip(devPath, activate_host)
                    else:
                        test_lib.lib_execute_ssh_cmd(activate_host, 'root', 'password', cmd_activate)
                        backing_file = get_qcow_backing_file_by_ip(devPath, activate_host)
                        test_lib.lib_execute_ssh_cmd(activate_host, 'root', 'password', cmd_unactivate)
                    backing_file = backing_file.replace("\n", "")

                    if not backing_file:
                        if volume_obj.get_volume().type == 'Root':
                            test_util.test_logger('%s is against the Root volume, need to pop up the image cache %s' % (snapshot, devPath))
                            backing_list.pop()
                        break
                    else:
                        backing_list.append(backing_file)
                        devPath = backing_file

                backing_list = list(reversed(backing_list))

                if not sp_tree_actual:
                    test_util.test_logger('current sp list is empty, add %s into it' % (backing_list))
                    sp_tree_actual.append(backing_list)
                    continue

                for i in sp_tree_actual:
                    if backing_list == i:
                        sp_covered = 1

                if sp_covered == 1:
                    test_util.test_logger('%s already in current sp list %s, no need to add it anymore' % (backing_list, sp_tree_actual))
                    continue
                else:
                    test_util.test_logger('%s not in current sp list %s, start comparing detailed list items' % (backing_list, sp_tree_actual))

                for i in sp_tree_actual:
                    count = min(len(backing_list), len(i)) - 1
                    tmp_count = 0
                    while tmp_count <= count:
                        if backing_list[tmp_count] == i[tmp_count]:
                            tmp_count += 1
                            sp_covered = 1
                            continue
                        elif backing_list[tmp_count] != i[tmp_count]:
                            sp_covered = 0
                            break

                    if sp_covered == 0:
                        if i == sp_tree_actual[-1]:
                            test_util.test_logger('%s not in current sp list %s, add it into sp list' % (backing_list, sp_tree_actual))
                            sp_tree_actual.append(backing_list)
                            break
                    elif sp_covered == 1 and len(backing_list) > len(i):
                        test_util.test_logger('%s is the superset of the list %s in current sp list %s, update current sp list' % (backing_list, i, sp_tree_actual))
                        sp_tree_actual.remove(i)
                        sp_tree_actual.append(backing_list)
                        break
                    elif sp_covered == 1 and len(backing_list) <= len(i):
                        test_util.test_logger('%s already in current sp list %s, no need to add it anymore' % (backing_list, sp_tree_actual))
                        break

            test_util.test_logger('sp_tree_actual is %s' % (sp_tree_actual))
        
            vol_trees = test_lib.lib_get_volume_snapshot_tree(volume_uuid)
            tree_allowed_depth = cfg_ops.get_global_config_value('volumeSnapshot', \
                    'incrementalSnapshot.maxNum')

            for vol_tree in vol_trees:
                tree = json.loads(jsonobject.dumps(vol_tree))['tree']

                for leaf_node in get_leaf_nodes(tree):
                    backing_list = []
                    backing_file = ''
                    current_node = ''

                    backing_file = "/dev/" + leaf_node['inventory']['primaryStorageInstallPath'].split("sharedblock://")[1]
                    backing_list.append(backing_file.encode('utf-8'))
                    current_node = leaf_node

                    while True:
                        parent_node = get_parent_node(tree, current_node)

                        if not parent_node:
                            break

                        backing_file = "/dev/" + parent_node['inventory']['primaryStorageInstallPath'].split("sharedblock://")[1]
                        backing_list.append(backing_file.encode('utf-8'))

                        if parent_node.has_key('parentUuid'):
                            current_node = parent_node
                            continue
                        else:
                            break

                    backing_list = list(reversed(backing_list))
                    sp_tree_zs.append(backing_list)

            test_util.test_logger('sp_tree_zs is %s' % (sp_tree_zs))

            test_util.test_logger('compare the 2 sp lists - %s and %s' % (sp_tree_actual, sp_tree_zs))
            sp_covered = 0

            if len(sp_tree_actual) != len(sp_tree_zs):
                test_util.test_logger('%s is not same length as %s' % (sp_tree_actual, sp_tree_zs))
                return self.judge(False)

            for i in sp_tree_actual:
                if i in sp_tree_zs:
                    sp_covered = 1
                    test_util.test_logger('%s is in zs sp list %s' % (i, sp_tree_zs))
                    if i == sp_tree_actual[-1]:
                        test_util.test_logger('all the items in %s are in zs sp list %s' % (sp_tree_actual, sp_tree_zs))
                    continue
                elif i not in sp_tree_zs:
                    sp_covered = 0
                    test_util.test_logger('%s is not in zs sp list %s' % (i, sp_tree_zs))
                    return self.judge(False)

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

        elif ps.type == "LocalStorage":
            for snapshot in snapshots:
                backing_list = []
                backing_file = ''
                sp_covered = 0
                activate_host = ''

                devPath = snapshot.get_snapshot().primaryStorageInstallPath

                for i in sp_tree_actual:
                    if devPath in i:
                        test_util.test_logger('%s already in sp list %s' % (devPath, backing_list))
                        sp_covered = 1

                if sp_covered == '1':
                    continue
                else:
                    test_util.test_logger('%s not in current sp list, start checking its backing chain' % (devPath))

                backing_list.append(devPath)

                cmd_info = "ls %s" % devPath

                for host in test_lib.lib_find_hosts_by_ps_uuid(ps_uuid):
                    result = test_lib.lib_execute_ssh_cmd(host.managementIp, 'root', 'password', cmd_info)
                    if result:
                        activate_host = host.managementIp
                        break

                if not activate_host:
                    test_util.test_logger('No activate host found for %s' % (snapshot))
                    return self.judge(self.exp_result)

                while True:
                    cmd_info = "ls %s" % devPath

                    result = test_lib.lib_execute_ssh_cmd(activate_host, 'root', 'password', cmd_info)
                    if result:
                        backing_file = get_qcow_backing_file_by_ip(devPath, activate_host)
                    else:
                        test_util.test_logger('No activate host found for %s' % (snapshot))
                        return self.judge(self.exp_result)
                    backing_file = backing_file.replace("\n", "")

                    if not backing_file:
                        if volume_obj.get_volume().type == 'Root':
                            test_util.test_logger('%s is against the Root volume, need to pop up the image cache %s' % (snapshot, devPath))
                            backing_list.pop()
                        break
                    else:
                        backing_list.append(backing_file)
                        devPath = backing_file

                backing_list = list(reversed(backing_list))

                if not sp_tree_actual:
                    test_util.test_logger('current sp list is empty, add %s into it' % (backing_list))
                    sp_tree_actual.append(backing_list)
                    continue

                for i in sp_tree_actual:
                    if backing_list == i:
                        sp_covered = 1

                if sp_covered == '1':
                    test_util.test_logger('%s already in current sp list %s, no need to add it anymore' % (backing_list, sp_tree_actual))
                    continue
                else:
                    test_util.test_logger('%s not in current sp list %s, start comparing detailed list items' % (backing_list, sp_tree_actual))

                for i in sp_tree_actual:
                    count = min(len(backing_list), len(i)) - 1
                    tmp_count = 0
                    while tmp_count <= count:
                        if backing_list[tmp_count] == i[tmp_count]:
                            tmp_count += 1
                            sp_covered = 1
                            continue
                        elif backing_list[tmp_count] != i[tmp_count]:
                            sp_covered = 0
                            break

                    if sp_covered == 0:
                        if i == sp_tree_actual[-1]:
                            test_util.test_logger('%s not in current sp list %s, add it into sp list' % (backing_list, sp_tree_actual))
                            sp_tree_actual.append(backing_list)
                            break
                    elif sp_covered == 1 and len(backing_list) > len(i):
                        test_util.test_logger('%s is the superset of the list %s in current sp list %s, update current sp list' % (backing_list, i, sp_tree_actual))
                        sp_tree_actual.remove(i)
                        sp_tree_actual.append(backing_list)
                        break
                    elif sp_covered == 1 and len(backing_list) <= len(i):
                        test_util.test_logger('%s already in current sp list %s, no need to add it anymore' % (backing_list, sp_tree_actual))
                        break

            test_util.test_logger('sp_tree_actual is %s' % (sp_tree_actual))
        
            vol_trees = test_lib.lib_get_volume_snapshot_tree(volume_uuid)
            tree_allowed_depth = cfg_ops.get_global_config_value('volumeSnapshot', \
                    'incrementalSnapshot.maxNum')

            for vol_tree in vol_trees:
                tree = json.loads(jsonobject.dumps(vol_tree))['tree']

                for leaf_node in get_leaf_nodes(tree):
                    backing_list = []
                    backing_file = ''
                    current_node = ''

                    backing_file = leaf_node['inventory']['primaryStorageInstallPath']
                    backing_list.append(backing_file.encode('utf-8'))
                    current_node = leaf_node

                    while True:
                        parent_node = get_parent_node(tree, current_node)

                        if not parent_node:
                            break

                        backing_file = parent_node['inventory']['primaryStorageInstallPath']
                        backing_list.append(backing_file.encode('utf-8'))

                        if parent_node.has_key('parentUuid'):
                            current_node = parent_node
                            continue
                        else:
                            break

                    backing_list = list(reversed(backing_list))
                    sp_tree_zs.append(backing_list)

            test_util.test_logger('sp_tree_zs is %s' % (sp_tree_zs))

            test_util.test_logger('compare the 2 sp lists - %s and %s' % (sp_tree_actual, sp_tree_zs))
            sp_covered = 0

            if len(sp_tree_actual) != len(sp_tree_zs):
                test_util.test_logger('%s is not same length as %s' % (sp_tree_actual, sp_tree_zs))
                return self.judge(False)

            for i in sp_tree_actual:
                if i in sp_tree_zs:
                    sp_covered = 1
                    test_util.test_logger('%s is in zs sp list %s' % (i, sp_tree_zs))
                    if i == sp_tree_actual[-1]:
                        test_util.test_logger('all the items in %s are in zs sp list %s' % (sp_tree_actual, sp_tree_zs))
                    continue
                elif i not in sp_tree_zs:
                    sp_covered = 0
                    test_util.test_logger('%s is not in zs sp list %s' % (i, sp_tree_zs))
                    return self.judge(False)
            

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

def get_parent_node(tree, node):
    '''
    return parent node for a node
    '''

    if not tree:
        return 0

    if not node.has_key('parentUuid'):
        return 0

    parent_node = ''

    if node['parentUuid'] != tree['inventory']['uuid']:
        if tree['children']:
            for child in tree['children']:
                result = get_parent_node(child, node)
                if result:
                    parent_node = result
        else:
            return
    elif node['parentUuid'] == tree['inventory']['uuid']:
        parent_node = tree

    return parent_node

def get_leaf_nodes(tree):
    '''
    return all the leaf nodes of a tree
    '''
    if not tree:
        return 0

    leaf_nodes = []

    if not tree.has_key('children'):
        test_util.test_fail('Snapshot tree has invalid format, it does not has key for children.')

    if tree['children']:
        for child in tree['children']:
            leaf_node = get_leaf_nodes(child)
            for i in leaf_node:
                leaf_nodes.append(i)
    else:
        leaf_nodes.append(tree)

    return leaf_nodes

def get_qcow_backing_file_by_ip(installPath, hostIp):
    '''
    get backing file with given install Path
    '''

    cmd = 'qemu-img info %s | grep "backing file:" | awk \'{print $3}\'' % installPath
    return test_lib.lib_execute_ssh_cmd(hostIp, 'root', 'password', cmd)

def get_snaps_for_raw_by_ip(installPath, hostIp):
    '''
    return all the snapshots for a given volume Path via Host IP
    '''

    snaps = []
    cmd_lines = 'rbd snap ls %s | wc -l' % installPath
    rsp = test_lib.lib_execute_ssh_cmd(hostIp, 'root', 'password', cmd_lines)

    if rsp:
        lines = int(rsp)
        i = 2
        while i <= lines:
            cmd = 'rbd snap ls %s | sed -n %s\'p\' | awk \'{print $2}\'' % (installPath, i)
            result = test_lib.lib_execute_ssh_cmd(hostIp, 'root', 'password', cmd)
            snaps.append(result)
            i += 1
    elif not rsp:
        return 0

    return snaps
