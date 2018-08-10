'''

@author: Frank
'''
import os.path
import zstacklib.utils.xmlobject as xmlobject
import zstacklib.utils.linux as linux
import zstacklib.utils.shell as shell
import zstacklib.utils.log as log
import zstacklib.utils.lock as lock
import zstacklib.utils.ssh as ssh
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import apibinding.api as api
import apibinding.inventory as inventory
import socket
import time
import os
import sys
import signal
import tempfile
import threading
import traceback
import zstackwoodpecker.operations.resource_operations as res_ops 
import zstackwoodpecker.operations.node_operations as node_ops
import zstackwoodpecker.operations.deploy_operations as dpy_ops 
import zstackwoodpecker.ansible as ansible
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import glob

logger = log.get_logger(__name__)
#This path should be aligned with Dockerfile
docker_apache_path = '/usr/local/zstack'
docker_service_start_timeout = 3
DEFAULT_PYPI_URL = 'https://pypi.python.org/simple/'
ENV_PYPI_URL = os.environ.get('ZSTACK_PYPI_URL')
if not ENV_PYPI_URL:
    ENV_PYPI_URL = DEFAULT_PYPI_URL
USER_PATH = os.path.expanduser('~')
NODE_ANSIBLE_YAML = '%s/.zstackwoodpecker/ansible/node.yaml' % USER_PATH
#avoid of using http_proxy to impact zstack HTTP API request.
ENV_HTTP_PROXY = os.environ.get('woodpecker_http_proxy')
if not ENV_HTTP_PROXY:
    ENV_HTTP_PROXY = ''
ENV_HTTPS_PROXY = os.environ.get('woodpecker_https_proxy')
if not ENV_HTTPS_PROXY:
    ENV_HTTPS_PROXY = ''

NODE_PASSWORD = os.environ.get('ZSTACK_MANAGEMENT_SERVER_PASSWORD')
EXTRA_DEPLOY_SCRIPT = '%s/.zstackwoodpecker/extra_zstack_config.sh' % USER_PATH

node_exception = []

class ActionError(Exception):
    '''action error'''

def shell_cmd_thread(shell_cmd, ignore_exception = False):
    try:
        shell.call(shell_cmd)
    except Exception as e:
        if not ignore_exception:
            node_exception.append(sys.exc_info())
            raise e
        else:
            print sys.exc_info()

def restart_zstack_without_deploy_db(test_config_path):
    '''
    This API could be called, when zstack.war is rebuilt. 

    It will find all running nodes and deploy zstack.war to them.
    '''
    import zstackwoodpecker.test_util as test_util
    test_config_obj = test_util.TestConfig(test_config_path)
    all_config = test_config_obj.get_deploy_config()

    plan = Plan(all_config)
    plan.restart_war_on_all_nodes()

class Node(object):
    '''
    Node super class
    '''
    def __init__(self, plan_config):
        self.node_ip = None
        self.catalina_home = None
        self.start_script = None
        self.stop_script = None
        self.webapps_path = None 
        self.src_war_path = None
        self.war_path = None 
        self.war_folder = None
        self.dst_zstack_properties = None
        self.dst_cloudbus_properties = None
        self.db_server = None
        self.db_port = None
        self.rabbitmq_server = None
        #Need cleanup following 2 properties files after operations.
        self.node_zstack_properties = None
        self.node_cloudbus_properties = None
        self._parse_node_config(plan_config)

    def _parse_node_config(self, test_plan):
        self._set_catalina_home(test_plan.catalina_home)
        self._set_db_server(test_plan.db_server)
        self._set_db_port(test_plan.db_port)
        self._set_rabbitmq_server(test_plan.rabbitmq_server)
        self._set_war_path(test_plan.war_path)
        self._prepare_zstack_properties(test_plan.zstack_properties)
        #self._prepare_cloudbus_properties()

    def set_node_ip(self, node_ip):
        self.node_ip = node_ip
        #need to manually set nodeName
        shell.ShellCmd("echo 'management.server.ip=%s' >> %s" % (self.node_ip, self.node_zstack_properties))()

    def _set_catalina_home(self, catalina_home):
        self.catalina_home = catalina_home
        self.start_script = os.path.join(self.catalina_home, 'bin', 'startup.sh')
        self.stop_script = os.path.join(self.catalina_home, 'bin', 'shutdown.sh')
        self.webapps_path = os.path.join(self.catalina_home, 'webapps')

    def _set_war_path(self, src_war_path):
        self.src_war_path = src_war_path
        self.war_path = os.path.join(self.webapps_path, os.path.basename(self.src_war_path))
        self.war_folder = self.war_path.strip('.war')
        self.dst_zstack_properties = os.path.join(self.war_folder, 'WEB-INF/classes/zstack.properties')
        self.dst_cloudbus_properties = os.path.join(self.war_folder, 'WEB-INF/classes/springConfigXml/CloudBus.xml')

    def _set_db_server(self, db_server):
        self.db_server = db_server

    def _set_db_port(self, db_port):
        self.db_port = db_port

    def _set_rabbitmq_server(self, rabbitmq_server):
        self.rabbitmq_server = rabbitmq_server

    def _prepare_zstack_properties(self, zstack_properties=None):
        if not zstack_properties:
            self.zstack_properties = self.dst_zstack_properties
        else:
            self.zstack_properties = zstack_properties

        handler, tmpfile = tempfile.mkstemp()
        shell.ShellCmd("/bin/cp -f %s %s" % \
                (zstack_properties, tmpfile))()
        #change db server
        shell.ShellCmd("sed -i 's#mysql://localhost:3306#mysql://%s:%s#' %s" %\
                (self.db_server, self.db_port, tmpfile))()
        #change rabbitmq server
        shell.ShellCmd("sed -i 's#CloudBus.serverIp.0 = localhost#CloudBus.serverIp.0 = %s#' %s" % (self.rabbitmq_server, tmpfile))()

        #Remove management.server.ip, if existing.
        shell.ShellCmd("sed -i '/management.server.ip=.*/d' %s" % tmpfile)()
        self.node_zstack_properties = tmpfile

    def _prepare_cloudbus_properties(self):
        handler, tmpfile = tempfile.mkstemp()
        shell.ShellCmd("/bin/cp -f %s %s" % \
                (self.dst_cloudbus_properties, tmpfile))()
        shell.ShellCmd("sed -i 's/localhost/%s/' %s" % \
                (self.master_name, tmpfile))()
        self.node_cloudbus_properties = tmpfile

    def start_node(self):
        print('Deloying war %s to tomcat in node: %s ...' % \
                (self.src_war_path, self.node_ip))

    def stop_node(self):
        print('Stop tomcat in node: %s ...' % self.node_ip)
    
    #must be called before exit Node operations.
    def cleanup(self):
        if os.path.exists(self.node_zstack_properties):
            os.remove(self.node_zstack_properties)

        #if os.path.exists(self.node_cloudbus_properties):
        #    os.remove(self.node_cloudbus_properties)

    def wait_for_node_start(self):
        pass

