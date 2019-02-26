package utils

import (
	"fmt"
	"bytes"
	"golang.org/x/crypto/ssh"
	"github.com/tmc/scp"
)

func Connect(host string, port string, username string, password string) (*ssh.Client, *ssh.Session, error) {
	config := &ssh.ClientConfig {
		User: username,
		Auth: []ssh.AuthMethod {
			ssh.Password(password)},
		HostKeyCallback: ssh.InsecureIgnoreHostKey(),
	}

	client, err := ssh.Dial("tcp", fmt.Sprintf("%s:%s", host, port ), config)
	if err != nil {
		return nil, nil, err
	}

	session, err := client.NewSession()
	if err != nil {
		return nil, nil, err
	}
	return client, session, err
}

func ExecuteCommand(host string, port string, username string, password string, command string) (string, error) {
	client, session, err := Connect(host, port, username, password)
	if err != nil {
		return "", err
	}
	defer session.Close()
	var b bytes.Buffer
	session.Stdout = &b
	err = session.Run(command)
	if err != nil {
		client.Close()
		return "", err
	}

	client.Close()
	return b.String(), nil
}

func ScpFile(host string, port string, username string, password string, filePath string, destPath string) error {
	client, session, err := Connect(host, port, username, password)
	if err != nil {
		return err
	}
	defer session.Close()
	err = scp.CopyPath(filePath, destPath, session)
	if err != nil {
		client.Close()
		return err
	}

	client.Close()
	return nil
}
