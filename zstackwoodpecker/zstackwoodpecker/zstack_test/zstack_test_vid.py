'''
zstack iam2 virtual id test class

@author: Glody 
'''
import zstackwoodpecker.header.vid as vid_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.iam2_operations as iam2_ops

class ZstackTestVid(vid_header.TestVid):

    def __init__(self):
        self.vid_creation_option = test_util.VidOption()
        self.vid = None
        self.session_uuid = None
        super(ZstackTestVid, self).__init__()

    def create(self, name, password, session_uuid=None, without_default_role="false"):
        if without_default_role == "true":
            self.set_vid(iam2_ops.create_iam2_virtual_id(name, password, session_uuid, without_default_role="true"))
        else:
            self.set_vid(iam2_ops.create_iam2_virtual_id(name, password, session_uuid))
        self.session_uuid = session_uuid
        super(ZstackTestVid, self).create()

    def delete(self):
        iam2_ops.delete_iam2_virtual_id(self.get_vid().uuid, self.session_uuid)
        super(ZstackTestVid, self).delete()

    def check(self):
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestVid, self).check()

    def set_creation_option(self, vid_creation_option):
        self.vid_creation_option = vid_creation_option

    def get_vid_option(self):
        return self.vid_creation_option
