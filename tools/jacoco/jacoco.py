#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import commands
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def get_commit_id_from_build(build_dir, repo):
    version_txt = os.path.join(build_dir, 'versions.txt')
    (status, output) = commands.getstatusoutput("cat %s |grep %s:|awk '{print $2}'"% (version_txt, repo))
    if status == 0:
        print 'Commit id is %s' %output    
        return output
    return False

def get_commit_id_from_env(zstack_root, repo):
    if repo == 'zstack':
        version_file = 'git-commit'
    elif repo == 'premium':
        version_file = 'premium-git-commit'
    version_txt = os.path.join(zstack_root, 'apache-tomcat-7.0.35/webapps/zstack', version_file)
    (status, output) = commands.getstatusoutput("cat %s |grep ^commit| head -1 | awk '{print $2}'"% (version_txt))
    if status == 0:
        print 'Commit id is %s' %output    
        return output
    return False

def reset_src_files(report_root_path, repo, branch, commit_id):
    print commit_id
    repo_dir = os.path.join(report_root_path, 'src', repo)

    (status, output) = commands.getstatusoutput('cd %s && git reset --hard %s' %(repo_dir, commit_id))
    if status == 0:
        print output
        return True

    (status, output) = commands.getstatusoutput('cd %s && git log ' % (repo_dir))
    repo_url = 'http://dev.zstack.io:9080/zstackio/%s.git' % (repo)
    if status != 0:
        os.system('rm -rf %s' % repo_dir)
        os.system('mkdir -p %s' % os.path.join(report_root_path, 'src'))
        os.system('cd %s && git clone %s' % (os.path.join(report_root_path, 'src'), repo_url))
    os.system('cd %s && git branch temp ; git checkout temp' % (repo_dir))
    print 'cd %s && git fetch %s +%s:%s && git reset --hard %s' %(repo_dir, repo_url, branch, branch, commit_id)
    (status, output) = commands.getstatusoutput('cd %s && git fetch %s +%s:%s && git reset --hard %s' %(repo_dir, repo_url, branch, branch, commit_id))
    print output
    if status == 0:
        print output
        return True
    return False

def reset_class_files(war_file, classes):
    if os.path.exists(classes):
        os.system('rm -rf %s' %classes)
    if os.path.exists(war_file):
        (status, output) = commands.getstatusoutput('unzip %s -d %s' %(war_file, classes))
        if status == 0:
            print output
            return True
    return False

def generate_class_ini(report_root_path, class_path, class_ini_path, repo):
    fd = open(class_ini_path, 'w')
    class_str = ''
    #for src in ('zstack', 'premium'):
    pom_xml_path = os.path.join(os.path.join(report_root_path, 'src', repo), 'pom.xml') 
    tree = ET.parse(pom_xml_path)
    root = tree.getroot()
    module_lst = []
    for child in root:
        #if src == 'zstack':
        #    if child.tag.find('profiles') != -1:
        #        for prof in child.getchildren():
        #           is_target_module = False
        #           for item in prof.getchildren():
        #             if item.text == 'premium':
        #                 is_target_module = True
        #             if is_target_module == True and item.tag.find('modules') != -1:
        #                   for module in item.getchildren():
        #                       module_lst.append(module.text)
        #                   is_target_module = False
        #else:
            if child.tag.find('modules') != -1:
                for module in child:
                    if module.text == 'sdk':
                        continue
                    module_lst.append(module.text)
    lib_path = os.path.join(class_path, 'WEB-INF', 'lib') 
    for module in module_lst:
        print module
        if module == 'baremetal':
            continue
        (status, output) = commands.getstatusoutput('ls %s|grep "^%s-[0-9]"' %(lib_path, module))
        if status == 0:
            class_str += lib_path+"/"+output+'\n'

    fd.write(class_str)
    fd.close()

def filter_class(class_ini_file):
    class_fd = open(class_ini_file, 'r')
    for class_file in class_fd:
        class_file = class_file.replace("\n", "")
        (status, output) = commands.getstatusoutput('unzip -l %s | grep Doc_zh_cn' % class_file)
        print 'unzip -l %s | grep Doc_zh_cn' % class_file
        if status != 0:
            continue
        os.system('rm -rf temp')
        os.system('mkdir -p temp')
        print 'unzip %s -d temp' % (class_file)
        os.system('unzip %s -d temp' % (class_file))
        print 'find temp | grep Doc_zh_cn | xargs rm -rf'
        os.system('find temp | grep Doc_zh_cn | xargs rm -rf')
        print 'rm -rf %s' % (class_file)
        os.system('rm -rf %s' % (class_file))
        print 'zip -r %s temp' % (class_file)
        os.system('zip -r %s temp' % (class_file))

