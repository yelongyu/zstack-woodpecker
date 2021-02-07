'''

New Integration Test for checking the mysql host password

@author: ye.tian 2018-10-08
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops
import os
import MySQLdb as mdb


_config_ = {
        'timeout' : 360,
        'noparallel' : False
        }

default_mode = None
zstack_management_ip = os.environ.get('zstackManagementIp')
password1 = os.environ.get('hostPassword')
con = None
def test():
    global default_mode
    global default_mode1
    global password, password1, pswd 
    default_mode = conf_ops.change_global_config('encrypt', 'enable.password.encrypt', 'true')
    pswd = 'zstack.mysql.password'
    try: 
        con = mdb.connect(host='localhost', user='root', passwd=pswd, db='zstack')
        cur = con.cursor()
        cur.execute('select * from KVMHostVO')
	rs = cur.fetchone()
        password = list(rs)[2]
    finally:
        if con:
	    con.close()
    if password == password1 : 
        test_util.test_fail('test fail mysql HOST password ')
    else:
        default_mode1 = conf_ops.change_global_config('encrypt', 'enable.password.encrypt', 'false')
        test_util.test_pass('Test check the host password mysql test Success')
#Will be called only if exception happens in test().
def error_cleanup():
    conf_ops.change_global_config('encrypt', 'enable.password.encrypt', 'false')
