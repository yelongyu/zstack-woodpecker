'''

All zstack billing operations

@author: Mirabel
'''
import os

import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import account_operations
import zstackwoodpecker.test_util as test_util

def calculate_account_spending(account_uuid, session_uuid = None):
    action = api_actions.CalculateAccountSpendingAction()
    action.accountUuid = account_uuid
    test_util.action_logger('Calculate account spending, uuid: %s' \
            % (account_uuid))
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result

def delete_resource_price(resource_name, date_in_long, delete_mode = None, session_uuid = None):
    action = api_actions.DeleteResourcePriceAction()
    action.resourceName = resource_name
    action.dateInLong = date_in_long
    action.deleteMode = delete_mode
    test_util.action_logger('Delete resource %s price, date in long: %s' \
            % (resource_name, date_in_long))
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result

def create_resource_price(resource_name, time_unit, price, resource_unit = None, date_in_long = None, account_uuid = None, session_uuid = None):
    action = api_actions.CreateResourcePriceAction()
    action.resourceName = resource_name
    action.timeUnit = time_unit
    action.price = price
    action.resourceUnit = resource_unit
    action.dateInLong = date_in_long
    action.accountUuid = account_uuid
    test_util.action_logger('Create resource %s price %s, date in long: %s' \
            % (resource_name, price, date_in_long))
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result.inventory

def query_resource_price(resource_name, session_uuid = None):
    action = api_actions.QueryResourcePriceAction()
    action.resourceName = resource_name
    test_util.action_logger('Query resource %s price' % (resource_name))
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result.inventories
