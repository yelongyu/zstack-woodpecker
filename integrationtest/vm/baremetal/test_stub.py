import zstackwoodpecker.operations.baremetal_operations as bare_operations
import zstackwoodpecker.test_util as test_util
import os

def create_pxe(pxe_option=None, session_uuid=None):
    if not pxe_option:
    	pxe_option = test_util.PxeOption()
    	pxe_option.set_dhcp_interface(os.environ.get('pxe_interface'))
    	pxe_option.set_dhcp_range_end(os.environ.get('dhcp_end'))
    	pxe_option.set_dhcp_range_begin(os.environ.get('dhcp_begin'))
    	pxe_option.set_dhcp_netmask(os.environ.get('dhcp_netmask'))
    if session_uuid:
        pxe_option.set_session_uuid(session_uuid)
    bare_operations.create_pxe(pxe_option)

