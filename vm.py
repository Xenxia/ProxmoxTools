#!/usr/bin/env python3

import os, sys, argparse
from os import system, name
from time import sleep

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
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--list", action="store_true", help ="List vm")
parser.add_argument("-c", "--command", action="store_true", help ="Open comande line")
parser.add_argument("-start", type=int, metavar='VMID', help ="Start vm")
parser.add_argument("-stop", type=int, metavar='VMID', help ="Stop vm")
args = parser.parse_args()

#? Fonction ----------------------------------------------------------------------------------------->
def Clear():
    _ = system('clear')

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
    
    print(co.LightRed+str(ID_vm)+' ID incorect'+co.Reset)
    raise SystemExit(0)

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

    elif vm["Tag"] == "LXC":
        print(co.Yellow+"Start Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)
        os.system('pct start '+ str(vm["VM_ID"]))
        print(co.Green+"Started Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "QM":
        print(co.Yellow+"Start VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)
        os.system('qm start '+ str(vm["VM_ID"]))
        print(co.Green+"Started VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

def Stop_VM(vm):

    if vm == None:
        print(co.Red+"No vm"+co.Reset)

    elif vm["Tag"] == "LXC":
        print(co.Yellow+"Stop Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)
        os.system('pct stop '+ str(vm["VM_ID"]))
        print(co.Green+"Stopped Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "QM":
        print(co.Yellow+"Stop VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)
        os.system('qm stop '+ str(vm["VM_ID"]))
        print(co.Green+"Stopped VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

def Reboot_VM(vm):

    if vm == None:
        print(co.Red+"No vm"+co.Reset)

    elif vm["Tag"] == "LXC":
        print(co.Yellow+"Reboot Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)
        os.system('pct reboot '+ str(vm["VM_ID"]))
        print(co.Green+"Rebooted Container "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)

    elif vm["Tag"] == "QM":
        print(co.Yellow+"Reboot VM "+vm["Name"]+':'+vm["VM_ID"]+co.Reset)
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

Clear()
print("\n")

if args.start:

    vm_info = Search_VM(Check_IDVM(args.start))
    Start_VM(vm_info)
    raise SystemExit(0)

if args.stop:

    vm_info = Search_VM(Check_IDVM(args.stop))
    Stop_VM(vm_info)
    raise SystemExit(0)

if args.list:

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
            

    print(co.Blue+"\nenter '0' to exit"+co.Reset)

    choiced_vm = input('Enter VM ID : ')

    if choiced_vm == '0':
        raise SystemExit(0)

    vm_info = Search_VM(Check_IDVM(choiced_vm))

    Clear()
    print('\n'+dash)
    print(co.Cyan+'VM selected'+co.Default)
    print('ID : '+vm_info['VM_ID'])
    print('Name : '+vm_info['Name'])
    if vm_info['Status'] == 'stopped':
        print('Status : '+co.Red+'Stopped'+co.Default)
    elif vm_info['Status'] == 'running':
        print('Status : '+co.Green+'Running'+co.Default)
    print(dash)
    print('1 : Start')
    print('2 : Stop')
    print('3 : Restart')
    print('4 : Console')

    choiced_Action = input('\nAction : ')
    print('\n')

    if choiced_Action == '1':
        Start_VM(vm_info)
    elif choiced_Action == '2':
        Stop_VM(vm_info)
    elif choiced_Action == '3':
        Reboot_VM(vm_info)
    elif choiced_Action == '4':
        Console_VM(vm_info)
    
    raise SystemExit(0)

if args.command:
    print('c')

# print('finish')