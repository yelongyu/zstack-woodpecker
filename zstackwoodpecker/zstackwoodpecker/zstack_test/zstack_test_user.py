'''
zstack user test class

@author: Youyk
'''
import zstackwoodpecker.header.user as user_header
import zstackwoodpecker.operations.account_operations as acc_ops

class ZstackTestUser(user_header.TestUser):

    def __init__(self):
        self.username = None
        self.password = None
        self.session_uuid = None
        super(ZstackTestUser, self).__init__()

    def create(self, username, password, session_uuid):
        self.set_user(acc_ops.create_user(username, password, session_uuid))
        self.username = username
        self.password = password
        self.session_uuid = session_uuid
        super(ZstackTestUser, self).create()

    def delete(self):
        acc_ops.delete_user(self.get_user().uuid, self.session_uuid)
        super(ZstackTestUser, self).delete()

    def check(self):
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestUser, self).check()
