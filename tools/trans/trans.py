# coding=utf-8

import time

import jieba

import function
import resource
import zh_en
import threading
import optparse

HEAD = '''import zstackwoodpecker.test_state as ts_header
import os
TestAction = ts_header.TestAction
def path():

    return dict(initial_formation="template5", path_list=[
'''

TAIL = "])"


def _parse(zh_paths):
    en_paths = []
    for i in zh_paths:
        en_paths.append(zh_en.change_to_english(' '.join(jieba.cut(i)).split(" ")))
    return en_paths


def parse(en_paths):
    case_path = []
    time.sleep(0.1)
    for i in en_paths:
        case_path.extend(function.parse_path(i))

    return case_path


def reset():
    resource.all_volumes = resource.resource_dict()
    resource.all_vms = resource.resource_dict()
    resource.all_snapshots = resource.resource_dict()
    resource.all_backups = resource.resource_dict()
    resource.all_images =resource.resource_dict()


def parse_csv(csv_filename):
    with open(csv_filename, "rb") as f:
        action_path = []
        while True:
            line = f.readline()
            if not line:
                break
            action_path.append(line.strip("\n").split(","))
    return action_path


def write_to_file(action_path, name):
    resource.reset()
    py_path = parse(_parse(action_path))
    all_resources = resource.all_vms + resource.all_volumes + resource.all_snapshots + resource.all_backups + resource.all_images
    with open(name, "w") as f:
        f.write(HEAD)
        for i in py_path:
            f.write("\t\t")
            f.write(i)
            f.write(",\n")
        f.write(TAIL)
        f.write("\n\n\n\n'''\nThe final status:\n")
        f.write(str(all_resources))
        f.write("\n'''")




def main():
    arg_parser = optparse.OptionParser("Usage: translation robot path")
    arg_parser.add_option(
        "-f", "--file",
        dest="csv_file",
        default=None,
        action="store",
        help="PICT tool exports a csv file"
    )
    arg_parser.add_option(
        "-r", "--directory",
        dest="directory",
        default=".",
        action="store",
        help="[Optional]The auto created path file will be put in this directory. Default is current directory"
    )
    arg_parser.add_option(
        "-n", "--num",
        dest="num",
        default="1",
        action="store",
        help="[Optional]The auto created path file will be named path[num].py. Defaule value is 1"
    )
    arg_parser.add_option(
        "-m", "--mini",
        dest="mini",
        default=False,
        action="store_true",
        help="[Optional]if env is mini must add -m"
    )
#创建云主机cpu随机large,创建云盘容量随机large,加载数据云盘
    (options, arg) = arg_parser.parse_args()
    if options.mini:
        resource.MINI = True

    jieba.load_userdict("./words")

    thread_list = []
    csv_filename = options.csv_file
    directory = options.directory
    if directory[-1] == '/':
        directory = directory[-1]
    filename = directory + "/path%s.py"
    action_path = parse_csv(csv_filename)
    for i in range(len(action_path)):
        name = filename % str(i + int(options.num))
        t = threading.Thread(target=write_to_file(action_path[i],name))
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()

    print "Done!"

if __name__ == "__main__":
    # t_list = []
    # for i in range(1):
    #     name = "path"+str(i)+".py"
    #     t = threading.Thread(target=write_to_file(_test,name))
    #     t_list.append(t)
    #     t.start()
    # for t in t_list:
    #     t.join()
    main()
    # print parse(_parse(_test))
