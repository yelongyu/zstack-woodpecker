# zstack-woodpecker
The automated testing framework for project ZStack http://zstack.org

#1. Download all source
#1. Download all source
#1. Download all source
#1. Download all source
 * `mkdir /home/zstack`  
 * `cd /home/zstack`  
 * `git clone https://github.com/zstackorg/zstack`  
 * `git clone https://github.com/zstackorg/zstack-utility`  
 * `git clone https://github.com/zstackorg/zstack-woodpecker`  
 * `git clone https://github.com/zstackorg/zstack-dashboard`  
 * `git clone https://github.com/zstackorg/zstack-vyos`  
 
#2. Install necessary packages and set GOROOT 
* In CentOS7.2 
* `yum install java-1.8.0-openjdk-devel.x86_64 java-1.8.0-openjdk.x86_64 ant  apache-maven git libffi libffi-devel openssl-devel bc ant sshpass golang -y` 
* `export GOROOT=/usr/lib/golang`
* `export GO15VENDOREXPERIMENT=1`

#3. Manually build ZStack
 * make sure Java JDK and maven are installed.  
 * For Mainland developer, please download repository.tar to /root/.m2/ manually from http://pan.baidu.com/s/1eQvUmWU, before build ZStack. Then run  `cd /root/.m2 ; tar xf repository.tar `
 * `cd /home/zstack; wget -c http://archive.apache.org/dist/tomcat/tomcat-7/v7.0.35/bin/apache-tomcat-7.0.35.zip`  
 * `cd /home/zstack/zstack`  
 * `mvn -DskipTests clean install` (The 1st time build will be a little bitter slow, since it need to download a lot of java libs)  


#4. Use woodpecker to build zstack all in one package
 * `cd /home/zstack/zstack-woodpecker/dailytest`  
 * `./zstest.py -b`  

#5. Create local test configuration environment files

 * `cd /home/zstack/zstack-woodpecker/tools/`  
 * `sh copy_test_config_to_local.sh` (it will copy all woodpecker test env configuration files to USER_HOME/.zstackwoodpecker/)  
 * so all local testing configuration (like network, image template url, primary storage nfs root) could be modified locally. It will keep config files uncontaminated in zstack-woodpecker repository
 * edit ~/.zstackwoodpecker/integrationtest/vm/deploy.tmpt and make sure it reflect local environment. Basic and virtualroute test suite will share this config ini file. For detailed config content, it is in every test suite's folder, like ~/.zstackwoodpecker/integrationtest/vm/basic/deploy.xml and ~/.zstackwoodpecker/integrationtest/vm/virtualrouter/deploy.xml . These xml file was not supposed to be changed. The .xml and .tmpt file path was set in test-config.xml file in each test suite's folder, like ~/.zstackwoodpecker/integrationtest/vm/basic/test-config.xml , this file will be used in next step when executing woodpecker test cases. 

#6. Run basic test suite
 * Environment Requirement: 1~2 test machine (1 for mn 1 for host, or mn and host in single machine), step 1~4 on mn, , mysql server and rabbitmq-server should be installed and started up. 
 * `cd /home/zstack/zstack-woodpecker/dailytest`  
 * `./zstest.py -s basic` (or -s b, -s ba, -s basi) (The suite test case list is defined in   `/home/zstack/zstack-woodpecker/integrationtest/vm/basic/integration.xml)`  
 * For single test case:  
   * `./zstest.py -l (list all test cases)`  
   * `./zstest.py -l -s basic` (list test cases in basic test suite)  
   * `./zstest.py -c case_name` (or test case number) (run specific test case, if the test case is not the suite_setup, please make sure the suite_setup is already executed.)  
   * `./zstest.py -c case_name -r 10 -p 2` (run test case 10 times with 2 cases parallel execution)  
 * If not use '-C config_file_path' option, Woodpecker will firstly find the test config file (test-config.xml) in local environment folder, like  ~/.zstackwoodpecker/integrationtest/vm/basic/test-config.xml (when executing test case in basic test suite). If the local file is missed, it will use the file in repository, like  /home/zstack/zstack-woodpecker/integrationtest/vm/basic/test-config.xml 
 * In order to test iscsi primary storage, it is needed to edit environment config ini: ~/.zstackwoodpecker/integrationtest/vm/basic/deploy-iscsi-fs.tmpt and when executing basic test suite for iscsi, it is needed to run this command: ./zstest.py -s b -C ~/.zstackwoodpecker/integrationtest/vm/basic/test-config-iscsi-fs-backend.xml
 * for more zstest.py parameters, please using -h option. 

#7. Run virtual route test suite
 * Environment Requirement: 1~2 test machine (1 for mn 1 for host, or mn and host in single machine), step 1~4 on mn, mysql server and rabbitmq-server should be installed and started up. 
 * environment config file: ~/.zstackwoodpecker/integrationtest/vm/deploy.tmpt
 * `./zstest.py -s vir`  

#8. Run multi hosts test suite
 * Environment Requirement: 4 or 5 test machines (1 mn + 4 hosts, or 4 hosts with mn on 1 host), execute step 1~4 on mn, mysql server and rabbitmq-server should be installed and started up. 
 * environment config file: ~/.zstackwoodpecker/integrationtest/vm/multihosts/deploy.tmpt
 * `./zstest.py -s multihost`  

#9. Run multi zones test suite
 * Environment Requirement: 4 or 5 test machines (1 mn + 4 hosts, or 4 hosts with mn on 1 host), execute step 1~4 on mn, mysql server and rabbitmq-server should be installed and started up. 
 * environment config file: ~/.zstackwoodpecker/integrationtest/vm/multizones/deploy.tmpt
 * `./zstest.py -s multizones`  
