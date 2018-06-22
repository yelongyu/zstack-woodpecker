'''
test iam2 platform admin related zone


@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    global test_obj_dict

    # need at least 2 zones
    zones_inv = res_ops.query_resource(res_ops.ZONE)
    if len(zones_inv) < 2:
        test_util.test_skip('test need at least 2 zones')

    zone1_uuid = zones_inv[0].uuid
    zone2_uuid = zones_inv[1].uuid

    iam2_ops.clean_iam2_enviroment()

    username = 'username'
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    platform_admin_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    attributes = [{"name": "__PlatformAdmin__"}, {"name": "__PlatformAdminRelatedZone__", "value": zone1_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(platform_admin_uuid, attributes)

    username2 = 'username2'
    password2 = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    platform_admin2_uuid = iam2_ops.create_iam2_virtual_id(username2, password2).uuid
    attributes = [{"name": "__PlatformAdmin__"}, {"name": "__PlatformAdminRelatedZone__", "value": zone2_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(platform_admin2_uuid, attributes)

    zone1_cluster = []
    zone2_cluster = []
    cond = res_ops.gen_query_conditions('zoneUuid', '=', zone1_uuid)
    cluster_inv = res_ops.query_resource(res_ops.CLUSTER, cond)
    for cluster in cluster_inv:
        zone1_cluster.append(cluster.uuid)

    cond = res_ops.gen_query_conditions('zoneUuid', '=', zone2_uuid)
    cluster_inv = res_ops.query_resource(res_ops.CLUSTER, cond)
    for cluster in cluster_inv:
        zone2_cluster.append(cluster.uuid)

    platform_admin_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
    cluster_list = res_ops.query_resource(res_ops.CLUSTER, session_uuid=platform_admin_session_uuid)
    for cluster in cluster_list:
        if cluster.uuid not in zone1_cluster:
            test_util.test_fail("can't get zone1:[%s] cluster [%s]" % (zone1_uuid, cluster.uuid))
        if cluster.uuid in zone2_cluster:
            test_util.test_fail(
                "platformadmin has no permission get zone2:[%s] cluster [%s]" % (zone2_uuid, cluster.uuid))

    zone1_hosts = []
    zone2_hosts = []
    cond = res_ops.gen_query_conditions('zoneUuid', '=', zone1_uuid)
    hosts_inv = res_ops.query_resource(res_ops.HOST, cond)
    for host in hosts_inv:
        zone1_hosts.append(host.uuid)

    cond = res_ops.gen_query_conditions('zoneUuid', '=', zone2_uuid)
    hosts_inv = res_ops.query_resource(res_ops.HOST, cond)
    for host in hosts_inv:
        zone2_hosts.append(host.uuid)

    host_list = res_ops.query_resource_fields(res_ops.HOST, session_uuid=platform_admin_session_uuid)
    for host in host_list:
        if host.uuid not in zone1_hosts:
            test_util.test_fail("can't get zone1:[%s] host [%s]" % (zone1_uuid, host.uuid))
        if host.uuid in zone2_hosts:
            test_util.test_fail("platformadmin has no permission get zone2:[%s] host [%s]" % (zone2_uuid, host.uuid))

    vm = test_stub.create_vm(session_uuid=platform_admin_session_uuid)
    test_obj_dict.add_vm(vm)
    vm_uuid = vm.get_vm().uuid
    volume = test_stub.create_volume(session_uuid=platform_admin_session_uuid)
    test_obj_dict.add_volume(volume)
    volume_uuid = volume.get_volume().uuid
    acc_ops.logout(platform_admin_session_uuid)

    platform_admin2_session_uuid = iam2_ops.login_iam2_virtual_id(username2, password2)
    # TODO:there is a bug below this operation ZSTAC-13105
    # vm_inv=res_ops.query_resource(res_ops.VM_INSTANCE,session_uuid=platform_admin2_session_uuid)
    # if vm_inv:
    #     if vm_inv.uuid == vm_uuid:
    #         test_util.test_fail("zone2:[%s] platformadmin can't query zone1 vm "%zone2_uuid)

    volume_inv = res_ops.query_resource(res_ops.VOLUME, session_uuid=platform_admin2_session_uuid)
    if volume_inv:
        if volume_inv[0].uuid == volume_uuid:
            test_util.test_fail("zone2:[%s] platformadmin can't query zone1 volume " % zone2_uuid)

    test_lib.lib_robot_cleanup(test_obj_dict)
    iam2_ops.clean_iam2_enviroment()

    test_util.test_pass('success test iam2 login in by admin!')


def error_cleanup():
    global test_obj_dict
    test_lib.lib_robot_cleanup(test_obj_dict)
    iam2_ops.clean_iam2_enviroment()
