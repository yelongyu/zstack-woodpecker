Zstack_Base_Image_Name='zstack_base_centos_image'
Zstack_Test_Image_Name='zstack_test_centos_image'

help(){
    echo "Usage: $0 [Options]"
    echo Docker image creation facility script. It should be executed  under \
woodpecker/docker/centos/ folder. 
    echo "
[Options:]
	-z ZSTACK_PATH	the path of zstack.war. 
	-b NAME		[Optional] set ZStack Base Image Name, which will be 
			used for creating zstack test image. 
			Default Value: $Zstack_Base_Image_Name
	-t NAME		[Optional] set ZStack Test Image Name, which will be 
			used for running zstack by \`docker run -d NAME\`
			Default Value: $Zstack_Test_Image_Name
	-h		show this help message and exit
"
    exit 1
}

[ $# -eq 0 ] && help

zstack_path=' '

OPTIND=1
while getopts "z:b:t:h" Option
do
    case $Option in
        z ) zstack_path=$OPTARG;;
        b ) Zstack_Base_Image_Name=$OPTARG;;
        t ) Zstack_Test_Image_Name=$OPTARG;;
        h ) help;;
        * ) help;;
    esac
done
OPTIND=1

if [ ! -f $zstack_path ]; then
    echo $zstack_path does not exist. It should be a path of zstack.war
    help
fi

DIR_PATH=`dirname $0`
Zstack_Base_Docker=${DIR_PATH}/host-docker-img
Zstack_Base_Docker_File=${Zstack_Base_Docker}/Dockerfile

if [ ! -f $Zstack_Base_Docker_File ]; then
    echo $Zstack_Base_Docker_File does not exist. 
    help 
fi

Zstack_Test_Docker=${DIR_PATH}/test-img
Zstack_Test_Docker_File=${Zstack_Test_Docker}/Dockerfile
if [ ! -f $Zstack_Test_Docker_File ]; then
    echo "$Zstack_Test_Docker_File does not exist. "
    help 
fi

echo "Create new centos jail root ..."
febootstrap -i iputils -i vim-minimal -i iproute -i bash -i coreutils -i yum -i mysql-server -i python-setuptools -i java-1.6.0-openjdk-devel -i wget -i openssh-clients -i telnet centos centos http://mirror.centos.org/centos/6.5/os/x86_64/ -u http://mirror.centos.org/centos/6.5/updates/x86_64/
echo "Jail root create successfully"

echo "import initial centos image..."
cd centos
tar -c . |docker import - centos
cd ..

echo "create zstack base image"
cd $Zstack_Base_Docker
docker build -t $Zstack_Base_Image_Name .
cd ..

echo "create zstack test image"
cd $Zstack_Test_Docker
docker build -t $Zstack_Test_Image_Name .
cd ..

echo "
$Zstack_Test_Image_Name is created.
ZStack service could be run in docker by docker run -d $Zstack_Test_Image_Name
A local jailroot ${DIR_PATH}/centos was also created. 
"
