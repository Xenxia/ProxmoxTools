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

import argparse
import os
import subprocess
import re as regex
import sys
from argparse import RawTextHelpFormatter
from operator import itemgetter

version = "4.0.0"


# ? Color ------------------------------------------------------------------------------->
class Color:
    RESET = "\u001b[0m" + "\n"
    CLEAR = "\u001b[0m"

    DEFAULT = "\u001b[0m"
    BLACK = "\u001b[38;5;0m"
    WHITE = "\u001b[38;5;255m"
    RED = "\u001b[38;5;160m"
    GREEN = "\u001b[38;5;82m"
    YELLOW = "\u001b[38;5;226m"
    ORANGE = "\u001b[38;5;208m"
    BLUE = "\u001b[38;5;27m"
    MAGENTA = "\u001b[38;5;207m"
    CYAN = "\u001b[38;5;51m"

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    REVERSE = "\033[;7m"


# ? Argument parser ------------------------------------------------------------------------------->

parser = argparse.ArgumentParser(description="Application to merge the 'qm', 'pct' commands from proxmox",
                                 allow_abbrev=False,
                                 prog='vm-cli',
                                 usage="%(prog)s"
                                 )

subparsers = parser.add_subparsers(title='Commande',
                                   dest='Command_Name',
                                   )

parser_list = subparsers.add_parser('list', help='[OPTION] shows the list of all VMs',
                                    formatter_class=RawTextHelpFormatter)
parser_list.add_argument('-sort', choices=['status', 'type', 'name'],
                         help='Default sort by ID VM\n'
                              'status = sort by STATUS VM running/stopped\n'
                              'type = sort by TYPE VM : LXC/QM\n'
                              'name = sort by NAME VM'
                         )
parser_list.add_argument('-r', '-reverse', action="store_true", dest='REVERSE', help='reverse sort.')

parser_config = subparsers.add_parser('config',
                                      help='<vmID> [OPTION] Get the configuration of the virtual machine or container with '
                                           'the current configuration changes applied. Set the current '
                                           'parameter to get the current configuration instead.')
parser_config.add_argument('VMID', metavar='vmID', type=int, help='The (unique) ID of the VM.')
parser_config.add_argument('-current', action="store_true", help='Get current values (instead of pending values).',
                           dest='CURRENT')
parser_config.add_argument('-snapshot', type=str, help='Fetch config values from given snapshot.', dest='SNAPSHOT')

parser_start = subparsers.add_parser('start', help="<vmID's> Start VM")
parser_start.add_argument('VMID_LIST', metavar="vmID's", type=str,
                          help='The (unique) ID of the VM. Start multiple VM\CTs with : 100.101')

parser_stop = subparsers.add_parser('stop', help="<vmID's> Stop VM")
parser_stop.add_argument('VMID_LIST', metavar="vmID's", type=str,
                         help='The (unique) ID of the VM. Stop multiple VM\CTs with : 100.101')

parser_reboot = subparsers.add_parser('reboot', help="<vmID's> Reboot VM")
parser_reboot.add_argument('VMID_LIST', metavar="vmID's", type=str,
                           help='The (unique) ID of the VM. Reboot multiple VM\CTs with : 100.101')

parser_console = subparsers.add_parser('console', help="<vmID> Open console vm 'for lxc vm'")
parser_console.add_argument('VMID', metavar='vmID', type=int, help='The (unique) ID of the VM.')

parser_destroy = subparsers.add_parser('destroy',
                                       help='<vmID> [OPTION] Destroy the container (also delete all uses files).')
parser_destroy.add_argument('VMID', metavar='vmID', type=int, help='The (unique) ID of the VM.')
parser_destroy.add_argument('-p', '-purge', action='store_true', dest='PURGE',
                            help='Remove container from all related configurations.')

