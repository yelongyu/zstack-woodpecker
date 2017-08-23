import zstackwoodpecker.operations.baremetal_operations as bare_operations
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import os

def test():
    pxe_uuid = test_lib.lib_get_pxe_by_name(os.environ.get('pxename')).uuid
    dhcpbegin_2 = os.environ.get('dhcpbegin_2')
    dhcpend_2 = os.environ.get('dhcpend_2')
    dhcpnetmask_2 = os.environ.get('dhcpnetmask_2')
    bare_operations.update_pxe(pxe_uuid=pxe_uuid, begin=dhcpbegin_2, end=dhcpend_2, netmask=dhcpnetmask_2)
    begin = test_lib.lib_get_pxe_by_name(os.environ.get('pxename')).dhcpRangeBegin
    end = test_lib.lib_get_pxe_by_name(os.environ.get('pxename')).dhcpRangeEnd
    netmask = test_lib.lib_get_pxe_by_name(os.environ.get('pxename')).dhcpRangeNetmask
    if dhcpbegin_2 != begin or dhcpend_2 != end or dhcpnetmask_2 != netmask:
        test_util.test_fail('Update PXE failed')
    test_util.test_pass('Update PXE Test Success')

def error_cleanup():
    pass
