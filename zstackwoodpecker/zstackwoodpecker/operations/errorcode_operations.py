'''

All errorcode operations for test.

@author: Glody
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import os

def get_elaborations(category = None, regex = None, systemtags = None, session_uuid = None):
    action = api_actions.GetElaborationsAction()
    action.category = category
    action.regex = regex
    action.systemTags = systemtags
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Get Elaborations:] %s %s succeed.' % (category, regex))
    return evt.contents

def get_elaboration_categories(systemtags = None, session_uuid = None):
    action = api_actions.GetElaborationCategoriesAction()
    action.systemTags = systemtags
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('Get Elaborations Categories Succeed.')
    return evt.categories

def get_missed_elaboration(repeats = None, starttime = None, systemtags = None, session_uuid = None):
    action = api_actions.GetMissedElaborationAction()
    action.repeats = repeats
    action.startTime = starttime
    action.systemTags = systemtags
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('Get Missed Elaborations Succeed.' )
    return evt.inventories

def reload_elaboration(session_uuid = None):
    action = api_actions.ReloadElaborationAction()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('Relead Elaborations Succeed.' )

def check_elaboration_content(elaborate_file, systemtags = None, session_uuid = None):
    action = api_actions.CheckElaborationContentAction()
    action.elaborateFile = elaborate_file
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Check Elaboration Content:] %s Succeed.'%elaborate_file )
    return evt.results
