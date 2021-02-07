import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acct_ops
import zstackwoodpecker.test_util as test_util

vm = None
host1_uuid = None
host2_uuid = None


def add_ceph_backup_storage(name, mon_urls, pool_name, system_tags=None, session_uuid=None):
    action = api_actions.AddCephBackupStorageAction()
    action.name = name
    action.monUrls = mon_urls
    action.importImages = "true"
    action.poolName = pool_name
    if system_tags:
        action.systemTags = system_tags

    evt = acct_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory


def test():
    # query zone
    zone = res_ops.query_resource(res_ops.ZONE)[0]

    # query old ceph_bs
    cond = res_ops.gen_query_conditions("type", "=", "Ceph")
    ceph_bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
    if not ceph_bss:
        test_util.test_skip("This env do not have ceph bs .Skip it")

    ceph_bs = ceph_bss[0]
    old_ceph_uuid = ceph_bs.uuid

    mon_user = ceph_bs.mons[0].sshUsername
    mon_password = ceph_bs.mons[0].sshPassword
    mon_port = ceph_bs.mons[0].sshPort
    mon_ip = ceph_bs.mons[0].monAddr
    mon_pool_name = ceph_bs.poolName

    mon_url = "%s:%s@%s:%s" % (mon_user, mon_password, mon_ip, mon_port)
    data_cidr_tag = "backupStorage::data::network::cidr::172.24.0.0/24"

    # delete_old ceph_bs
    bs_ops.delete_backup_storage(old_ceph_uuid)

    # create ceph backupstorage
    new_ceph_bs = add_ceph_backup_storage("ceph_bs_with_data_cidr", [mon_url], mon_pool_name, [data_cidr_tag])

    # attch ceph_bs -> zone
    bs_ops.attach_backup_storage(new_ceph_bs.uuid, zone.uuid)



def error_cleanup():
    pass


def env_recover():
    pass