parser_clone = subparsers.add_parser('clone', help='<vmID> <newID> [OPTION] Create a container clone/copy')
parser_clone.add_argument('VMID', metavar='vmID', type=int, help='The (unique) ID of the VM.')
parser_clone.add_argument('newID', type=int, help='vmID for the clone.')
parser_clone.add_argument('-bwlimit', type=int, help='Override I/O bandwidth limit (in KiB/s).', dest='BWLIMIT')
parser_clone.add_argument('-description', type=str, help='Description for the new CT/VM.', dest='DESCRIPTION')
parser_clone.add_argument('-full', action="store_true",
                          help='Create a full copy of all disks. This is always done when you clone a normal CT/VM.'
                               'For CT templates, we try to create a linked clone by default.',
                          dest='FULL'
                          )
parser_clone.add_argument('-name', type=str, help='Set a hostname/name for the new CT/VM.', dest='NAME')
parser_clone.add_argument('-pool', type=str, help='Add the new CT to the specified pool.', dest='POOL')
parser_clone.add_argument('-snapname', type=str, help='The name of the snapshot.', dest='SNAPNAME')
parser_clone.add_argument('-storage', type=str, help='Target storage for full clone.', dest='STORAGE')
parser_clone.add_argument('-target', type=str,
                          help='Target node. Only allowed if the original VM is on shared storage.',
                          dest='TARGET'
                          )
parser_clone.add_argument('-format', choices=['qcow2', 'raw', 'vmdk'],
                          help='Target format for file storage. Only valid for full clone. (Only QEMU VM)',
                          dest='FORMAT'
                          )

group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--version', action='version', version=Color.GREEN + version + Color.DEFAULT)

args = parser.parse_args()

if args.Command_Name is None:
    print('\n' + Color.RED + 'One argument expected' + Color.RESET)
    parser.print_help()
    print('\n')
    sys.exit()


# ? Function sys ------------------------------------------------------------------------------------->

def clear() -> None: os.system("printf '\033c'")


# ? Class ----------------------------------------------------------------------------------------->

class Main_vm:
    __vm_list: list = []

    def __init__(self) -> None:

        list_pct = os.popen("pct list", "r").read()
        list_qm = os.popen("qm list", "r").read()

        ###############
        # VM LXC LIST #
        ###############

        for line in list_pct.split("\n"):

            if line != "":

                num = int(1)
                temp_dict: dict = {'vm_ID': '', 'Status': '', 'Tag': '', 'Name': ''}

                for string in line.split(" "):

                    if string != "" and string != "VMID" and string != "Status" and string != "Lock" and string != "Name":

                        if num == 1:
                            temp_dict['vm_ID'] = string

                        elif num == 2:
                            temp_dict['Status'] = string

                        elif num == 3:
                            temp_dict['Name'] = string
                            temp_dict['Tag'] = "LXC"

                        num += 1

                if temp_dict['vm_ID'] != "":
                    self.__vm_list.append(temp_dict)

        ################
        # VM QEMU LIST #
        ################

        for line in list_qm.split("\n"):

            if line != "":

                num = int(1)
                temp_dict: dict = {'vm_ID': '', 'Status': '', 'Tag': '', 'Name': ''}

                for string in line.split(" "):

                    if string != "" and string != "VMID" and string != "STATUS" and string != "NAME" and string != "MEM(MB)" and string != "BOOTDISK(GB)" and string != "PID":

                        if num == 1:
                            temp_dict['vm_ID'] = string

                        elif num == 2:
                            temp_dict['Name'] = string

                        elif num == 3:
                            temp_dict['Status'] = string
                            temp_dict['Tag'] = "QM"

                        num += 1

                if temp_dict['vm_ID'] != "":
                    self.__vm_list.append(temp_dict)

    @staticmethod
    def __check_ID(ID_vm: str) -> None:

        if 100 <= int(ID_vm) <= 999:
            return None

        print(Color.RED + ID_vm + ' ID incorect' + Color.RESET)
        sys.exit()

    def __exist_VM(self, ID_vm: str) -> None:

        self.__check_ID(ID_vm)

        for vmDict in self.__vm_list:
            for value in vmDict.values():
                if value == str(ID_vm):
                    return None

        sys.exit(Color.RED + "No existing VM ID:" + ID_vm + Color.RESET)

    def __research_VM(self, ID_vm: str) -> dict:

        for vmDict in self.__vm_list:
            for value in vmDict.values():
                if value == str(ID_vm):
                    return vmDict

    def regex_vmID(self, str_ID_vm: str) -> list:

        if not regex.search(r'[.]{2,}|[^.\d]|[.]$|^[.]', str_ID_vm):
            reg = regex.compile(r"\d{3}")
            list_ID_vm = reg.findall(str_ID_vm)
            for ID_vm in list_ID_vm:
                self.__exist_VM(ID_vm)

            return list_ID_vm
        else:
            sys.exit(Color.RED + "Syntax invalid : " + str_ID_vm + Color.RESET)

    def used_ID(self, ID_vm: str) -> None:

        self.__check_ID(ID_vm)

        for vmDict in self.__vm_list:
            for value in vmDict.values():
                if value == str(ID_vm):
                    print(Color.ORANGE + 'The ID "' + ID_vm + '" is already used by another VM' + Color.RESET)
                    sys.exit()

    def get_VM_info_check(self, ID_vm: str) -> dict:
        self.__exist_VM(ID_vm)
        return self.__research_VM(ID_vm)

    def get_VM_info_unchecked(self, ID_vm: str) -> dict:
        return self.__research_VM(ID_vm)

    def get_VM_List(self) -> list:
        return self.__vm_list


