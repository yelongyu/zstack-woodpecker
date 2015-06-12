WOODPECKER_VIRTUALENV=/var/lib/zstack/virtualenv/woodpecker
VIRTUALENV_ACT=$WOODPECKER_VIRTUALENV/bin/activate
if [ ! -f $VIRTUALENV_ACT ]; then
    echo "Not find virutalenv in $WOODPECKER_VIRTUALENV. It should be created by virtualenv and install apibinding and zstacklib firstly. The easiest way is to run \`./install_woodpecker_env.sh zstacklib.tar.gz apibinding.tar.gz\`"
fi

. $VIRTUALENV_ACT

python `dirname $0`/zstest.py $*

