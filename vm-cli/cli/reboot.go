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

var cliReboot = cli.Command{
	Name:      "reboot",
	Usage:     "Reboot virtual machine. <vmid> is the (unique) ID of the VM. Reboot multiple VM\\CTs with : 100.101 | Reboot All machine with : all",
	UsageText: "vm reboot <vmid>\nvm reboot 100.101\nvm reboot all",

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
			
			reboot(machines.Machines)
			return nil
		}
		
		var ms []vm.Machine
		for _, id := range vmid {
			m, _ := machines.Get_Machine(id)
			ms = append(ms, m)
		}
		reboot(ms)

		return nil
	},
}

func reboot(ms []vm.Machine) {

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

			spin.EditMessage("Reboot " + m.Name + ":" + m.Vmid)

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

				m.Reboot()
				
				cancel()
				time.Sleep(time.Millisecond * 200)

				var start bool
				
				if m.Status == "stopped" {
					spin.EditMessage("Is not started " + m.Name + ":" + m.Vmid)
					start = true
				} else {
					spin.EditMessage("Rebooted " + m.Name + ":" + m.Vmid)
					start = false
				}
				
				spin.Done(false, start)
			} else {
				cancel()
				time.Sleep(time.Millisecond * 200)
				
				spin.EditMessage("Is not running " + m.Name + ":" + m.Vmid)
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