# ? Function vm -------------------------------------------------------------------------------------->

def get_config_VM(info_vm: dict, option: str = "") -> None:
    dash_30: str = '-' * 30
    print(Color.WHITE + dash_30 + str(' ' + info_vm["vm_ID"] + ':' + info_vm["Name"] + ' ') + dash_30 + Color.CLEAR)
    if info_vm["Tag"] == "LXC":
        os.system('pct config ' + info_vm["vm_ID"] + option)

    elif info_vm["Tag"] == "QM":
        os.system('qm config ' + info_vm["vm_ID"] + option)

    print(
        Color.WHITE + dash_30 + '-' * len(' ' + info_vm["vm_ID"] + ':' + info_vm["Name"] + ' ') + dash_30 + Color.RESET)


def start_VM(info_vm: dict) -> None:
    if info_vm["Status"] == "running":
        print(Color.MAGENTA + "VM Already " + Color.GREEN + "started " + Color.MAGENTA + info_vm["Name"] + ':' +
              info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "LXC":
        try:
            print(Color.YELLOW + "Start Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
            subprocess.check_output(['pct start ' + info_vm["vm_ID"]], shell=True)
            print(Color.GREEN + "Started Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)
        except subprocess.CalledProcessError:
            print(Color.RED + "The command was not executed correctly" + Color.RESET)

    elif info_vm["Tag"] == "QM":
        try:
            print(Color.YELLOW + "Start VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
            subprocess.check_output(['qm start ' + info_vm["vm_ID"]], shell=True)
            print(Color.GREEN + "Started VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)
        except subprocess.CalledProcessError:
            print(Color.RED + "The command was not executed correctly" + Color.RESET)


def stop_VM(info_vm: dict) -> None:
    if info_vm["Status"] == "stopped":
        print(Color.MAGENTA + "VM Already " + Color.RED + "stopped " + Color.MAGENTA + info_vm["Name"] + ':' +
              info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "LXC":
        try:
            print(Color.YELLOW + "Stop Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
            subprocess.check_output(['pct stop ' + info_vm["vm_ID"]], shell=True)
            print(Color.GREEN + "Stopped Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)
        except subprocess.CalledProcessError:
            print(Color.RED + "The command was not executed correctly" + Color.RESET)

    elif info_vm["Tag"] == "QM":
        try:
            print(Color.YELLOW + "Stop VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
            subprocess.check_output(['qm stop ' + info_vm["vm_ID"]], shell=True)
            print(Color.GREEN + "Stopped VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)
        except subprocess.CalledProcessError:
            print(Color.RED + "The command was not executed correctly" + Color.RESET)


def reboot_VM(info_vm: dict) -> None:
    if info_vm["Status"] == "stopped":
        print(Color.MAGENTA + "The VM is " + Color.RED + "stopped " + Color.MAGENTA + info_vm["Name"] + ':' +
              info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "LXC":
        try:
            print(Color.YELLOW + "Reboot Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
            subprocess.check_output(['pct reboot ' + info_vm["vm_ID"]], shell=True)
            print(Color.GREEN + "Rebooted Container " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)
        except subprocess.CalledProcessError:
            print(Color.RED + "The command was not executed correctly" + Color.RESET)

    elif info_vm["Tag"] == "QM":
        try:
            print(Color.YELLOW + "Reboot VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.DEFAULT)
            subprocess.check_output(['qm reboot ' + info_vm["vm_ID"]], shell=True)
            print(Color.GREEN + "Rebooted VM " + info_vm["Name"] + ':' + info_vm["vm_ID"] + Color.RESET)
        except subprocess.CalledProcessError:
            print(Color.RED + "The command was not executed correctly" + Color.RESET)


def console_VM(info_vm: dict) -> None:
    if info_vm["Status"] == "stopped":
        print(Color.MAGENTA + "The VM is " + Color.RED + "stopped " + Color.MAGENTA + info_vm["Name"] + ':' +
              info_vm["vm_ID"] + Color.RESET)

    elif info_vm["Tag"] == "LXC":
        print(Color.YELLOW + "exit the console Ctrl+a q" + Color.RESET)
        os.system('pct console ' + info_vm["vm_ID"] + ' -escape ^a')
        clear()

    elif info_vm["Tag"] == "QM":
        print(Color.YELLOW + "use 'qm terminal' and config serial" + Color.RESET)


def destroy_VM(info_vm: dict, option: str = "") -> None:
    if info_vm["Status"] == "running":
        print(
            Color.MAGENTA + "The VM is " + Color.GREEN + "running " + Color.MAGENTA + info_vm["Name"] + ':' +
            info_vm["vm_ID"] + Color.RESET)
        sys.exit()

    choicer_Action = input(
        Color.ORANGE + "Do you really want to remove the VM : " + Color.UNDERLINE + Color.CYAN +
        info_vm["Name"] + Color.DEFAULT + " (" + Color.GREEN + "Y" + Color.DEFAULT + "/" + Color.RED + "[N]" +
        Color.DEFAULT + "): ")
    print()

    if choicer_Action == 'Y' or choicer_Action == 'y':

        input_vmID = input(
            Color.MAGENTA + "Please enter the ID to confirm" + Color.DEFAULT + " (" + info_vm["vm_ID"] + ") : ")

        if input_vmID == info_vm["vm_ID"]:
            print(Color.RESET)
            if info_vm["Tag"] == "LXC":
                os.system('pct destroy ' + info_vm["vm_ID"] + option)

            elif info_vm["Tag"] == "QM":
                os.system('qm destroy ' + info_vm["vm_ID"] + option)
        else:
            print(Color.RED + 'Wrong ID : ' + input_vmID + Color.RESET)
            sys.exit()

        print()

    else:
        print()
        sys.exit()


def clone_VM(info_vm: dict, new_vm: str, option: str = "") -> None:
    if info_vm["Status"] == "running":
        print(
            Color.MAGENTA + "The VM is " + Color.GREEN + "running " + Color.MAGENTA + info_vm["Name"] + ':' +
            info_vm["vm_ID"] + Color.RESET)
        sys.exit()

    if info_vm["Tag"] == "LXC":
        print()
        os.system('pct clone ' + str(info_vm["vm_ID"]) + ' ' + new_vm + option)

    elif info_vm["Tag"] == "QM":
        print()
        os.system('qm clone ' + str(info_vm["vm_ID"]) + ' ' + new_vm + option)

    print()
    sys.exit()


# ? Start ----------------------------------------------------------------------------------------->

print()

vm = Main_vm()
command_option: str = ""

if args.Command_Name == 'config':
    vm_info = vm.get_VM_info_check(args.VMID)

    if args.CURRENT: command_option += " -current"
    if args.SNAPSHOT: command_option += " -snapshot " + str(args.SNAPSHOT)

    get_config_VM(vm_info, command_option)
    sys.exit()

if args.Command_Name == 'start':

    list_vmID = vm.regex_vmID(args.VMID_LIST)

    for vmID in list_vmID:
        vm_info = vm.get_VM_info_unchecked(vmID)
        start_VM(vm_info)

    sys.exit()

if args.Command_Name == 'stop':

    list_vmID = vm.regex_vmID(args.VMID_LIST)

    for vmID in list_vmID:
        vm_info = vm.get_VM_info_unchecked(vmID)
        stop_VM(vm_info)

    sys.exit()

if args.Command_Name == 'reboot':

    list_vmID = vm.regex_vmID(args.VMID_LIST)

    for vmID in list_vmID:
        vm_info = vm.get_VM_info_unchecked(vmID)
        reboot_VM(vm_info)

    sys.exit()

if args.Command_Name == 'console':
    vm_info = vm.get_VM_info_check(args.VMID)
    console_VM(vm_info)
    sys.exit()

if args.Command_Name == 'destroy':

    vm_info = vm.get_VM_info_check(args.VMID)
    if args.PURGE: command_option = " -purge "
    destroy_VM(vm_info, command_option)
    sys.exit()

if args.Command_Name == 'clone':

    vm.used_ID(args.newID)
    vm_info = vm.get_VM_info_check(args.VMID)

    if args.BWLIMIT: command_option += " -bwlimit " + str(args.BWLIMIT)
    if args.DESCRIPTION: command_option += " -description " + str(args.DESCRIPTION)
    if args.FULL: command_option += " -full"
    if args.POOL: command_option += " -pool " + str(args.POOL)
    if args.SNAPNAME: command_option += " -snapname " + str(args.SNAPNAME)
    if args.STORAGE: command_option += " -storage " + str(args.STORAGE)
    if args.TARGET: command_option += " -target " + str(args.TARGET)
    if args.NAME:  # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        if vm_info["Tag"] == "LXC":
            command_option += " -hostname " + args.NAME
        elif vm_info["Tag"] == "QM":
            command_option += " -name " + args.NAME
    if args.FORMAT:  # ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
        if vm_info["Tag"] == "QM":
            command_option += " -format " + args.FORMAT
        else:
            print(Color.ORANGE + 'The "-format" option is only available for VM (QEMU)' + Color.RESET)
            sys.exit()

    clone_VM(vm_info, str(args.newID), command_option)
    sys.exit()

if args.Command_Name == 'list':

    key_sort: str = 'vm_ID'

    if args.sort:
        if args.sort == "type":
            key_sort = 'Tag'
        elif args.sort == "status":
            key_sort = 'Status'
        elif args.sort == "name":
            key_sort = 'Name'

    vm_list_sort: list = sorted(vm.get_VM_List(), key=itemgetter(key_sort), reverse=args.REVERSE)

    form_header = "{0:6}{1:10}{2:6}{3:10}"
    form_Stop = "{0:6}" + Color.RED + "{1:10}" + Color.DEFAULT + "{2:6}{3:10}"
    form_Start = "{0:6}" + Color.GREEN + "{1:10}" + Color.DEFAULT + "{2:6}{3:10}"
    dash_40 = '-' * 40
    title = ['VMID', 'Status', 'Type', 'Name']

    print(dash_40)
    print(form_header.format(*title))
    print(dash_40)

    for vm_dict in vm_list_sort:

        vm_print = list(vm_dict.values())

        if vm_print[1] == 'stopped':
            print(form_Stop.format(*vm_print))
        elif vm_print[1] == 'running':
            print(form_Start.format(*vm_print))

    print(Color.RESET)

    sys.exit()

sys.exit()
