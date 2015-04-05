#!/bin/sh
# This script should be put under ~/.zstackwoodpecker/extra_zstack_config.sh
# This script is to do additional config, when doing integration test.
# Integration test deploy will call this script, after unzip zstack.war and 
# copy the zstack.properties.

[ $# -lt 1 ] && echo "Usage: #$0 CATALINA_HOME" && exit 1

catalina_home=$1
script_dir=`dirname $0`

#enable appliancevm and virutalrouter service deployment when starting vr
#sed -i "s/false/true/" $catalina_home/webapps/zstack/WEB-INF/classes/globalConfig/applianceVm.xml
#sed -i "s/false/true/" $catalina_home/webapps/zstack/WEB-INF/classes/globalConfig/virutalRouter.xml


#enable kvm simulator
#cd $catalina_home/webapps/zstack/WEB-INF/classes/
#yes | cp simulatorBeanRefContext.xml beanRefContext.xml

#only enable WARN and above level log
#sed -i 's/DEBUG/WARN/' $catalina_home/webapps/zstack/WEB-INF/classes/log4j-cloud.xml
#sed -i 's/TRACE/WARN/' $catalina_home/webapps/zstack/WEB-INF/classes/log4j-cloud.xml
#enable extra log. log_lines.xml should be in same folder of this script. It include additional log config, which will be added below </root> label
#extra_log=$script_dir/log_lines.xml
#sed -i "/<\/root>/r $extra_log" $catalina_home/webapps/zstack/WEB-INF/classes/log4j-cloud.xml 
