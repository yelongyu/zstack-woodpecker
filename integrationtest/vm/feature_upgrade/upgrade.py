# coding=utf-8
import test_stub
import os

management_ip = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']

def test():
    test_stub.initial(management_ip)

    version = test_stub._version()
    current_version = next(version)
    all_cases = test_stub.import_xml_to_cases()

    while True:
        print "--------------------------    Version: %s    --------------------------" % current_version
        cases_list, all_cases = test_stub.find_cases(all_cases, current_version)
        try:
            for case in cases_list:
                try:
                    case.run()
                except:
                    case.error_cleanup()
                finally:
                    case.recover_env()

            next_version = next(version)
            test_stub.upgrade_mn(management_ip, current_version, next_version)
            current_version = next_version
            print "\n\n"

        except StopIteration:
            print "\n"
            print "*" * 20
            print "*" + ' ' + "Test Pass!"
            print "*" * 20
            break