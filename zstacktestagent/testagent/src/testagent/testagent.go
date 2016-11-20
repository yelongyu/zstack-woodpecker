package main

import (
	"strings"
	"testagent/server"
	"testagent/plugin"
	"testagent/utils"
	"fmt"
	"flag"
	"os"
)

func loadPlugins()  {
	plugin.VmEntryPoint()
	plugin.HostEntryPoint()
	plugin.MiscEntryPoint()
}

var options server.Options

func abortOnWrongOption(msg string) {
	fmt.Println(msg)
	flag.Usage()
	os.Exit(1)
}

func parseCommandOptions() {
	options = server.Options{}
	flag.StringVar(&options.Ip, "ip", "", "The IP address the server listens on")
	flag.UintVar(&options.Port, "port", 7272, "The port the server listens on")
	flag.UintVar(&options.ReadTimeout, "readtimeout", 10, "The socket read timeout")
	flag.UintVar(&options.WriteTimeout, "writetimeout", 10, "The socket write timeout")
	flag.StringVar(&options.LogFile, "logfile", "testagent.log", "The log file path")
	flag.StringVar(&options.Type, "type", "", "host type")

	flag.Parse()

	if options.Ip == "" {
		abortOnWrongOption("error: the options 'ip' is required")
	}

	server.SetOptions(options)
}

func configureFirewall() {
	var Commands []string
	Commands = append(Commands, fmt.Sprintf("$SET firewall name eth0.local rule %d action accept", options.Port))
	Commands = append(Commands, fmt.Sprintf("$SET firewall name eth0.local rule %d destination address %s", options.Port, options.Ip))
	Commands = append(Commands, fmt.Sprintf("$SET firewall name eth0.local rule %d destination port %d", options.Port, options.Port))
	Commands = append(Commands, fmt.Sprintf("$SET firewall name eth0.local rule %d protocol tcp", options.Port))
	server.RunVyosScriptAsUserVyos(strings.Join(Commands, "\n"))
}

func main()  {
	parseCommandOptions()
	utils.InitLog(options.LogFile, false)
	loadPlugins()
//	if options.Type == "vyos" {
//		configureFirewall()
//	}
	server.Start()
}