class HostNode(Node):
    '''
    Node on real exist host. 
    '''
    def __init__(self, test_plan):
        super(HostNode, self).__init__(test_plan)
        self.node_username = None
        self.NODE_PASSWORD = None

    def set_username(self, username):
        self.node_username = username

    def set_password(self, password):
        self.NODE_PASSWORD = password

    def _rshell(self, cmd):
        ssh.execute(cmd, self.node_ip, self.node_username, self.NODE_PASSWORD)

    def prepare_node(self):
        catalina_root = os.path.dirname(self.catalina_home)
        catalina_tar_name = 'zstack_woodpecker_apache.tgz'
        catalina_real_path = os.path.realpath(self.catalina_home)
        catalina_real_name = os.path.basename(catalina_real_path)
        catalina_real_root = os.path.dirname(catalina_real_path)
        catalina_tar = '%s/%s' % (catalina_real_root, catalina_tar_name)
        if not os.path.exists(catalina_tar):
            os.system("cd %s; tar -zcf %s --exclude='logs/*' --exclude='webapps/zstack*' %s" % \
                (catalina_real_root, catalina_tar_name, catalina_real_name))

        ansible_cmd_args  = "host=%s catalina_root=%s catalina_folder=%s \
            catalina_tar=%s zstack_war=%s zstack_properties=%s pypi_url=%s" % \
            (self.node_ip, catalina_root, self.catalina_home, catalina_tar, \
            self.src_war_path, self.node_zstack_properties, ENV_PYPI_URL)

        if ENV_HTTP_PROXY:
            ansible_cmd_args = "%s http_proxy=%s https_proxy=%s" % \
                (ansible_cmd_args, ENV_HTTP_PROXY, ENV_HTTPS_PROXY)

        self.ansible_cmd = "%s -e '%s'" % (NODE_ANSIBLE_YAML, ansible_cmd_args)

    def start_node(self):
        try:
            super(HostNode, self).start_node()
            self.stop_node()
            ansible_dir = os.path.dirname(NODE_ANSIBLE_YAML)
            ansible.execute_ansible(self.node_ip, self.node_username, \
                    self.NODE_PASSWORD, ansible_dir, self.ansible_cmd)
    
            start_node_cmd = 'export CATALINA_OPTS=" -Djava.net.preferIPv4Stack=true "; sh ' + self.start_script
            if self.NODE_PASSWORD:
                start_node_cmd = 'export ZSTACK_MANAGEMENT_SERVER_PASSWORD=%s; %s'\
                        % (self.NODE_PASSWORD, start_node_cmd)
            self._rshell(start_node_cmd)
        except Exception as e:
            node_exception.append(sys.exc_info())

    def stop_node(self):
        super(HostNode, self).stop_node()
        self._rshell('sh %s; \
                ps -aef|grep java|grep -v grep; \
                if [ $? -ne 0 ]; then \
                    sleep 1; \
                    ps -aef|grep java|grep -v grep;\
                    if [ $? -ne 0 ]; \
                        then pkill -9 java || true; \
                    fi; \
                fi;' % \
                self.stop_script)

