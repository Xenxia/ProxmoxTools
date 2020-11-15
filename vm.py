#!/usr/bin/env python3

# MIT License

# Copyright (c) 2020 Xenxia

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os, sys, argparse
from os import system, name
from time import sleep

version="1.0.0"

#? Color ------------------------------------------------------------------------------->
class co:
    Reset = "\033[0m"+"\n"

    Default      = "\u001b[0m"
    Black        = "\u001b[38;5;0m"
    Red          = "\u001b[38;5;160m"
    Green        = "\u001b[38;5;82m"
    Yellow       = "\u001b[38;5;226m"
    Blue         = "\u001b[38;5;27m"
    Magenta      = "\033[35m"
    Cyan         = "\033[36m"

#? Argument parser ------------------------------------------------------------------------------->
parser = argparse.ArgumentParser(description="Application to merge the 'qm' and 'pct' commands from proxmox")
parser.add_argument('-v', '--version', action='version', version=co.Green+version+co.Default)
parser.add_argument("-l", "--list", action="store_true", help ="List all vm")
parser.add_argument("-start", type=int, metavar='VMID', help ="Start vm")
parser.add_argument("-stop", type=int, metavar='VMID', help ="Stop vm")
parser.add_argument("-reboot", type=int, metavar='VMID', help ="Reboot vm")
parser.add_argument("-console", type=int, metavar='VMID', help ="Open console vm 'for lxc vm'")
args = parser.parse_args()

#? Fonction ----------------------------------------------------------------------------------------->
def Clear():
    _ = system('clear')

def Exit():
    raise SystemExit(0)

def List_vm():

    vm_dico = {}
    vm_dico[0] = {'#1' : 'VMID', '#2' : 'Status', '#3' : 'Type', '#4' : 'Name'}
    List_pct = os.popen("pct list", "r").read();
    List_qm = os.popen("qm list", "r").read();
    num_dict = int(1);

    ###############
    # VM LXC LIST #
    ###############

    for ligne in List_pct.split("\n"):
        num = int(1)
        vm_dico[num_dict] = {'VM_ID' : '', 'Status' : '', 'Tag' : '', 'Name' : ''}
        
        for string in ligne.split(" "):
        
            if string != "" and string != "VMID" and string != "Status" and string != "Lock" and string != "Name":

                if num == 1:
                    vm_dico[num_dict]['VM_ID'] = string

                if num == 2:
                    vm_dico[num_dict]['Status'] = string

                if num == 3:
                    vm_dico[num_dict]['Name'] = string
                    vm_dico[num_dict]['Tag'] = "LXC"
                    num_dict = num_dict+1

                num = num+1

    ################
    # VM QEMU LIST #
    ################

    for ligne in List_qm.split("\n"):
        num = int(1)
        vm_dico[num_dict] = {'VM_ID' : '', 'Status' : '', 'Tag' : '', 'Name' : ''}
        
        for string in ligne.split(" "):
        
            if string != "" and string != "VMID" and string != "STATUS" and string != "NAME" and string != "MEM(MB)" and string != "BOOTDISK(GB)" and string != "PID":

                if num == 1:
                    vm_dico[num_dict]['VM_ID'] = string

                if num == 2:
                    vm_dico[num_dict]['Name'] = string

                if num == 3:
                    vm_dico[num_dict]['Status'] = string
                    vm_dico[num_dict]['Tag'] = "QM"
                    num_dict = num_dict+1

                num = num+1

    return vm_dico

def Check_IDVM(ID_vm):

    if int(ID_vm) >= 100 and int(ID_vm) <= 999:
        return ID_vm
    
    print(co.Red+str(ID_vm)+' ID incorect'+co.Reset)
    Exit()

def Search_VM(ID_vm):

    vm_dico = List_vm()
    num_vm_pct = len(vm_dico)

    for x in range(1,num_vm_pct):
        for valeur in vm_dico[x].values():
            if valeur == str(ID_vm):
                return vm_dico[x]

