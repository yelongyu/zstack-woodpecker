#!/usr/bin/python
'''
ZStack integration automation test tool. It includes building, deployment and 
test.

The complexity test combination is recommmended to manually edit test case 
config file, like zstack-woodpecker/integrationtest/vm/basic/integration.xml 
and run it by `zstack-woodpecker -f integration.xml`. 

Author: yyk
'''

import os
import sys
import imp
import optparse
import tempfile
import xml.etree.cElementTree as etree
import subprocess

TEST_CASE_SIGN = "grep 'def test()'"
INTEGRATION_TEST_FOLDER = 'integrationtest/vm/'
#IGNORE_SUITE_LIST = ['poc', 'stress', 'simulator']
#IGNORE_SUITE_LIST = ['poc', 'simulator']
IGNORE_SUITE_LIST = []
INTEGRATION_TEST_CONFIG = 'integration.xml'
SUITE_SETUP_CASE_NAME = 'suite_setup.py'
SUITE_TEARDOWN_CASE_NAME = 'suite_teardown.py'
DEPLOYER_SCRIPT = 'deploy_zstack.sh'
CATALINA_ROOT = 'apache-tomcat'
SANITYTEST_ROOT = 'sanitytest'
ZSTACK_WAR = 'zstack.war'
ZSTACK_PROPERTIES = 'conf/zstack.properties'
CATALINA_OPTS = "-Djava.net.preferIPv4Stack=true" 
CATALINA_DEBUG_OPTS = "-Xdebug -Xnoagent -Djava.compiler=NONE -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=5005"
CONFIG_XML='config_xml'
LOCAL_CONFIG_FOLDER = '%s/.zstackwoodpecker/%s' % \
        (os.path.expanduser('~'), INTEGRATION_TEST_FOLDER)
TEST_CONFIG_FILE = 'test-config.xml'

def set_env_param(debug):
    '''
    Set system environment for later build and test usage.
    '''
    if debug:
        catalina_opts = "%s %s" % (CATALINA_OPTS, CATALINA_DEBUG_OPTS)
    else:
        catalina_opts = CATALINA_OPTS

    os.environ['CATALINA_OPTS'] = catalina_opts

class TestExc(Exception):
    '''
    ZStack Test Exception.
    '''
    pass

class TestCase(object):
    '''
    The Class to save test case information.
    '''
    def __init__(self):
        self.rla_path = None
        self.suite = None
        self.special = False
        self.setup_case = False
        self.teardown_case = False
        self.flavors = []

    def analyze_test_case(self, candidate):
        self.rla_path = candidate
        self.suite = candidate.split('/')[0]
        if os.path.basename(candidate) == SUITE_SETUP_CASE_NAME:
            self.setup_case = self.rla_path
            self.special = True
        else:
            self.setup_case = os.path.join(self.suite, SUITE_SETUP_CASE_NAME)
        if os.path.basename(candidate) == SUITE_TEARDOWN_CASE_NAME:
            self.teardown_case = self.rla_path
            self.special = True
        else:
            self.teardown_case = os.path.join(self.suite, SUITE_TEARDOWN_CASE_NAME)

    def is_special_case(self):
        return self.special

    def is_setup(self):
        return self.rla_path == self.setup_case

    def is_teardown(self):
        return self.rla_path == self.teardown_case

    def get_name_with_suite(self):
        '''
        return the name of test case: suite/case
        '''
        return self.rla_path

    def get_name(self):
        '''
        only return test case name without suite name
        '''
        return self.rla_path[len(self.suite) + 1:]

    def get_suite(self):
        return self.suite

    def get_flavor(self):
        return True if self.flavors else False

    def set_flavor(self, flavor):
        self.flavors.insert(0, flavor)

