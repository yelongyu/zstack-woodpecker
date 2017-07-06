import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub

def test():
    test_stub.create_pxe()
    test_util.test_pass('Create PXE Test Success')

def error_cleanup():
    pass