def Start_VM(vm):

    if vm == None:
        print(co.Red+"No vm"+co.Reset)

    else:
        if vm["Status"] == "running":
            print(co.Magenta+"VM Already "+co.Green+"started "+co.Magenta+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

        elif vm["Tag"] == "LXC":
            print(co.Yellow+"Start Container "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
            os.system('pct start '+ str(vm["VM_ID"]))
            print(co.Green+"Started Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

        elif vm["Tag"] == "QM":
            print(co.Yellow+"Start VM "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
            os.system('qm start '+ str(vm["VM_ID"]))
            print(co.Green+"Started VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

def Stop_VM(vm):

    if vm == None:
        print(co.Red+"No vm"+co.Reset)

    else:
        if vm["Status"] == "stopped":
            print(co.Magenta+"VM Already "+co.Red+"stopped "+co.Magenta+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

        elif vm["Tag"] == "LXC":
            print(co.Yellow+"Stop Container "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
            os.system('pct stop '+ str(vm["VM_ID"]))
            print(co.Green+"Stopped Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

        elif vm["Tag"] == "QM":
            print(co.Yellow+"Stop VM "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
            os.system('qm stop '+ str(vm["VM_ID"]))
            print(co.Green+"Stopped VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

def Reboot_VM(vm):

    if vm == None:
        print(co.Red+"No vm"+co.Reset)

    elif vm["Tag"] == "LXC":
        print(co.Yellow+"Reboot Container "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
        os.system('pct reboot '+ str(vm["VM_ID"]))
        print(co.Green+"Rebooted Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "QM":
        print(co.Yellow+"Reboot VM "+vm["Name"]+':'+vm["VM_ID"]+co.Default)
        os.system('qm reboot '+ str(vm["VM_ID"]))
        print(co.Green+"Rebooted VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)


def Console_VM(vm):

    if vm == None:
        print(co.Red+"No vm"+co.Reset)

    elif vm["Tag"] == "LXC":
        print(co.Yellow+"Exit the console Ctrl+a q"+co.Reset)
        os.system('pct console '+ str(vm["VM_ID"])+' -escape ^a')
        Clear()

    elif vm["Tag"] == "QM":
        print(co.Yellow+"use 'qm terminal' and config serial"+co.Reset)

#? Start ----------------------------------------------------------------------------------------->

print()

if args.start:

    vm_info = Search_VM(Check_IDVM(args.start))
    Start_VM(vm_info)
    Exit()

if args.stop:

    vm_info = Search_VM(Check_IDVM(args.stop))
    Stop_VM(vm_info)
    Exit()

if args.reboot:

    vm_info = Search_VM(Check_IDVM(args.reboot))
    Reboot_VM(vm_info)
    Exit()

if args.console:

    vm_info = Search_VM(Check_IDVM(args.console))
    Console_VM(vm_info)
    Exit()

if args.list:

    Clear()
    print("\n")

    vm_dico = List_vm()

    num_vm_pct = len(vm_dico)

    form_header = "{0:6}{1:10}{2:6}{3:10}"
    form_Stop = "{0:6}"+co.Red+"{1:10}"+co.Default+"{2:6}{3:10}"
    form_Start = "{0:6}"+co.Green+"{1:10}"+co.Default+"{2:6}{3:10}"
    dash = '-' * 40

    for x in range(0,num_vm_pct-1):

        vm_print = list(vm_dico[x].values())

        if x != 0:
            if vm_print[1] == 'stopped':
                print(form_Stop.format(*vm_print))
            elif vm_print[1] == 'running':
                print(form_Start.format(*vm_print))
        else:
            print(dash)
            print(form_header.format(*vm_print))
            print(dash)
    
    print(co.Reset)

    Exit()

print(co.Red+'No argument detected'+co.Reset)

parser.print_help()

print('\n')