class TestLib(object):
    '''
    A main class to find, orgnize test cases and will prepare test case config.
    '''

    def __init__(self):
        self.current_dir = None
        self.test_case_dir = None
        self.test_case_lib = {}
        self.exclude_case_list = []
        self.target_case_list = []
        self.suite_list = []
        self.test_xml = None
        self.all_cases_name = []
        self.all_cases_name_no_exclude = []

    def set_test_dir(self, test_dir):
        self.test_case_dir = os.path.join(test_dir, INTEGRATION_TEST_FOLDER)
        if not os.path.isdir(self.test_case_dir):
            raise TestExc('Integration Test Folder does not exist: %s' % self.test_case_dir)

    def set_current_dir(self, current_dir):
        self.current_dir = current_dir

    def find_test_case(self):
        def _is_test_case(candidate):
            ret = os.system('%s %s >/dev/null 2>&1' % (TEST_CASE_SIGN, candidate))
            if ret == 0:
                return True
            return False

        def _new_find_cases(test_dir):
            shell_cmd = "find %s -name '*.py' -exec grep -l \
                    'def test()' {} \;|sort" % test_dir

            import commands
            test_results = commands.getstatusoutput(shell_cmd)
            if test_results[0] == 0 :
                for file_ in test_results[1].split():
                    file_path = os.path.join(test_dir, file_)
                    case = TestCase()
                    case.analyze_test_case(file_path[len(self.test_case_dir):])
                    if case.get_suite() in IGNORE_SUITE_LIST:
                        continue
                    case_suite = case.get_suite()
                    if not case_suite in self.suite_list:
                        self.suite_list.append(case_suite)
                    test_case_list.append(case)
                    #self.test_case_lib[len(self.test_case_lib) + 1] = case


        def _find_cases(test_dir):
            files = os.listdir(test_dir)
            files.sort()
            for file_ in files:
                file_path = os.path.join(test_dir, file_)
                if os.path.isdir(file_path):
                    _find_cases(file_path)
                else:
                    if file_.endswith('.py'):
                        if _is_test_case(file_path):
                            case = TestCase()
                            case.analyze_test_case(file_path[len(self.test_case_dir):])
                            if case.get_suite() in IGNORE_SUITE_LIST:
                                continue
                            case_suite = case.get_suite()
                            if not case_suite in self.suite_list:
                                self.suite_list.append(case_suite)
                            test_case_list.append(case)
                            #self.test_case_lib[len(self.test_case_lib) + 1] = case
 
        if not self.test_case_dir:
            raise TestExc('Need to set test folder by TestLib.set_test_dir() firstly')
    
        test_case_list = []
        #_find_cases(self.test_case_dir)
        _new_find_cases(self.test_case_dir)
        test_case_num = 1
        for case in test_case_list:
            self.all_cases_name_no_exclude.append(case.get_name_with_suite())
            if str(test_case_num) not in self.exclude_case_list and case.get_name_with_suite() not in self.exclude_case_list:
                self.test_case_lib[test_case_num] = case
                self.all_cases_name.append(case.get_name_with_suite())
            test_case_num += 1
    
    def _find_case_num(self, case_name):
        for num, case in self.test_case_lib.iteritems():
            if case_name == case.get_name_with_suite():
                return num
    def analyze_exclude_case_list(self, case_list):
        if case_list and ',' in case_list:
            temp_cases = case_list.split(',')
            for case in temp_cases:
                if case != '':
                    self.exclude_case_list.append(case)
        else:
            self.exclude_case_list = [case_list]

    def _analyze_case_list(self, case_list):
        def _parase_case_range(case_num_list):
            try:
                case_start_num = int(case_num_list[0])
                case_end_num = int(case_num_list[1])
            except:
                raise TestExc("Detect to use case range '~' to set running cases. But the case number is not correct. It should be '-c Case_Start_Num~Case_End_Num'. Your input is: '-c %s' " % case_list)
            if case_start_num > case_end_num:
                raise TestExc("The StartNum should be smaller than EndNum, when use case range: '-c Case_Start_Num~Case_End_Num'. But your input is '-c %s'" % case_list)
            new_cases = []
            while case_start_num <= case_end_num:
                new_cases.append(str(case_start_num))
                case_start_num += 1

            return new_cases

        if ',' in case_list:
            temp_cases = case_list.split(',')
            cases = []
            for case in temp_cases:
                if case == '':
                    continue
                if '~' in case:
                    cases.extend(_parase_case_range(case.split('~')))
                else:
                    cases.append(case)
        elif '~' in case_list:
            cases = list(_parase_case_range(case_list.split('~')))
        else:
            cases = [case_list]

        for case in cases:
            case = case.strip()
            flavor = None
            if "::" in case:
                case, flavor = case.split("::")
            try:
                if case in self.all_cases_name:
                    case_obj = self.test_case_lib[self._find_case_num(case)]
                    if flavor:
                        if self.exclude_case_list == [None]:
                            case_obj.set_flavor(flavor)
                            self.target_case_list.append(case_obj)
                        elif "{}::{}".format(case.split('/')[-1], flavor) not in [item.split('/')[-1] for item in self.exclude_case_list]:
                            case_obj.set_flavor(flavor)
                            self.target_case_list.append(case_obj)
                    else:
                        self.target_case_list.append(case_obj)
                elif int(case) in self.test_case_lib.keys():
                    self.target_case_list.append(self.test_case_lib[int(case)])
                else:
                    print_warn("Not find test case: %s" % case)

            except ValueError as e:
                #following code will time consuming, so only move in exception.
                for real_case_name in self.all_cases_name:
                    if case in real_case_name:
                        case_obj = self.test_case_lib[self._find_case_num(real_case_name)]
                        if flavor:
                            if self.exclude_case_list == [None]:
                                case_obj.set_flavor(flavor)
                                self.target_case_list.append(case_obj)
                            elif "{}::{}".format(case.split('/')[-1], flavor) not in [item.split('/')[-1] for item in self.exclude_case_list]:
                                case_obj.set_flavor(flavor)
                                self.target_case_list.append(case_obj)
                        else:
                            self.target_case_list.append(case_obj)
                        break
                else:
                    for real_case_name_no_exclude in self.all_cases_name_no_exclude:
			if case in real_case_name_no_exclude:
                            break
                    else:
                        raise TestExc('Not able to find test case: %s in %s' \
                            % (case, self.test_case_dir))

    def print_test_case(self, suiteList=None, caseList=None):
        '''
        List all test cases, or list some test suite's test cases.
        '''
        def _print_head(wt=80):
            print '  \033[1mNo.\t|  \tTest Case\033[0m'
            print '-'*int(wt)

        if caseList:
            self._analyze_case_list(caseList)
            for case in self.target_case_list:
                case_num = self._find_case_num(case.get_name_with_suite())
                test_case_path = os.path.join(self.test_case_dir, case.get_name_with_suite())
                sys.path.append(os.path.dirname(test_case_path))
                test_case = imp.load_source('test_case', test_case_path)
                print '='*80
                _print_head()
                print '  [%s]\t| %s' % (str(case_num), case.get_name_with_suite())
                print '-'*80
                print '\t\t\033[1m Description:\033[0m'
                print '-'*80
                print test_case.__doc__
                print '='*80
                print '\n'

            return

        target_suites = []
        if suiteList:
            suites = suiteList.split(',')
            for suite in suites:
                if suites == '':
                    continue
                suite = suite.strip()
                if suite in self.suite_list:
                    target_suites.append(suite)
                else:
                    for real_suite in self.suite_list:
                        if suite == real_suite[0:len(suite)]:
                            target_suites.append(real_suite)
        else:
            target_suites = self.suite_list

        if not target_suites:
            print_info("Not find test suite name, which is start with '%s'" % suiteList)
            return 

        try:
            ht, wt = os.popen('stty size', 'r').read().split()
        except:
            ht = '57'
            wt = '237'
        print_info('Available ZStack Integration Test Cases:')
        print '='*int(wt)
        _print_head(wt)
        currt_ht = 1
        for i in self.test_case_lib:
            case = self.test_case_lib[i]
            if not case.get_suite() in target_suites:
                continue 

            #if currt_ht > int(ht):
            if currt_ht > 5:
                #_print_head(wt)
                #currt_ht = 4
                currt_ht = 1
                print '-'*int(wt)
                #print '\n'
            if case.is_special_case():
                print '  \033[1m[%s]\t| %s\033[0m' % (str(i), case.get_name_with_suite())
            else:
                print '  [%s]\t| %s' % (str(i), case.get_name_with_suite())
            currt_ht += 1
        print '='*int(wt)

    def assemble_test(self, case_list, auto_complete=None, parallel=None, repeat=None):
        '''
        Assemble test config file, like integration.xml, which could be executed
        as zstack-woodpecker -f config.xml 

        case_list: a string with a serial case name, which is separated by ','
        
        a valid test case name could be test case num, which can be get by -l;
        or a test case name string, include test_suite/sub_suite/case_name.py

        auto_complete: a flag, whether need to add suite_setup and 
        suite_teardown test cases. 
        '''
        root = etree.Element("integrationTest")
        self._analyze_case_list(case_list)

        suite_dict = {}
        if not self.target_case_list:
            print_warn("Did not find available test cases to execute: %s. Quit!" % case_list)
            sys.exit()

        print_info("Following cases will be executed:")
        for case in self.target_case_list:
            if case.get_flavor():
                print "\t{}::{}".format(case.get_name_with_suite(), case.flavors[-1])
            else:
                print "\t%s" % case.get_name_with_suite()
            suite_name = case.get_suite()
            if not suite_name in suite_dict.keys():
                suite = etree.SubElement(root, "suite")
                suite.set("name", "%s" % suite_name)
                suite.set("path", "%s%s" % (self.test_case_dir, suite_name))
                if parallel:
                    suite.set("parallel", "%s" % parallel)
                suite_dict[suite_name] = suite
            else:
                suite = suite_dict[suite_name]

            if case.is_special_case():
                if case.is_setup():
                    suite.set("setupCase", os.path.join(self.test_case_dir, case.get_name_with_suite()))
                else:
                    suite.set("teardownCase", os.path.join(self.test_case_dir, case.get_name_with_suite()))
            else:
                case_e = etree.SubElement(suite, "case")
                if case.get_flavor():
                    case_e.text = os.path.join(self.test_case_dir, "{}::{}".format(case.get_name_with_suite(), case.flavors.pop()))
                else:
                    case_e.text = os.path.join(self.test_case_dir, case.get_name_with_suite())
                if repeat:
                    case_e.set("repeat", "%s" % repeat)

        if auto_complete:
            for suite_name, suite_item in suite_dict.iteritems():
                if not suite_item.get("setupCase"):
                    suite_item.set("setupCase", os.path.join(self.test_case_dir, suite_name, SUITE_SETUP_CASE_NAME))
                    print '\t%s/%s' % (suite_name, SUITE_SETUP_CASE_NAME)
                if not suite_item.get("teardownCase"):
                    suite_item.set("teardownCase", os.path.join(self.test_case_dir, suite_name, SUITE_TEARDOWN_CASE_NAME))
                    print '\t%s/%s' % (suite_name, SUITE_TEARDOWN_CASE_NAME)

        print "\n"
        tree = etree.ElementTree(root)
        #test_workbench = tempfile.mkdtemp(dir=self.current_dir)
        #test_workbench = os.path.join(self.current_dir, 'test_case_config')
        self.test_xml = os.path.join(self.current_dir, CONFIG_XML, "test_case.xml")
        if not os.path.isdir(os.path.dirname(self.test_xml)):
            os.system('mkdir -p %s' % os.path.dirname(self.test_xml))
        tree.write(self.test_xml)

    def execute_test(self, test_args):
        #process = subprocess.Popen("zstack-woodpecker -f %s" % self.test_xml, executable='/bin/sh', shell=True, cwd=self.current_dir, universal_newlines=True)
        woodpecker_root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        if test_args:
            print("export woodpecker_root_path=%s woodpecker_http_proxy=$http_proxy; export woodpecker_https_proxy=$https_proxy; unset http_proxy; unset https_proxy; zstack-woodpecker -f %s %s" % (woodpecker_root_path, self.test_xml, test_args))
            os.system("export woodpecker_root_path=%s woodpecker_http_proxy=$http_proxy; export woodpecker_https_proxy=$https_proxy; unset http_proxy; unset https_proxy; zstack-woodpecker -f %s %s" % (woodpecker_root_path, self.test_xml, test_args))
        else:
            print ("export woodpecker_root_path=%s woodpecker_http_proxy=$http_proxy; export woodpecker_https_proxy=$https_proxy; unset http_proxy; unset https_proxy; zstack-woodpecker -f %s %s" % (woodpecker_root_path, self.test_xml, test_args))
            os.system("export woodpecker_root_path=%s woodpecker_http_proxy=$http_proxy; export woodpecker_https_proxy=$https_proxy; unset http_proxy; unset https_proxy; zstack-woodpecker -f %s %s" % (woodpecker_root_path, self.test_xml, test_args))

    def find_real_suite(self, suite_shortname):
        for real_suite in self.suite_list:
            if suite_shortname == real_suite[0:len(suite_shortname)]:
                return real_suite
        else:
            raise TestExc('Did not find suiteable suite for: %s. Available suites: %s' % (suite_shortname, self.suite_list))

    def restart_zstack(self, suite_name):
        real_suite = self.find_real_suite(suite_name)
        suite_local_test_config = os.path.join(LOCAL_CONFIG_FOLDER, \
                real_suite, TEST_CONFIG_FILE)
        if not os.path.exists(suite_local_test_config):
            suite_local_test_config = os.path.join(self.test_case_dir, \
                    real_suite, TEST_CONFIG_FILE)

        if not os.path.exists(suite_local_test_config):
            raise TestExc('Not find suite test config file: %s' \
                    % suite_local_test_config)

        import zstackwoodpecker.setup_actions as setup_action
        setup_action.restart_zstack_without_deploy_db(suite_local_test_config)
        print_info('ZStack Service Restart Completed')

    def assemble_test_suite(self, suite_list, parallel=None):
        if not os.path.isdir(os.path.join(self.current_dir, CONFIG_XML)):
            os.system('mkdir -p %s' % os.path.join(self.current_dir, CONFIG_XML))

        suites = suite_list.split(',')
        root = etree.Element("integrationTest")
        for suite in suites:
            if suite == '':
                continue
            suite_config = None
            suite = suite.strip()
            real_suite = self.find_real_suite(suite)
            suite_config = os.path.join(self.test_case_dir, real_suite, INTEGRATION_TEST_CONFIG)

            if suite_config:
                new_suite_config = os.path.join(self.current_dir, CONFIG_XML, '%s_%s' % (real_suite, INTEGRATION_TEST_CONFIG))
                os.system('/bin/cp -f %s %s' % (suite_config, new_suite_config))
                suite_content = etree.parse(new_suite_config)
                suite_item = suite_content.find('suite')
                if parallel:
                    suite_item.set('parallel', parallel)
                if suite_item.get('setupCase'):
                    suite_item.set('setupCase', \
                            '%s/%s/%s' % (self.test_case_dir, real_suite, suite_item.get('setupCase')))
                if suite_item.get('teardownCase'):
                    suite_item.set('teardownCase', \
                            '%s/%s/%s' % (self.test_case_dir, real_suite, suite_item.get('teardownCase')))
                suite_item.set("path", "%s/%s" % (self.test_case_dir, suite))
                for case_item in suite_item.getchildren():
                    for exclude_case in self.exclude_case_list:
                        if exclude_case == None:
                            continue
                        if "::" in exclude_case:
                            exclude_case = exclude_case.split("::")[0] + ".py::" + exclude_case.split("::")[1].split('.')[0]
                        if case_item.text == exclude_case or case_item.text == '%s.py' % (exclude_case) or '/%s.py' % (exclude_case) in case_item.text or '/%s' % (case_item.text) in '%s.py' % (exclude_case):
                            suite_item.remove(case_item)
                            break
                    org_case_name = case_item.text
                    case_item.text = '%s/%s/%s' % (self.test_case_dir, real_suite, org_case_name)
                suite_content.write(new_suite_config)
                suite_item = etree.SubElement(root, 'import')
                suite_item.set('path', new_suite_config)
            else:
                print('suite: %s is not found' % suite)

        tree = etree.ElementTree(root)
        self.test_xml = os.path.join(self.current_dir, CONFIG_XML, "test_suite.xml")
        tree.write(self.test_xml)