def generate_report(report_root_path, repo, class_ini_file, exec_file, source_ini_file):
    report_path = os.path.join(report_root_path, 'report', repo)

    class_fd = open(class_ini_file, 'r')
    #exec_fd = open(exec_ini_file, 'r')
    source_fd = open(source_ini_file, 'r')
    #print 'java -jar jacococli.jar merge `find %s/%s/%s|grep code_coverage.exec ` --destfile %s/%s/%s/merged.exec' % (nightly_result_path, buildtype, buildid, nightly_result_path, buildtype, buildid)
    #os.system('java -jar jacococli.jar merge `find %s/%s/%s|grep code_coverage.exec ` --destfile %s/%s/%s/merged.exec' % (nightly_result_path, buildtype, buildid, nightly_result_path, buildtype, buildid))

    cmd = 'java -jar %s report ' %cli_path
    #for exec_file in exec_fd:
    #   cmd += '%s '%exec_file.replace("\n", "")
    cmd += exec_file

    cmd = cmd+' --html %s '% report_path
    for class_file in class_fd:
        cmd += '--classfiles %s '% class_file.replace("\n", "")

    for source_file in source_fd:
        cmd += '--sourcefiles %s '% os.path.join(report_root_path, 'src' ,source_file.replace("\n", ""))

    print cmd
    os.system(cmd)

if __name__ == "__main__":
    branch = 'master'
    os.system('yum install -y --disablerepo=epel zip')
    #if len(sys.argv) == 4:
    #    buildtype = sys.argv[1]
    #    buildid = sys.argv[2]
    #    repo = sys.argv[3]
    #elif len(sys.argv) != 4 and len(sys.argv) != 1:
    #    print "please provide buildtype buildid and repo, for example:jacoco.py mevoco_2.6.0 136 zstack"
    #    sys.exit(1)

    if True:
        zstack_root = '/usr/local/zstacktest/'
        war_file = '/usr/local/zstacktest/zstack.war'
        exec_file = '/home/1.exec'
        zstack_commit_id = get_commit_id_from_env(zstack_root, 'zstack')
        premium_commit_id = get_commit_id_from_env(zstack_root, 'premium')
        report_root_path = '/home/'
        cli_path = os.path.join('/home/', 'jacococli.jar')
    else:
        build_dir = '/var/www/html/mirror/mevoco_2.6.0/136/'
        war_file = os.path.join(build_dir, 'zstack.war')
        exec_file = os.path.join(build_dir, 'merged.exec')
        zstack_commit_id = get_commit_id_from_build(build_dir, 'zstack')
        premium_commit_id = get_commit_id_from_build(build_dir, 'premium')
        report_root_path = '/mnt/coverage/'
        cli_path = os.path.join('/mnt/jacoco/', 'jacococli.jar')

    class_folder = 'class_files'
    class_ini_file = 'class.ini'
    source_ini_file = 'source.ini'
    exec_ini_file = 'exec.ini'
    result_folder = 'report'

    class_ini_path = os.path.join(report_root_path, class_ini_file)
    exec_ini_path = os.path.join(report_root_path, exec_ini_file)
    source_ini_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), source_ini_file)
    class_path = os.path.join(report_root_path, class_folder)

    reset_class_files(war_file, class_path)
    reset_src_files(report_root_path, 'zstack', branch, zstack_commit_id)
    reset_src_files(report_root_path, 'premium', branch, premium_commit_id)
    #TODO merge exec here
    generate_class_ini(report_root_path, class_path, class_ini_path, 'zstack')
    filter_class(class_ini_path)
    generate_report(report_root_path, 'zstack', class_ini_path, exec_file, source_ini_path)
    generate_class_ini(report_root_path, class_path, class_ini_path, 'premium')
    filter_class(class_ini_path)
    generate_report(report_root_path, 'premium', class_ini_path, exec_file, source_ini_path)