class DockerNode(Node):
    '''
    Node running in Docker
    '''
    def __init__(self, test_plan):
        #Only CentOS and Ubuntu supported docker at present.
        try:
            shell.ShellCmd('docker -v')()
        except:
            traceback.print_exc(file=sys.stdout)
            raise ActionError('Did not find docker command. Can not run \
multi nowith dockerimage: %s.' % node.dockerImage_)
        #check docker image
        super(DockerNode, self).__init__(test_plan)
        self.docker_image = None
        self.br_dev = None
        self.docker_folder = tempfile.mkdtemp()

        zones_obj = test_plan.config.deployerConfig.zones
        zones = zones_obj.get_child_node_as_list('zone')
        net_dev = zones[0].l2Networks.l2NoVlanNetwork.physicalInterface__
        br_dev = 'br_%s' % net_dev
        self.set_br_dev(br_dev)

    def cleanup(self):
        super(DockerNode, self).cleanup()
        if os.path.exists(self.docker_folder):
            os.system('rm -rf %s' % self.docker_folder)

    def set_br_dev(self, br_dev):
        self.br_dev = br_dev

    def set_docker_image(self, docker_image):
        try:
            shell.ShellCmd('docker images|grep %s' % docker_image)()
        except:
            traceback.print_exc(file=sys.stdout)
            raise ActionError('Did not find docker image: %s by command: \
`docker image`' % docker_image)
        self.docker_image = docker_image

    def _setup_docker_bridge(self):
        #enable bridge. use default l2network setting.
        br_dev = 'br_%s' % self.br_dev
        if not linux.is_bridge(br_dev):
            linux.create_bridge(br_dev, br_dev)
    
        #set docker args
        rhel_docker_config = '/etc/sysconfig/docker'
        ubuntu_docker_config = '/etc/default/docker'
    
        if os.path.exists(rhel_docker_config):
            open(rhel_docker_config, 'w').write('other_args="-b=%s"' % br_dev)
            shell.ShellCmd('service docker restart')()
    
        if os.path.exists(ubuntu_docker_config):
            open(ubuntu_docker_config, 'w').write('other_args="-b=%s"' % \
                    br_dev)
            shell.ShellCmd('service docker restart')()

    def _prepare_docker_image(self):
        #prepare new docker image with right ip address zstack.war, properties
        shell.ShellCmd('cp -a %s %s' % (self.node_zstack_properties, \
                self.docker_folder))()
        #shell.ShellCmd('cp -a %s %s' % (self.node_cloudbus_properties, \
        #        self.docker_folder))()
        shell.ShellCmd('cp -a %s %s' % (self.war_folder, \
                self.docker_folder))()
        dockerfile_content = ["FROM %s" % self.docker_image]
        dockerfile_content.append("RUN rm -rf %s" % self.war_folder)
        dockerfile_content.append("ADD %s %s" % \
                (os.path.basename(self.war_folder), self.war_folder))
        dockerfile_content.append("ADD %s %s" % \
                (os.path.basename(self.node_zstack_properties), \
                self.dst_zstack_properties))
        #dockerfile_content.append("ADD %s %s" % \
        #        (os.path.basename(self.node_cloudbus_properties), \
        #        self.dst_cloudbus_properties))
        if NODE_PASSWORD:
            dockerfile_content.append('CMD \
export CATALINA_OPTS="-Djava.net.preferIPv4Stack=true" && \
export ZSTACK_MANAGEMENT_SERVER_PASSWORD="%s" && \
ifconfig eth0 %s && export ZSTACK_BUILT_IN_HTTP_SERVER_IP=%s && \
/bin/sh %s/apache-tomcat/bin/startup.sh \
&& tail -f %s/apache-tomcat/logs/catalina.out ' % (NODE_PASSWORD, \
                self.node_ip, self.node_ip, docker_apache_path, \
                docker_apache_path))
        else:
            dockerfile_content.append('CMD \
export CATALINA_OPTS="-Djava.net.preferIPv4Stack=true" && \
ifconfig eth0 %s && export ZSTACK_BUILT_IN_HTTP_SERVER_IP=%s && \
/bin/sh %s/apache-tomcat/bin/startup.sh \
&& tail -f %s/apache-tomcat/logs/catalina.out ' % (self.node_ip, \
                self.node_ip, docker_apache_path, docker_apache_path))

        open(os.path.join(self.docker_folder, 'Dockerfile'), \
                'w').write('\n'.join(dockerfile_content))
        print 'Dockerfile is prepared.'

    def prepare_node(self):
        self._setup_docker_bridge()
        self._prepare_docker_image()

    def start_node(self):
        def _wait(data):
            try:
                shell.ShellCmd('docker ps')()
                print('docker service is ready')
                return True
            except:
                print ('docker service is still starting ...')
                return False
        
        try:
            if not linux.wait_callback_success(_wait, None, \
                    docker_service_start_timeout, 0.1):
                raise ActionError('waiting for docker start up time out: %s' % \
                    docker_service_start_timeout)
            shell.ShellCmd('cd %s ; docker build --tag="%s" .' % \
                    (self.docker_folder, self.node_ip))()
            #run docker image
            shell.ShellCmd("docker run -d %s " % self.node_ip)()
            print 'docker container has been created.'
        except Exception as e:
            node_exception.append(sys.exc_info())

    def stop_node(self):
        shell.ShellCmd("docker stop \
                `docker ps -a|grep %s|awk '{print $1}'`|| true" \
                % self.node_ip)()
        shell.ShellCmd("docker rm \
                `docker ps -a|grep %s|awk '{print $1}'`|| true" \
                % self.node_ip)()
        shell.ShellCmd("docker rmi %s || true" % self.node_ip)()