def print_info(information):
    print '\n\033[1m - %s\033[0m\n' % information

def print_warn(information):
    print '\n\033[31m WARN: %s\033[0m\n' % information

def print_runtime_test_log(folder, nofollow=False):
    import glob
    def _find_latest_file(t_folder):
        latest_result = max(glob.iglob('%s/*' % t_folder), key=os.path.getctime)
        if os.path.isdir(latest_result):
            latest_result = _find_latest_file(latest_result)
        return latest_result

    test_result_folder = '%s/%s/test-result/latest/logs' % (folder, CONFIG_XML)
    latest_log = _find_latest_file(test_result_folder)
        
    if nofollow:
        os.system('tail -n 100 %s' % latest_log)
    else:
        os.system('tail -f %s' % latest_log)

def parse_test_args(options):
    test_args = []
    if options.stopFailure:
        test_args.append('-s')

    if options.stopFailureMatch:
        test_args.append('-m')
        test_args.append('"%s"' % options.stopFailureMatch)

    if options.caseTimeOut:
        test_args.append('-t')
        test_args.append(options.caseTimeOut)

    if options.verbose:
        test_args.append('-v')

    if options.dryRun:
        test_args.append('-u')

    if options.startDebugger:
        test_args.append('-d')

    if options.noCleanup:
        test_args.append('-n')

    if options.testFailureRetry:
        test_args.append('-r') 
        test_args.append(options.testFailureRetry) 

    if options.configFile:
        test_args.append('-c')
        test_args.append(options.configFile) 

    if options.scenarioConfig:
        test_args.append('-e')
        test_args.append(options.scenarioConfig) 

    if options.scenarioFile:
        test_args.append('-g')
        test_args.append(options.scenarioFile) 

    if options.scenarioDestroy:
        test_args.append('-x')
        test_args.append(options.scenarioDestroy) 

    return ' '.join(test_args)

