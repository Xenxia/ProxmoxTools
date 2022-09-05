package cli

import (
    "fmt"

    "github.com/urfave/cli/v2"
)


var cliConfig = cli.Command{
    Name: "config",
    Usage: "Get the configuration of the virtual machine or container with\nthe current configuration changes applied. Set the current\nparameter to get the current configuration instead.",
    UsageText: "vm config <vmid>",
    
    Before: func(ctx *cli.Context) error {
        if ctx.NArg() < 1 { return cli.Exit("One argument attempt", 3)}
        if ctx.NArg() >= 2 { return cli.Exit("One argument attempt", 3)}
        return nil
    },

    Action: func(ctx *cli.Context) error {
        ctx.Args()
        fmt.Println(ctx.Args())
        return nil
    },
}