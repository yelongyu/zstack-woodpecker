import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

image1 = None
image2 = None
disconnect = False
host = None


def test():
    global disconnect, host, image1, image2
    # query&get clusters
    cond = res_ops.gen_query_conditions('name', '=', "cluster1")
    cluster1 = res_ops.query_resource(res_ops.CLUSTER, cond)[0]

    cond = res_ops.gen_query_conditions('name', '=', "cluster2")
    cluster2 = res_ops.query_resource(res_ops.CLUSTER, cond)[0]

    # query&get hosts
    cond = res_ops.gen_query_conditions('clusterUuid', '=', cluster1.uuid)
    cluster1_host = res_ops.query_resource(res_ops.HOST, cond)

    cond = res_ops.gen_query_conditions('clusterUuid', '=', cluster2.uuid)
    cluster2_host = res_ops.query_resource(res_ops.HOST, cond)

    # query bs
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE)

    # disconnect mn_host1
    host = cluster1_host[0]
    host_ops.update_kvm_host(host.uuid, 'username', "root1")
    try:
        host_ops.reconnect_host(host.uuid)
    except:
        test_util.test_logger("host: [%s] is disconnected" % host.uuid)
    disconnect = True

    url = "http://172.20.1.22/mirror/diskimages/zstack_image_test3.qcow2"

    # add image to bs1
    img_option = test_util.ImageOption()
    img_option.set_name("bs1_image")
    img_option.set_url(url)
    img_option.set_format('qcow2')
    img_option.set_mediaType = 'RootVolumeTemplate'

    img_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_inv = img_ops.add_root_volume_template(img_option)
    image1 = zstack_image_header.ZstackTestImage()
    image1.set_image(image_inv)

    # add image to bs2
    img_option.set_name("bs2_image")
    img_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_inv = img_ops.add_root_volume_template(img_option)
    image2 = zstack_image_header.ZstackTestImage()
    image2.set_image(image_inv)

    image1.clean()
    image2.clean()

    host_ops.update_kvm_host(host.uuid, 'username', "root")
    host_ops.reconnect_host(host.uuid)


def error_cleanup():
    global host, disconnect, image1, image2
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False

    if image1:
        image1.clean()

    if image2:
        image2.clean()


def env_recover():
    global host, disconnect, image1, image2
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False

    if image1:
        image1.clean()

    if image2:
        image2.clean()
