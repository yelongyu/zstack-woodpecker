'''
zstack account test class

@author: Youyk
'''
import zstackwoodpecker.header.account as account_header
import zstackwoodpecker.operations.account_operations as acc_ops

class ZstackTestAccount(account_header.TestAccount):

    def __init__(self):
        self.username = None
        self.password = None
        super(ZstackTestAccount, self).__init__()

    def __repr__(self):
        if self.get_account():
            return "account_%s" % self.get_account().uuid
        else:
            return "account_None"

    def create(self, username, password):
        self.set_account(acc_ops.create_normal_account(username, password))
        self.username = username
        self.password = password
        super(ZstackTestAccount, self).create()

    def delete(self):
        acc_ops.delete_account(self.get_account().uuid)
        super(ZstackTestAccount, self).delete()

    def check(self):
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestAccount, self).check()
