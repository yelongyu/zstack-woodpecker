package main

import (
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

	flag.Parse()

	if options.Ip == "" {
		abortOnWrongOption("error: the options 'ip' is required")
	}

	server.SetOptions(options)
}

func main()  {
	parseCommandOptions()
	utils.InitLog(options.LogFile, false)
	loadPlugins()
	server.Start()
}
