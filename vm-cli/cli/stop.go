package cli

import (
	"context"
	"strings"
	"sync"
	"time"
	"vm-cli/term"
	"vm-cli/util"
	"vm-cli/vm"

	"github.com/urfave/cli/v2"
)

var cliStop = cli.Command{
	Name:      "stop",
	Usage:     "Stop virtual machine. <vmid> is the (unique) ID of the VM. Stop multiple VM\\CTs with : 100.101 | Stop All machine with : all",
	UsageText: "vm stop <vmid>\nvm stop 100.101\nvm stop all",
	Flags: []cli.Flag{
		&cli.BoolFlag{
			Name:    "force",
			Aliases: []string{"f"},
			Usage:   "Force Shutdown",
		},
	},

	Before: func(ctx *cli.Context) error {
		if ctx.NArg() < 1 {
			return cli.Exit("One argument attempt", 3)
		}
		if ctx.NArg() >= 2 {
			return cli.Exit("One argument attempt", 3)
		}

		var v []string
		vmid := ctx.Args().First()

		if strings.Contains(vmid, ".") {
			v = strings.Split(vmid, ".")
		} else {
			v = []string{vmid}
		}

		ctx.Context = context.WithValue(ctx.Context, "vmid", v)

		return nil
	},

	Action: func(ctx *cli.Context) error {

		machines := vm.Get_Machines()

		vmid := ctx.Context.Value("vmid").([]string)

		if vmid[0] == "all" {
			
			stop(machines.Machines, ctx.Bool("force"))
			return nil
		}
		
		var ms []vm.Machine
		for _, id := range vmid {
			m, _ := machines.Get_Machine(id)
			ms = append(ms, m)
		}
		stop(ms, ctx.Bool("force"))

		return nil
	},
}

func stop(ms []vm.Machine, force bool) {

	var wg sync.WaitGroup
	var lplus int

	l := term.GetCursorPos().Line
	t, _ := term.GetTermSize()
	mnum := len(ms)

	if l+mnum > int(t.Line) {
		l = l-mnum
		term.ScrollUp(mnum+1)
		term.MoveCursor(int(l), 0)
	} else {
		l = l+1
		term.MoveDownCursor(2)

	}

	term.HideCursor()

	for i, m := range ms {

		wg.Add(1)

		go func(m vm.Machine, i int) {

			ctx, cancel := context.WithCancel(context.Background())

			spin := util.NewSpinners(11, 0, l+i, 0)

			spin.EditMessage("Stop " + m.Name + ":" + m.Vmid)

			go func() {
				for {
					select {
					case <-ctx.Done():
						return
					default:
						time.Sleep(time.Millisecond * 100)
						spin.Next()
					}
				}

			}()

			// time.Sleep(time.Millisecond * 5000)
			if m.Status == "running" {

				i := 0

				m.Stop(force)

				for m.Status == "running" {
					
					m.Update()
					time.Sleep(time.Millisecond * 1000)

					if i > 2 {
						break
					}

					i += 1
				}
				
				cancel()
				time.Sleep(time.Millisecond * 200)

				var start bool
				
				if m.Status == "running" {
					spin.EditMessage("Is not stopped " + m.Name + ":" + m.Vmid)
					start = true
				} else {
					spin.EditMessage("Stopped " + m.Name + ":" + m.Vmid)
					start = false
				}
				
				spin.Done(false, start)
			} else {
				cancel()
				time.Sleep(time.Millisecond * 200)
				
				spin.EditMessage("Is already stopped " + m.Name + ":" + m.Vmid)
				spin.Done(true, false)
			}
			
			time.Sleep(time.Millisecond * 100)
			
			wg.Done()
		}(m, i)

		time.Sleep(time.Millisecond * 500)

		lplus = i
	}

	wg.Wait()
	term.MoveCursor(int(l+mnum), 0)

	if l+lplus+1 >= int(t.Line) {
		term.ScrollUp(1)
	} else {
		term.MoveDownCursor(1)
	}

	term.ShowCursor()
}

