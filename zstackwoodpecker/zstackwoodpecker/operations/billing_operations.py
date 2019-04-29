'''

All zstack billing operations

@author: Mirabel
'''
import os

import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import account_operations
import zstackwoodpecker.test_util as test_util

def calculate_account_spending(account_uuid, date_start=None, date_end=None, session_uuid = None):
    action = api_actions.CalculateAccountSpendingAction()
    action.accountUuid = account_uuid
    action.dateStart = date_start
    action.dateEnd = date_end
    test_util.action_logger('Calculate account spending, uuid: %s' \
            % (account_uuid))
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result

def delete_resource_price(price_uuid, delete_mode = None, session_uuid = None):
    action = api_actions.DeleteResourcePriceAction()
    action.uuid = price_uuid
    action.deleteMode = delete_mode
    test_util.action_logger('Delete resource price uuid: %s' \
            % (price_uuid))                       
    result = account_operations.execute_action_with_session(action, \
            session_uuid)                         
    return result                                 

def create_resource_price(resource_name, time_unit, price, system_tags = None, resource_unit = None, date_in_long = None, account_uuid = None, session_uuid = None):
    action = api_actions.CreateResourcePriceAction()
    action.resourceName = resource_name
    action.timeUnit = time_unit
    action.price = price
    action.resourceUnit = resource_unit
    action.dateInLong = date_in_long
    action.accountUuid = account_uuid
    action.systemTags = system_tags
    test_util.action_logger('Create resource %s price %s, date in long: %s' \
            % (resource_name, price, date_in_long))
    result = account_operations.execute_action_with_session(action, \
            session_uuid)

    return result.inventory

def query_resource_price(cond, session_uuid= None):
    action = api_actions.QueryResourcePriceAction()
    action.conditions = cond
    result = account_operations.execute_action_with_session(action, \
            session_uuid)
    return result

def generate_account_billing(account_uuid, session_uuid=None):
    action = api_actions.GenerateAccountBillingAction()
    action.accountUuid = account_uuid
    result = account_operations.execute_action_with_session(action, \
            session_uuid)
    return result
