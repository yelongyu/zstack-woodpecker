import os
import socket
import apibinding.api as api
import apibinding.inventory as inventory
import zstacklib.utils.linux as linux
import zstackwoodpecker.operations.resource_operations as res_ops

def is_management_node_ready(node_uuid):
    try:
        apicmd = inventory.APIIsReadyToGoMsg()
        api_client = api.Api(host = os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_IP'))
        api_client.managementNodeId = node_uuid
        (name, event) = api_client.async_call_wait_for_complete(apicmd, exception_on_error=False, interval=1000)
        if not event.success:
            print('management node is still not ready ...')
        else:
            print('management node is ready !')

        return event.success
    except socket.error as e:
        print('%s, tomcat is still starting ... ' % str(e))
        return False

def wait_for_management_server_start(wait_start_timeout=120, \
        node_uuid=None):
    if not linux.wait_callback_success(is_management_node_ready, \
            node_uuid, \
            wait_start_timeout, 1, True):
        raise Exception('waiting for management server start up time out\
                after %s seconds' % wait_start_timeout)
    else:
        print('management starts successfully, is running now ...')

def get_management_node_by_host_ip(host_ip):
    '''
    return node inventory if find management node on host
    '''
    cond = res_ops.gen_query_conditions('hostName', '=', host_ip)
    node = res_ops.query_resource(res_ops.MANAGEMENT_NODE, cond)
    return node

def is_management_node_start(host_ip):
    '''
    check whether management node is started on host
    '''
    node = get_management_node_by_host_ip(host_ip)
    if not node:
        print ('No management node on host: %s' % host_ip)
        return False
    else:
        print ('management node: %s is started on host: %s' % \
                (node[0].uuid, host_ip))
        return True

