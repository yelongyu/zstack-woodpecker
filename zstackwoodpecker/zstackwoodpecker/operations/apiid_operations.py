'''

api id related operations for setup zstack test.

@author: SyZhao
'''

import apibinding.api_actions as api_actions
from apibinding import api
import os
import sys
import traceback
import zstackwoodpecker.test_util as test_util



def ret_id_add_iso_template(image_creation_option):
    '''
    Add iso template
    '''
    action = api_actions.AddImageAction()
    action.name = image_creation_option.get_name()
    action.guest_os_type = image_creation_option.get_guest_os_type()
    action.mediaType = 'ISO'

    action.backupStorageUuids = \
            image_creation_option.get_backup_storage_uuid_list()
    action.bits = image_creation_option.get_bits()
    action.description = image_creation_option.get_description()
    action.format = 'iso'
    action.url = image_creation_option.get_url()
    action.timeout = image_creation_option.get_timeout()
    test_util.action_logger('Add ISO Template from url: %s in [backup Storage:] %s' % (action.url, action.backupStorageUuids))
    apiId = __execute_action_with_session(action, image_creation_option.get_session_uuid())
    return apiId


def ret_id_add_root_volume_template(image_creation_option):
    '''
    Add root volume template
    '''
    action = api_actions.AddImageAction()
    action.name = image_creation_option.get_name()
    action.guest_os_type = image_creation_option.get_guest_os_type()
    action.mediaType = 'RootVolumeTemplate'
    if image_creation_option.get_mediaType() and \
            action.mediaType != image_creation_option.get_mediaType():
        test_util.test_warn('image type %s was not %s' % \
                (image_creation_option.get_mediaType(), action.mediaType))

    action.backupStorageUuids = \
            image_creation_option.get_backup_storage_uuid_list()
    action.bits = image_creation_option.get_bits()
    action.description = image_creation_option.get_description()
    action.format = image_creation_option.get_format()
    if image_creation_option.get_system_tags() != None:
        action.systemTags = image_creation_option.get_system_tags().split(',')
    action.url = image_creation_option.get_url()
    action.timeout = image_creation_option.get_timeout()
    test_util.action_logger('Add Root Volume Template from url: %s in [backup Storage:] %s' % (action.url, action.backupStorageUuids))
    apiId = __execute_action_with_session(action, image_creation_option.get_session_uuid())
    return apiId


def __execute_action_with_session(action, session_uuid):
    if session_uuid:
        action.sessionUuid = session_uuid
        evt = __async_call(action, session_uuid)
    else:
        session_uuid = __login_as_admin()
        try:
            action.sessionUuid = session_uuid
            evt = __async_call(action, session_uuid)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise e
        finally:
            __logout(session_uuid)

    return evt


def __async_call(apicmd, session_uuid):
    api = Api(host=os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_IP'),
              port=os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_PORT'))
    api.set_session_to_api_message(apicmd, session_uuid)
    apiIp = api.async_call_no_wait(apicmd)
    return apiIp


def __login_as_admin():
    api = Api(host=os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_IP'),
              port=os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_PORT'))
    return api.login_as_admin()


def __logout(session_uuid):
    api = Api(host=os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_IP'),
              port=os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_PORT'))
    api.log_out(session_uuid)

