package cli

import (
    "log"
    "os"
    "time"

    "github.com/urfave/cli/v2"
)

func Init() {

    app := &cli.App{
        Name: "VM-cli",
        Version: "1.0.0",
        Usage: "Application to merge the 'qm', 'pct' and 'vz' commands from proxmox",
        HelpName: "vm",
        Compiled: time.Now(),
        Commands: []*cli.Command{
            &cliList,
            &cliConfig,
            &cliStart,
            {
                Name: "stop",
            },
            {
                Name: "reboot",
            },
            {
                Name: "console",
            },
            {
                Name: "delete",
            },
            {
                Name: "clone",
            },
            {
                Name: "backup",
            },
        },
    }

    if err := app.Run(os.Args); err != nil {
        log.Fatal(err)
    }

    // return app
}