def execute_unit_test(test_root):
    os.system('cd %s/zstack; mvn -DskipTests clean install' % test_root)
    print('\n\n\n')
    print_info('Build ZStack completely, begin to run unit test.')
    print('\n\n\n')
    os.system('cd %s/zstack/test; mvn test -Dtest=UnitTestSuite' % test_root)

def main():
    parser = optparse.OptionParser('Usage: zstest.py [options] \
\n\n\t ZStack automation build, deploy and test tool. \n')
    parser.add_option(
            "-a", "--auto-complete", 
            dest="autoComplete", 
            default=None, 
            action='store_true', 
            help="[Optional] this is used combined with -c option. User could pickup any test case with -a option, then the program will add related suite_setup and suite_teardown cases.")

    parser.add_option(
            "-b", "--build", 
            dest="needBuild", 
            default=None, 
            action='store_true', 
            help="[Optional] build and deploy zstack before test. The zstack.war will be deployed to TESTROOT/sanitytest/")

    parser.add_option(
            "-B", 
            dest="needBuildPremium", 
            default=None, 
            action='store_true', 
            help="[Optional] build and deploy zstack premium before test. The zstack.war will be deployed to TESTROOT/sanitytest/")

    parser.add_option(
            "-c", "--test-case", 
            dest="caseList", 
            default=None, 
            action='store', 
            help="[Optional] test cases need to be run. User can use test case number. e.g. -c 1,2,3,4. or use test case name, like -c basic/suite_setup.py,basic/test_create_vm.py,basic/suite_teardown.py. This option could be combined used with other options, like -b, -a, -l etc. For example: `zstest.py -c 3,4,5 -b -a`. It also supports a cases range by '~', for example: `zstest.py -c 30~50`, `zstest.py -c 30~50,60~65`")

    parser.add_option(
            "-x", "--exclude-test-case", 
            dest="excludeCaseList", 
            default=None, 
            action='store', 
            help="[Optional] test cases need to be excluded. User must use test case name. e.g. like -x basic/suite_setup.py,basic/test_create_vm.py,basic/suite_teardown.py. This option could be combined used with other options")

    parser.add_option(
            "-d", "--debug", 
            dest="debug", 
            default=None, 
            action='store_true', 
            help="[Optional] enable ZStack debug option: -Xdebug -Xnoagent -Djava.compiler=NONE -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=5005")

    parser.add_option(
            "-i", "--vr-image", 
            dest="vrImagePath", 
            default=None, 
            action='store', 
            help="[Optional] virtual router image path. It is only available when using -b option. It will update virtual router lib and zstacklib in virtual router image. User could also use `export ZSTACK_VR_IMAGE_PATH=/PATH/TO/VR/IMAGE` to set vr image path. ")

    parser.add_option(
            "-l", "--list", 
            dest="listCase", 
            default=None, 
            action='store_true', 
            help="[Optional] list test cases and exit. For example: `zstest.py -l` will list all integration test cases; `zstest.py -l -s basic` will list case name in basic test suite; `zstest.py -l -c 1` will list case 1 description.")

    parser.add_option(
            "-P", "--http-proxy", 
            dest="httpProxy", 
            default=None, 
            action='store', 
            help="[Optional] set http_proxy and https_proxy for possible external connection, when doing woodpecker testing. e.g. used by python lib installation. ")

    parser.add_option(
            "-R", "--test-root", 
            dest="testRoot", 
            default=None, 
            action='store', 
            help="[Optional] zstack test folder, which should include the source of zstack, zstack-utility and zstack-woodpecker. Default is the current folder's grandparent. The default CATALINA path will be TESTROOT/apache-tomcat. It could be changed by --catalina-path. User could also use `export ZSTACK_TEST_ROOT=/PATH/TO/ZSTACK_WORKBENCH` to set zstack test path.")

    parser.add_option(
            "-s", "--test-suite", 
            dest="suiteList", 
            default=None, 
            action='store', 
            help="[Optional] test suites need to be run. e.g. -s basic,virtualrouter. The suite name could be a short name with just few first chars belong to the full suite name, like `zstest.py -s vir` or `zstest.py -s v`, they are all means virtualrouter. If both -s and -c is set, all test cases in -c will be executed firstly. ")

    parser.add_option(
            "-z", "--restart-zstack", 
            dest="restartZstack", 
            default=None, 
            action='store', 
            help="[Optional] restart zstack based on the suite information, it usually be combined used with -b option. nodes information will read from suite's deploy.xml. So it needs to append suite name. The suite name could be a short name, like -s option. E.g. zstest.py -b -z v")

    parser.add_option(
            "-u", "--unit-test", 
            dest="unitTest", 
            default=None, 
            action='store_true', 
            help="[Optional] Execute ZStack unit test. Caution: this might be executed for a long time. ")

    parser.add_option(
            "--catalina-path", 
            dest="catalinaPath", 
            default=None, 
            action='store', 
            help="[Optional] the catalina path. The default path is TESTROOT/apache-tomcat. This config should be aligned with the config in test suite deploy.xml and deploy.tmpt. User could also use `export ZS_CATALINA_ROOT=CATALINA_PATH` to set catalina path. ")

    parser.add_option(
            "--log", dest="showLog", 
            default=None, 
            action='store_true', 
            help="[Optional] print current test case log. When next test case is run, this command needs to reexecuted to get related log.")

    parser.add_option(
            "--no-follow", dest="noFollow", 
            default=None, 
            action='store_true', 
            help="[Optional] do not follow logs when print current test case log.")

    option_group = optparse.OptionGroup(parser, "Test Options", "Following options are only available when run initegration test case or test suite.")

    option_group.add_option(
            "-n", "--no-cleanup", 
            dest="noCleanup", 
            default=None, 
            action='store_true', 
            help="[Optional] Do not execute test_cleanup() to destroy VMs, when test case fails E.g. `zstest -c 52,50 -n`")

    option_group.add_option(
            "-p", "--parallel", 
            dest="parallel", 
            default=None, 
            action='store', 
            help="[Optional] set how many test cases could be parallel executed. suite_setup and suite_teardown execution will not be impacted by paralel params. E.g. `zstest -c 49,50 -p 2` will parallel executed case 49 and case 50 ")

    option_group.add_option(
            "--pypi-index", 
            dest="pypiIndex", 
            default=None, 
            action='store', 
            help="[Optional] set special pypi index url for install zstack testagent required python libs. The default is https://pypi.python.org/simple/. You can also use environment ZSTACK_PYPI_URL to set it.")

    option_group.add_option(
            "-r", "--repeat", 
            dest="repeat", 
            default=None, 
            action='store', 
            help="[Optional] set the test case execution repeat times. Currently it is only available when using -c option. suite_setup and suite_teardown cases will not executed multi times. E.g. `zstest -c 49,50 -p 2 --repeat 10` case 49 and 50 will be repeatly executed 10 times each and 2 cases will be parallelly executed at the same time.")

    option_group.add_option(
            "--retry", 
            dest="testFailureRetry", 
            default=None, 
            action='store', 
            help="[Optional] when test checker executed failed, it could retry the checker. This params is to set the max retry times.")

    option_group.add_option(
            "-t", "--case-default-timeout", 
            dest="caseTimeOut", 
            default=None, 
            action='store', 
            help="[Optional] change test case default timeout. The unit is second. The default value is 1800 second. E.g. `zstest -c 1 -t 2000`")

    option_group.add_option(
            "-S", "--stop-when-failure", 
            dest="stopFailure", 
            default=None, 
            action='store_true', 
            help="[Optional] stop testing, when meet 1st failure. It is useful to debug test failure in a serial test case execution. E.g. `zstest -s basic -S`")

    option_group.add_option(
            "-m", "--stop-when-failure-match", 
            dest="stopFailureMatch", 
            default=None, 
            action='store', 
            help="[Optional] stop testing, when meet 1st failure test log match given string. It is useful to debug test failure in a serial test case execution. E.g. `zstest -s basic -m refused`")

    option_group.add_option(
            "-C", "--config",
            dest="configFile",
            default=None,
            action='store',
            help='[Optional] Integration test config file. Default config file will be test-config.xml under test cases folder.')

    option_group.add_option(
            "-v", "--verbose", 
            dest="verbose", 
            default=None, 
            action='store_true', 
            help="[Optional] print test execution log, instead of dot status bar. E.g. `zstest -s basic -S -v`")

    option_group.add_option(
            "--dry-run", 
            dest="dryRun", 
            default=None, 
            action='store_true', 
            help="[Optional] Dry run test case. E.g. `zstest -s basic --dry-run`")

    option_group.add_option(
            "--start-debugger", 
            dest="startDebugger", 
            default=None, 
            action='store_true', 
	    help="[Optional] Start remote debugger with rpdb when exception happens. E.g. `zstest -s basic --start-debugger`")

    option_group.add_option(
            "--scenario-config", 
            dest="scenarioConfig", 
            default=None, 
            action='store', 
	    help="[Optional] Use first level virtualization to create VM for test scenario. Used together with --scenario-file option, E.g. `zstest -s basic --scenario-config scenario-config.xml --scenario-file scenario-file.xml`")

    option_group.add_option(
            "--scenario-file", 
            dest="scenarioFile", 
            default=None, 
            action='store', 
	    help="[Optional] Use first level virtualization to create VM for test scenario, which is saved in this file. Used together with --scenario-config option, E.g. `zstest -s basic --scenario-config scenario-config.xml --scenario-file scenario-file.xml`")

    option_group.add_option(
            "--scenario-destroy", 
            dest="scenarioDestroy", 
            default=None, 
            action='store', 
	    help="[Optional] Destroy created VM in first level virtualization for test scenario, which is saved in this file. E.g. `zstest --scenario-file scenario-file.xml`")

    parser.add_option_group(option_group)
    (options, arg) = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    test_lib = TestLib()
    current_folder = os.path.dirname(os.path.abspath(__file__))
    test_lib.set_current_dir(current_folder)
    if not options.testRoot:
        if not os.environ.get('ZSTACK_TEST_ROOT'):
            test_root = os.path.dirname(os.path.dirname(current_folder))
        else:
            test_root = os.environ.get('ZSTACK_TEST_ROOT')
    else:
        test_root = options.testRoot

    zstack_root = os.path.join(test_root, 'zstack')
    utility_root = os.path.join(test_root, 'zstack-utility')
    woodpecker_root = os.path.join(test_root, 'zstack-woodpecker')

    test_lib.set_test_dir(woodpecker_root)
    test_lib.analyze_exclude_case_list(options.excludeCaseList)
    test_lib.find_test_case()

    if options.listCase:
        if options.suiteList:
            test_lib.print_test_case(suiteList=options.suiteList)
        elif options.caseList:
            test_lib.print_test_case(caseList=options.caseList)
        else:
            test_lib.print_test_case()
        print_info('List ZStack Integration Test Case Completed')
        sys.exit(0)

    set_env_param(options.debug)

    if options.httpProxy:
        os.environ['http_proxy'] = options.httpProxy
        os.environ['https_proxy'] = options.httpProxy

    if options.pypiIndex:
        os.environ['ZSTACK_PYPI_URL'] = options.pypiIndex

    if options.showLog:
        print_runtime_test_log(current_folder, options.noFollow)

    if options.needBuild or options.needBuildPremium:
        if options.vrImagePath:
            image_path = options.vrImagePath
        elif os.environ.get('ZSTACK_VR_IMAGE_PATH'):
            image_path = os.environ.get('ZSTACK_VR_IMAGE_PATH')
        else:
            image_path = ''

        extra_option = ''
        if options.needBuildPremium:
            extra_option = '-m'

        build_script = os.path.join(current_folder, DEPLOYER_SCRIPT)
        if image_path:
            ret = os.system('%s -r %s -i %s %s' % (build_script, test_root, image_path, extra_option))
        else:
            ret = os.system('%s -r %s %s' % (build_script, test_root, extra_option))

        if ret != 0:
            raise TestExc('Build ZStack Failure, can not continue testing. Exit code: %s' % ret)

        print_info('ZStack Build And Deployment Completed')
    else:
        os.system("touch /tmp/woodpecker_setup")

    if options.restartZstack:
        test_lib.restart_zstack(options.restartZstack)

    if options.unitTest:
        execute_unit_test(test_root)
        print_info('ZStack Unit Test Completed')

    if options.caseList:
        test_lib.assemble_test(options.caseList, auto_complete=options.autoComplete, parallel=options.parallel, repeat=options.repeat)
        test_args = parse_test_args(options)
        test_lib.execute_test(test_args)
        print_info('ZStack Auto Test Completed')

    if options.suiteList:
        test_lib.assemble_test_suite(options.suiteList, parallel=options.parallel)
        test_args = parse_test_args(options)
        test_lib.execute_test(test_args)
        print_info('ZStack Auto Test Completed')

if __name__ == '__main__':
    main()