class Plan(object):
    def _full_path(self, path):
        if path.startswith('~'):
            return os.path.expanduser(path)
        elif path.startswith('/'):
            return path
        else:
            return os.path.join(self.plan_base_path, path)
        
    def _set_and_validate_config(self):
        basic_config = self.config.basicConfig
        deploy_config = self.config.deployerConfig
        self.zstack_pkg = self._full_path(basic_config.zstackPkg.text_)
        self.zstack_install_script = \
                self._full_path(basic_config.zstackInstallScript.text_)
        try:
            os.system('source /root/.bashrc')
        except:
            pass
        if os.environ.get('ZSTACK_ALREADY_INSTALLED') != "yes" and not os.path.exists(self.zstack_pkg):
            raise ActionError('unable to find %s for ZStack binary' \
                    % self.zstack_pkg)

        if basic_config.hasattr('zstackInstallPath'):
            self.install_path = \
                    self._full_path(basic_config.zstackInstallPath.text_)
        else:
            raise ActionError(\
                    'need to set config.deployerConfig.zstackInstallPath in : %s' % self.deploy_config_path)
        
        #set ZSTACK_HOME, which will be used by zstack-ctl
        os.environ['ZSTACK_HOME'] = '%s/apache-tomcat/webapps/zstack/' % \
                self.install_path

        if basic_config.hasattr('testAgent'):
            self.test_agent_path = self._full_path(basic_config.testAgent.text_)
            linux.error_if_path_missing(self.test_agent_path)
            for zone in deploy_config.zones.get_child_node_as_list('zone'):
                for cluster in zone.clusters.get_child_node_as_list('cluster'):
                    if cluster.hypervisorType_ == inventory.KVM_HYPERVISOR_TYPE:
                        for h in cluster.hosts.get_child_node_as_list('host'):
                            if self.scenario_config != None and self.scenario_file != None:
                                managementIp = dpy_ops.get_host_from_scenario_file(h.name_, self.scenario_config, self.scenario_file, self.config)
                                if managementIp != None:
                                    h.managementIp_ = managementIp
                            h.managementIp_
                            h.username_
                            h.password_
                            # will raise exception if one of above not specified in xml filea.
                            self.test_agent_hosts.append(h)
        else:
            if xmlobject.has_element(basic_config, 'testAgentHost'):
                raise ActionError('<tesgAgent> is missing while <testAgentHost> presents')
    
        self.catalina_home = self.install_path + '/apache-tomcat'

        self.wait_for_start_timeout = basic_config.get('managementServerStartTimeout')
        if not self.wait_for_start_timeout:
            self.wait_for_start_timeout = 120
        else:
            self.wait_for_start_timeout = int(self.wait_for_start_timeout)
        
        if hasattr(basic_config, 'rabbitmq'):
            self.rabbitmq_server = basic_config.rabbitmq.get('server', 'localhost')
            self.rabbitmq_server_root_passwd = basic_config.rabbitmq.get('password', '')
            if not self.rabbitmq_server_root_passwd:
                print ('!!!WARN! Rabbitmq server root password are not set!')
        else:
            raise ActionError('need to set config.basicConfig.rabbitmq.server in: %s' % self.deploy_config_path)

        if hasattr(basic_config, 'db'):
            self.need_deploy_db = True
            self.db_server = basic_config.db.get('server', 'localhost')
            self.db_username = basic_config.db.get('username', 'zstack')
            self.db_password = basic_config.db.get('password', '')
            self.db_admin_username = basic_config.db.get('admin', 'root')
            self.db_admin_password = basic_config.db.get('adminPassword', '')
            self.db_server_root_password = basic_config.db.get('server_root_password', '')
            if not self.db_server_root_password:
                print ('!!!WARN! Database server root password are not set!')

            self.db_port = basic_config.db.get('port', '3306')
        
        if basic_config.has_element('zstackProperties'):
            if basic_config.zstackProperties.text_:
                self.zstack_properties = self._full_path(basic_config.zstackProperties.text_)
                if not os.path.exists(self.zstack_properties):
                    print('unable to find zstackProperties at %s, use \
default one' % self.zstack_properties)
                    self.zstack_properties = None

        if basic_config.has_element('zstackHaVip'):
	    self.zstack_ha_vip = basic_config.zstackHaVip.text_
	else:
            self.zstack_ha_vip = None

        if basic_config.has_element('zstackManagementIp'):
	    self.zstack_management_ip = basic_config.zstackManagementIp.text_
	else:
            self.zstack_management_ip = None

        os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = ''
        if deploy_config.has_element('nodes') \
            and deploy_config.nodes.has_element('node'):
            for node in deploy_config.nodes.get_child_node_as_list('node'):
                ip = dpy_ops.get_node_from_scenario_file(node.name_, self.scenario_config, self.scenario_file, self.config)
                if ip != None:
                    node.ip_ = ip
                else:
                    if self.zstack_ha_vip != None:
                        node.ip_ = self.zstack_ha_vip
                    else:
                        print("node [%s] does not have IP" % node.name_)
                node.ip_
                self.nodes.append(node)
                if linux.is_ip_existing(node.ip_):
                    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = node.ip_
                elif not os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_IP'):
                    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = node.ip_
        else:
            raise ActionError('deploy.xml setting error. No deployerConfig.nodes.node is found. ')

        if self.zstack_ha_vip != None:
            os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = self.zstack_ha_vip

        if self.zstack_management_ip != None:
            os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = self.zstack_management_ip

        if not os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_IP'):
            raise ActionError('deploy.xml setting error. No deployerConfig.nodes.node.ip is defined. ')

    def _deploy_zstack_properties(self):
        if not self.zstack_properties:
            return
        
        dst = os.path.join(self.catalina_home, \
                'webapps/zstack/WEB-INF/classes/zstack.properties')
        shell.call('cp -f %s %s' % (self.zstack_properties, dst))
        print('deployed zstack properties[%s] to %s' % \
                (self.zstack_properties, dst))

    def _extra_deployment(self):
        if not os.path.exists(EXTRA_DEPLOY_SCRIPT):
            return

        shell.call('%s %s' % (EXTRA_DEPLOY_SCRIPT, self.catalina_home))
        print('Extra deployment by %s' % EXTRA_DEPLOY_SCRIPT)

    def _upgrade_local_zstack(self):
        #cmd = 'WEBSITE=localhost bash %s -f %s -u -r %s' % \
        #        (self.zstack_install_script, self.zstack_pkg, \
        #        self.install_path)
        #if not add -F, will break db upgrade, since we stop_node by force.
        cmd = 'bash %s -u -F' % self.zstack_pkg

        shell.call(cmd)
        self._extra_deployment()

    def _install_local_zstack(self):
        shell.call('rm -rf %s' % self.install_path, False)
        #cmd = 'WEBSITE=localhost bash %s -f %s -r %s -a -z' % \
        #        (self.zstack_install_script, self.zstack_pkg, \
        #        self.install_path)
        #cmd = 'bash %s -D -z -r %s -m ' % (self.zstack_pkg, self.install_path)
        cmd = 'deactivate; which python; bash %s -D -z -r %s ' % (self.zstack_pkg, self.install_path)
        if self.db_admin_password:
            cmd = '%s -P %s' % (cmd, self.db_admin_password)
        if self.db_password:
            cmd = '%s -p %s' % (cmd, self.db_password)

        shell.call(cmd)
        #self._deploy_zstack_properties()
        self._extra_deployment()

    def _install_zstack_nodes_ha(self):
        for node in self.nodes:
            cmd = "/usr/local/bin/zs-network-setting -b %s %s %s %s" % (node.nic_, node.ip_, node.netmask_, node.gateway_)
            print cmd
            ssh.execute(cmd, node.ip_, node.username_, node.password_)
            ssh.scp_file(self.zstack_pkg, "/root/zstack-installer.bin", node.ip_, node.username_, node.password_)
            cmd = "deactivate; which python; bash %s -o -i -I %s" % ("/root/zstack-installer.bin", node.bridge_)
            print cmd
            ssh.execute(cmd, node.ip_, node.username_, node.password_)

    def _install_zstack_ha(self):
        node1 = self.nodes[0]
	host_info = ""
        host_id = 1
        for node in self.nodes:
            host_info += "--host%s-info %s:%s@%s " % (host_id, node.username_, node.password_, node.ip_)
	    host_id += 1
        cmd = "zstack-ctl install_ha %s --vip %s" % (host_info, self.zstack_ha_vip)
        print cmd
        ssh.execute(cmd, node1.ip_, node1.username_, node1.password_)

    def _set_extra_node_config(self):
        node1 = self.nodes[0]
        for node in self.nodes:
            cmd = 'zstack-ctl configure --duplicate-to-remote=%s; zstack-ctl configure --host=%s management.server.ip=%s' % \
                    (node.ip_, node.ip_, node.ip_)
            if os.environ.get('ZSTACK_SIMULATOR') == "yes":
                cmd += '; zstack-ctl configure --host=%s ApplianceVm.agentPort=8080' % (node.ip_)
            if not linux.is_ip_existing(node.ip_):
                ssh.execute(cmd, node1.ip_, node.username_, node.password_)
            else:
                thread = threading.Thread(target=shell_cmd_thread, args=(cmd,))
                thread.start()
                self._wait_for_thread_completion('set extra management node config', 60)

    def _change_node_ip(self):
        for node in self.nodes:
            cmd = 'zstack-ctl change_ip --ip=%s --mysql_root_password=%s' % (node.ip_, os.environ.get('DBAdminPassword'))
            if not linux.is_ip_existing(node.ip_):
                ssh.execute(cmd, node.ip_, node.username_, node.password_)
            else:
                thread = threading.Thread(target=shell_cmd_thread, args=(cmd,))
                thread.start()
                self._wait_for_thread_completion('change management node ip', 120)

            cmd = 'zstack-ctl configure InfluxDB.startupTimeout=1200'
            if not linux.is_ip_existing(node.ip_):
                ssh.execute(cmd, node.ip_, node.username_, node.password_)
            else:
                thread = threading.Thread(target=shell_cmd_thread, args=(cmd,))
                thread.start()
                self._wait_for_thread_completion('InfluxDB startup time setting to 10 mins', 120)

    def _wait_for_thread_completion(self, msg, wait_time, raise_exception = True):
        end_time = wait_time
        while end_time > 0:
            if threading.active_count() == 1:
                break

            if node_exception and raise_exception:
                print 'Meet exception when: %s :' % msg
                info1 = node_exception[0][1]
                info2 = node_exception[0][2]
                raise info1, None, info2
                
            print 'Wait for %s ...' % msg
            time.sleep(1)
            end_time -= 1
        else:
            raise ActionError('%s failed, since it exceeds %s seconds' % \
                    (msg, wait_time))

    def _install_management_nodes(self):
        for node in self.nodes:
            if not linux.is_ip_existing(node.ip_) and os.environ.get('ZSTACK_ALREADY_INSTALLED') != "yes":
                cmd = 'zstack-ctl install_management_node --force-reinstall \
                        --host=%s' % node.ip_
                thread = threading.Thread(target=shell_cmd_thread, args=(cmd,))
                thread.start()
            else:
                print "node: %s has been installed zstack" % node.ip_

        self._wait_for_thread_completion('install remote management node', 600)

    def _upgrade_management_nodes(self):
        for node in self.nodes:
            if not linux.is_ip_existing(node.ip_):
                cmd = 'zstack-ctl upgrade_management_node --host=%s' % node.ip_
                thread = threading.Thread(target=shell_cmd_thread, args=(cmd,))
                thread.start()

        self._wait_for_thread_completion('upgrade remote management node', 600)

    def _start_war(self):
        self.tomcat.start()

    def _deploy_rabbitmq(self):
        ssh.make_ssh_no_password(self.rabbitmq_server, 'root', \
                self.rabbitmq_server_root_passwd)

        cmd = "zstack-ctl install_rabbitmq --host=%s" % self.rabbitmq_server

        print('deploying rabbitmq ...')
        shell.call(cmd)

    def _deploy_db(self, keep_db = False):
        if not keep_db:
            extra_opts = '--drop'
        else:
            extra_opts = '--keep-db'

        if not self.need_deploy_db:
            return
        ssh.make_ssh_no_password(self.db_server, 'root', \
                self.db_server_root_password)

        if not self.db_admin_password:
            cmd = 'zstack-ctl install_db --debug --host=%s --login-password=zstack.mysql.password' % self.db_server
        else:
            cmd = 'zstack-ctl install_db --debug --host=%s \
                    --login-password=%s' \
                    % (self.db_server, \
                    self.db_admin_password)

        print('installing db ...')
        shell.call(cmd)

        cmd = 'zstack-ctl deploydb %s --host=%s' % (extra_opts, self.db_server)
        if self.db_admin_password:
            cmd = '%s --root-password=%s' % (cmd, self.db_admin_password )
        else:
            cmd = '%s --root-password=zstack.mysql.password' % cmd

        if self.db_password:
            cmd = '%s --zstack-password=%s' % (cmd, self.db_password)

        print('deploying db ...')
        shell.call(cmd)
    
    @lock.file_lock('deploy_test_agent')
    def deploy_test_agent(self, target=None):
        print('Deploy test agent\n')
        if not self.test_agent_path:
            print('Not find test_agent. Stop deploying test agent.\n')
            return
        
        testagentdir = None

        def _wait_echo(target_ip):
            try:
                rspstr = http.json_dump_post(testagent.build_http_path(target_ip, host_plugin.ECHO_PATH))
            except:
                print('zstack-testagent does not startup, will try again ...')
                return False
            return True

        testagentdir = self.test_agent_path
        ansible.check_and_install_ansible()

        lib_files = []

        if not target:
            #default will deploy all test hosts.
            exc_info = []
            for h in self.test_agent_hosts:
                print('Enable ansible connection in host: [%s] \n' % h.managementIp_)

                if hasattr(h, 'port_'):
                    ansible.enable_ansible_connection(h.managementIp_, h.username_, h.password_, exc_info, h.port_)
                else:
                    ansible.enable_ansible_connection(h.managementIp_, h.username_, h.password_, exc_info, 22)

            for h in self.test_agent_hosts:
                print('Deploy test agent in host: [%s] \n' % h.managementIp_)
                if h.username_ != 'root':
                    ansible_become_args = "ansible_become=yes become_user=root ansible_become_pass=%s" % (h.password_)
                else:
                    ansible_become_args = ""

                if hasattr(h, 'port_'):
                    ansible_port_args = "ansible_ssh_port=%s" % (h.port_)
                else:
                    ansible_port_args = ""

                ansible_cmd_args = "host=%s \
                        ansible_ssh_user=%s \
                        ansible_ssh_pass=%s \
                        %s \
                        %s \
                        testagentdir=%s" % \
                        (h.managementIp_, h.username_, h.password_, ansible_become_args, ansible_port_args, testagentdir)

                if ENV_HTTP_PROXY:
                    ansible_cmd_args = "%s http_proxy=%s https_proxy=%s" % \
                        (ansible_cmd_args, ENV_HTTP_PROXY, ENV_HTTPS_PROXY)

                ansible_cmd = "testagent.yaml -e '%s'" % ansible_cmd_args

                thread = threading.Thread(target=ansible.do_ansible,\
                     args=(testagentdir, ansible_cmd, lib_files, exc_info))
                # Wrap up old zstack logs in /var/log/zstack/
                #print('archive test log on host: [%s] \n' % h.managementIp_)
                #try:
                #    if hasattr(h, 'port_'):
                #        log.cleanup_log(h.managementIp_, h.username_, h.password_, h.port_)
                #    else:
                #        log.cleanup_log(h.managementIp_, h.username_, h.password_)
                #except Exception as e:
                #    print "clean up old testing logs meet execption on management node: %s" % h.managementIp_
                #    raise e

                thread.start()
            #if localhost is not in hosts, should do log archive for zstack
            log.cleanup_local_log()

            self._wait_for_thread_completion('install test agent', 200)

            for h in self.test_agent_hosts:
                if not linux.wait_callback_success(_wait_echo, h.managementIp_, 5, 0.2, True):
                    raise ActionError('testagent is not start up in 5s on %s, after it is deployed by ansible.' % h.managementIp_)

        else:
            print('Deploy test agent in host: %s \n' % target.managementIp)
	    if target.username != "root":
                ansible_cmd_args = "host=%s \
                        ansible_ssh_user=%s \
                        ansible_become=yes \
                        become_user=root \
                        ansible_become_pass=%s \
                        testagentdir=%s" % \
                        (target.managementIp, target.username, target.password, testagentdir)
            else:
                ansible_cmd_args = "host=%s \
                        testagentdir=%s" % \
                        (target.managementIp, testagentdir)
            if ENV_HTTP_PROXY:
                ansible_cmd_args = "%s http_proxy=%s https_proxy=%s" % \
                    (ansible_cmd_args, ENV_HTTP_PROXY, ENV_HTTPS_PROXY)

            ansible_cmd = "testagent.yaml -e '%s'" % ansible_cmd_args
            ansible.execute_ansible(target.managementIp, target.username, \
                    target.password, testagentdir, ansible_cmd, lib_files)
            if not linux.wait_callback_success(_wait_echo, target.managementIp, 5, 0.2):
                raise ActionError('testagent is not start up in 5s on %s, after it is deployed by ansible.' % target.managementIp)
            
    def _enable_jacoco_agent(self):
        for node in self.nodes:
            woodpecker_ip = ''
            import commands
            (status, output) = commands.getstatusoutput("ip addr show zsn0 | sed -n '3p' | awk '{print $2}' | awk -F / '{print $1}'")
            dst_file = '/var/lib/zstack/virtualenv/zstackctl/lib/python2.7/site-packages/zstackctl/ctl.py'
            if output.startswith('172'):
                woodpecker_ip = output
            if woodpecker_ip != '':
                #Separate woodpecker condition
                if os.path.exists('/home/%s/jacocoagent.jar' % woodpecker_ip):
                    src_file = '/home/%s/zstack-utility/zstackctl/zstackctl/ctl.py' % woodpecker_ip
                    fd_r = open(src_file, 'r')
                    fd_w = open(dst_file, 'w')
                    ctl_content = '' 
                    for line in fd_r:
                        if line.find('with open(setenv_path') != -1:
                            line = '            catalina_opts.append("-javaagent:/var/lib/zstack/jacocoagent.jar=output=tcpserver,address=%s,port=6300")\n%s'\
                                %(node.ip_, line)
                        ctl_content += line
                    fd_r.close()
                    fd_w.write(ctl_content)
                    fd_w.close()
                    ssh.scp_file(dst_file, dst_file, node.ip_, node.username_, node.password_)
                    print 'Inject jacoco agent into ctl.py'
                else:
                    print 'Here is no jacocoagent.jar, skip to inject jacoco agent'
            else:
                #Incorporate wookpecker condition
                if os.path.exists('/home/%s/jacocoagent.jar' % node.ip_):
                    src_file = '/home/%s/zstack-utility/zstackctl/zstackctl/ctl.py' % node.ip_
                    fd_r = open(src_file, 'r')
                    fd_w = open(dst_file, 'w')
                    ctl_content = ''
                    for line in fd_r:
                        if line.find('with open(setenv_path') != -1:
                            line = '            catalina_opts.append("-javaagent:/home/%s/jacocoagent.jar=output=tcpserver,address=127.0.0.1,port=6300")\n%s'\
                                %(node.ip_, line)
                        ctl_content += line
                    fd_r.close()
                    fd_w.write(ctl_content)
                    fd_w.close()
                    print 'Inject jacoco agent into ctl.py'
                else:
                    print 'Here is no jacocoagent.jar, skip to inject jacoco agent'


    def _enable_jacoco_dump(self):
        woodpecker_ip = ''
        import commands
        (status, output) = commands.getstatusoutput("ip addr show zsn0 | sed -n '3p' | awk '{print $2}' | awk -F / '{print $1}'")
        if output.startswith('172'):
            woodpecker_ip = output
        for node in self.nodes:
            import subprocess
            if woodpecker_ip != '':
                dump_str = 'java -jar /home/%s/jacococli.jar dump --address %s --port 6300 --reset\
                    --destfile /home/%s/zstack-woodpecker/dailytest/config_xml/code_coverage.exec' %(woodpecker_ip, node.ip_, woodpecker_ip)
            else:
                dump_str = 'java -jar /home/%s/jacococli.jar dump --address 127.0.0.1 --port 6300 --reset\
                    --destfile /home/%s/zstack-woodpecker/dailytest/config_xml/code_coverage.exec' %(node.ip_, node.ip_)
            cmd = 'while true; do sleep 15; %s; done' %dump_str
            (status, output) = commands.getstatusoutput('ps -ef|grep jacococli|grep while') 
            if status == 0 and output.find('while true') == -1:
                subprocess.Popen(cmd, shell=True)
            print 'jacoco dump started'

    def execute_plan_without_deploy_test_agent(self):
        self._enable_jacoco_agent()
        if os.environ.get('ZSTACK_ALREADY_INSTALLED') != "yes":
            try:
                self._stop_nodes()
                shell.call('zstack-ctl kairosdb --stop')
                shell.call('zstack-ctl cassandra --stop')
            except:
                pass
    
            self._install_local_zstack()
            self._deploy_db()
            self._deploy_rabbitmq()
            self._install_management_nodes()
            self._set_extra_node_config()
        else:
            self._change_node_ip()
            self._install_management_nodes()
            self._set_extra_node_config()
        try:
            with open('/root/.bashrc', 'a+') as bashrc:
                bashrc.write('export ZSTACK_ALREADY_INSTALLED=yes\n')
        except:
            pass

        self._start_multi_nodes(restart=True)
        self._enable_jacoco_dump()

    def execute_plan_ha(self):
	self._install_zstack_nodes_ha()
	self._install_zstack_ha()

    def deploy_db_without_reinstall_zstack(self):
        self.deploy_test_agent()
        self._stop_nodes()
        self._deploy_db()
        self._start_multi_nodes()

    def restart_war_on_all_nodes(self):
        #planed_nodes = []
        #for node in self.nodes:
        #    planed_nodes.append(node.ip_)

        #import socket
        #planed_nodes.append(socket.gethostbyname(socket.gethostname()))

        #live_nodes_inv = res_ops.query_resource(res_ops.MANAGEMENT_NODE, [])

        #set ZSTACK_HOME, which will be used by zstack-ctl
        os.environ['ZSTACK_HOME'] = '%s/apache-tomcat/webapps/zstack/' % \
                self.install_path
        not_restarted_nodes = []

        #for live_node_inv in live_nodes_inv:
        #    if not live_node_inv.hostName in planed_nodes:
        #        not_restarted_nodes.append(live_node_inv.hostName)

        self.deploy_test_agent()
        self._stop_nodes()
        self._upgrade_local_zstack()
        #self._deploy_db(keep_db = True)
        self._upgrade_management_nodes()
        self._set_extra_node_config()
        self._start_multi_nodes()

        if not_restarted_nodes:
            print('Following node are not restarted, since they are not defined in deploy.xml : %s' % not_restarted_nodes)
        else:
            nodes_ip = ''
            for node in self.nodes:
                nodes_ip = '%s %s' % (nodes_ip, node.ip__)

            print('\nAll nodes:%s have been restarted!\n' % nodes_ip)

    def execute_plan(self):
        self.deploy_test_agent()
        self.execute_plan_without_deploy_test_agent()
        
    def _start_multi_nodes(self, restart = False):
        nodes = []
        threads = []
        node1 = self.nodes[0]
        for node in self.nodes:
            #The reserved node is used by test cases. 
            if not restart and node.reserve__:
                continue

            if not node.dockerImage__:
                print 'Deploy node in hosts'
                #consider some zstack-server is running in vm, the server 
                # startup speed is slow. Increase timeout to 180s.
                if linux.is_ip_existing(node.ip_):
                    if os.environ.get('ZSTACK_SIMULATOR') == "yes":
                        cmd = 'zstack-ctl stop_node; zstack-ctl configure unitTestOn=true; zstack-ctl configure ThreadFacade.maxThreadNum=1000; nohup zstack-ctl start_node --simulator -DredeployDB=true'
                    else:
                        cmd = 'zstack-ctl stop_node; nohup zstack-ctl start_node'
                    thread = threading.Thread(target=shell_cmd_thread, args=(cmd, True, ))
                elif not linux.is_ip_existing(node1.ip_):
                    # when first node1 ip is not local, it usualy means woodpecker is running on hosts other than MN
                    cmd = 'zstack-ctl stop_node --host=%s ; zstack-ctl start_node --host=%s' % (node.ip_, node.ip_)
                    thread = threading.Thread(target=ssh.execute, args=(cmd, node1.ip_, node1.username_, node1.password_, ))
                else:
                    cmd = 'zstack-ctl stop_node --host=%s ; zstack-ctl start_node --host=%s' % (node.ip_, node.ip_)
                    thread = threading.Thread(target=shell_cmd_thread, args=(cmd, True, ))
                threads.append(thread)
            else:
                print 'Deploy node in docker'
                docker_node = DockerNode(self)
                docker_node.set_docker_image(node.dockerImage__)
                docker_node.set_node_ip(node.ip__)
                docker_node.prepare_node()
                nodes.append(docker_node)
                thread = threading.Thread(target=docker_node.start_node)
                threads.append(thread)

        for thread in threads:
            thread.start()

        self._wait_for_thread_completion('start management node', 400)
        time.sleep(10)

        if node_exception:
            print 'node start meets exception:'
            info1 = node_exception[0][1]
            info2 = node_exception[0][2]
            raise info1, None, info2
                
        current_time = time.time()
        #largest timeout time for multi nodes startup is 300s
        timeout_time = current_time + 300
        for node in self.nodes:
            #The reserved node is used by test cases. 
            if node.reserve__:
                continue
            new_time = time.time() 
            if new_time >= timeout_time:
                new_timeout = 1
            else:
                new_timeout = timeout_time - new_time

            if not linux.wait_callback_success(\
                    node_ops.is_management_node_start, \
                    node.ip_, timeout=new_timeout, interval=0.5):
                raise ActionError('multi node does not startup on host: %s' \
                        % node.ip_)

        zstack_home = '%s/apache-tomcat/webapps/zstack/' % self.install_path
        cmd = 'zstack-ctl setenv ZSTACK_HOME=%s' % zstack_home
        shell.call(cmd)

    def stop_node(self):
        print 'Begin to stop node ...'
        self._stop_nodes()

    def _stop_nodes(self):
        nodes = []
        for node in self.nodes:
            if node.dockerImage__:
                docker_node = DockerNode(self)
                docker_node.set_node_ip(node.ip__)
                nodes.append(docker_node)
                thread = threading.Thread(target=docker_node.stop_node)
                thread.start()
                docker_node.cleanup()
            else:
                #Woodpecker need to set no ssh password for all nodes.
                cmd = 'zstack-ctl stop_node --host=%s -f' % node.ip_
                thread = threading.Thread(target=shell_cmd_thread, args=(cmd, True))
                thread.start()

        self._wait_for_thread_completion('stop management node', 40, \
                raise_exception = False)

    def disable_db_deployment(self):
        self.need_deploy_db = False

    def __init__(self, plan_config, scenario_config = None, scenario_file = None):
        self.config = plan_config
        self.scenario_config = scenario_config
        self.scenario_file = scenario_file
        self.zstack_pkg = None
        self.zstack_install_script = None
        self.install_path = None
        self.test_agent_path = None
        self.test_agent_hosts = []
        self.nodes = []
        self.catalina_home = None
        self.tomcat = None
        #self.elasticsearch_home = None
        #self.recreate_elasticsearch_index = False
        self.wait_for_start_timeout = None
        self.deploy_config_path = plan_config.deployConfigPath_
        self.deploy_config_tmpt_path = plan_config.deployConfigTemplatePath__
        self.plan_base_path = os.path.dirname(plan_config.deployConfigPath_)
        self.need_deploy_db = False
        self.rabbitmq_server = 'localhost'
        #default db information
        self.db_server = 'localhost'
        self.db_username = 'zstack'
        self.db_password = ''
        self.db_port = '3306'
        self.zstack_properties = None
        self.wait_for_deploy_testagent_timeout = 300
        
        self._set_and_validate_config()

class SetupAction(object):
    def __init__(self):
        self.plan = None
        self.out = None
        
    def run(self):
        p = Plan(self.plan)
        p.execute_plan()
        return p
