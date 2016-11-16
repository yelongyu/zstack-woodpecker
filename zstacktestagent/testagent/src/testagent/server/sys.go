package server

import (
	"testagent/utils"
	"fmt"
	"io/ioutil"
	"os"
	"github.com/Sirupsen/logrus"
)

func RunVyosScriptAsUserVyos(command string) string {
	template := `export vyatta_sbindir=/opt/vyatta/sbin
SET=${vyatta_sbindir}/my_set
DELETE=${vyatta_sbindir}/my_delete
COPY=${vyatta_sbindir}/my_copy
MOVE=${vyatta_sbindir}/my_move
RENAME=${vyatta_sbindir}/my_rename
ACTIVATE=${vyatta_sbindir}/my_activate
DEACTIVATE=${vyatta_sbindir}/my_activate
COMMENT=${vyatta_sbindir}/my_comment
COMMIT=${vyatta_sbindir}/my_commit
DISCARD=${vyatta_sbindir}/my_discard
SAVE=${vyatta_sbindir}/vyatta-save-config.pl
API=/bin/cli-shell-api

session_env=$($API getSessionEnv $PPID)
echo $session_env
eval $session_env
$API setupSession

%s
$COMMIT
if [ $? -ne 0 ]; then
	echo "fail to commit"
	exit 1
fi

function atexit() {
    $API teardownSession
}

trap atexit EXIT SIGHUP SIGINT SIGTERM
`
	command = fmt.Sprintf(template, command)
	tmpfile, err := ioutil.TempFile("", "zvr"); utils.PanicOnError(err)
	defer os.Remove(tmpfile.Name())

	err = ioutil.WriteFile(tmpfile.Name(), []byte(command), 0777); utils.PanicOnError(err)
	tmpfile.Sync()
	tmpfile.Close()
	logrus.Debugf("[Configure VYOS]: %s\n", command)
	bash := utils.Bash{
		Command: fmt.Sprintf(`chown vyos:users %s; chmod +x %s; %v`, tmpfile.Name(), tmpfile.Name(), tmpfile.Name()),
	}
	_, o, _, err := bash.RunWithReturn()
	bash.PanicIfError()
	return o
}
