import zstackwoodpecker.header.checker as checker_header

class zstack_kvm_host_checker(checker_header.TestChecker):
    def check(self):
        super(zstack_kvm_host_checker, self).check()
        self.judge(self.exp_result)
