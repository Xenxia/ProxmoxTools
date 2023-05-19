#!/usr/bin/env python3

import os, sys
import requests
import pathlib
import datetime
from io import TextIOWrapper
from subprocess import *
from bullet import *
from bullet import colors
from requests.models import Response
from yaml import Loader, load
from tqdm import tqdm

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

    BOLD = "\033[1m"
    DIM = "\u001b[2m"

# /!\ don't modify below /!\

VERSION: str ="V.2"
FILE_VERSION: str ="version.yml"
INSTALL_PATH: str ="/usr/local/bin/"
TEMP_PATH: str ="/tmp/"
URL_DOWNLOAD: str ="https://github.com/Xenxia/ProxmoxTools/releases/download/Download/"


yaml_content: dict = {}
software: list = []
list_soft: list = []

def clear() -> None: os.system("printf '\033c'")

def refresh() -> None:
    software.clear()
    list_soft.clear()
    setup()

def setup() -> None:
    for keys, values in yaml_content.items():
        if keys == "software":
            for key, value in values.items():
                tmp_dict: dict = {}
                tmp_dict['Name'] = key if key != "" else "None"
                tmp_dict['version'] = value['version']
                tmp_dict['cmd'] = value['cmd']
                tmp_dict['install_path'] = value['install_path']
                tmp_dict['installed'] = False
                tmp_dict['current'] = "None"
                tmp_dict['update'] = False
            
                software.append(tmp_dict)
    
    for dico in software:

        try:
            dico['current'] = check_output([dico['cmd']+" --version"], shell=True, stderr=DEVNULL).decode("utf-8").strip()
        except CalledProcessError:
            dico['current'] = "None"

        if os.path.exists(dico['install_path']+dico['cmd']):
            dico['installed'] = True

            if dico['current'] != "None" and dico['current'] < dico['version']:
                dico['update'] = True
                list_soft.append(Color.ORANGE +"● "+ Color.CLEAR + dico['Name'] + " : " + dico['current'] + " ➤ " + dico['version'])
            else:
                list_soft.append(Color.GREEN +"● "+ Color.CLEAR + dico['Name'] + " : " + dico['current'])
        else:
            list_soft.append(Color.RED +"● "+ Color.CLEAR + dico['Name'])

def download(url: str, dest_path: str = '', chunk_size: int = 1024) -> None:

    if dest_path != '' and not os.path.exists(dest_path):
        os.mkdir(dest_path)

    responce: Response = requests.get(url, stream=True)
    if responce.status_code == 404:
        raise ValueError(f"404 Not found : {url}")
    size: int = int(responce.headers['content-length'])
    filename: str = url.split('/')[-1]

    with open(dest_path+filename, 'wb') as f:
        for data in tqdm(iterable=responce.iter_content(chunk_size=chunk_size), 
                        total=(size/chunk_size)+1, 
                        unit='KB', 
                        colour='#00ff00', 
                        dynamic_ncols=True):
            f.write(data)

# Fonction install, update, uninstall

def install_soft(softDict: dict, message: str = 'Install') -> None:

    nameVersion = softDict['Name']+'-'+softDict['version']

    print('Download : ' + nameVersion + '\n')
    download(URL_DOWNLOAD+nameVersion,
            dest_path=softDict['install_path'])
    print('\n' + message + ' : ' + nameVersion + '\n')
    os.rename(softDict['install_path']+nameVersion, softDict['install_path']+softDict['cmd'])
    os.chmod(softDict['install_path']+softDict['cmd'], 755)

def update_soft(softDict: dict) -> None:

    os.remove(softDict['install_path']+softDict['cmd'])
    install_soft(softDict, message='Update')

def uninstall_soft(softDict: dict) -> None:

    nameVersion = softDict['Name']+'-'+softDict['version']
    print('Uninstall : ' + nameVersion + '\n')
    os.remove(softDict['install_path']+softDict['cmd'])

# AutoUpdate

def autoUpdate() -> None:
    if yaml_content['version'] != VERSION:
        clear()
        print(Color.ORANGE + "\n!!! An update is now available !!!" + Color.RESET + Color.CYAN + "\nLink : " + URL_DOWNLOAD + "setup-update" + Color.RESET)
        sys.exit()

# MENU 

def mainMenu(skip: bool = False) -> None:

    clear()

    if skip == False:
        setup()

    list_soft.append('✕ Exit')

    mainMenuB = Bullet(
            prompt = Color.ORANGE + "-={ ProxmoxTools }=-" + Color.RESET,
            choices = list_soft, 
            bullet = ">>",
            bullet_color=Color.CYAN,
            word_color=Color.WHITE,
            word_on_switch=Color.CYAN,
            background_color=colors.background["black"],
            background_on_switch=colors.background["black"],
            margin = 2, 
            return_index = True)

    result_mainMenu: list = mainMenuB.launch()

    if result_mainMenu[0] == '✕ Exit':
        clear()
        sys.exit()
    elif result_mainMenu[0] == '':
        mainMenu(skip=True)

    subMenu(result_mainMenu[1])

def subMenu(index: int) -> None:
    clear()
    dict_subMenu = software[index]
    
    listChoice: list[str] = ['Install', 'Update', 'Uninstall', '↩ Return', '✕ Exit']

    if dict_subMenu['installed'] == True:
        listChoice[0] = Color.DIM+listChoice[0]+Color.CLEAR
        if dict_subMenu['update'] == False:
            listChoice[1] = Color.DIM+listChoice[1]+Color.CLEAR
    else:
        listChoice[1] = Color.DIM+listChoice[1]+Color.CLEAR
        listChoice[2] = Color.DIM+listChoice[2]+Color.CLEAR


    subMenuB = Bullet(
            prompt = Color.CYAN + "-={ "+dict_subMenu['Name'] + ' : '+dict_subMenu['version'] + " }=-" + Color.RESET,
            choices = listChoice, 
            bullet = ">>",
            bullet_color=Color.CYAN,
            word_color=Color.WHITE,
            word_on_switch=Color.CYAN,
            background_color=colors.background["black"],
            background_on_switch=colors.background["black"],
            margin = 2, 
            return_index = True)

    result_subMenu = subMenuB.launch()

    if result_subMenu[0] == 'Install' and dict_subMenu['installed'] == False:
        clear()
        install_soft(dict_subMenu)
        sys.exit()
        
    elif result_subMenu[0] == 'Update' and dict_subMenu['update'] == True:
        clear()
        update_soft(dict_subMenu)
        sys.exit()

    elif result_subMenu[0] == 'Uninstall' and dict_subMenu['installed'] == True:
        clear()
        uninstall_soft(dict_subMenu)
        sys.exit()

    elif result_subMenu[0] == '↩ Return':
        refresh()
        mainMenu(skip=True)

    elif result_subMenu[0] == '✕ Exit':
        clear()
        sys.exit()
    else:
        subMenu(index)
        

if __name__ == '__main__':

    if os.path.exists(TEMP_PATH+FILE_VERSION):
        version_ctime = datetime.datetime.fromtimestamp(pathlib.Path(TEMP_PATH+FILE_VERSION).stat().st_ctime).date()
        date = datetime.datetime.now().date()

        if version_ctime != date:
            os.remove(TEMP_PATH+FILE_VERSION)
            download(URL_DOWNLOAD+FILE_VERSION, dest_path=TEMP_PATH)
    else:
        download(URL_DOWNLOAD+FILE_VERSION, dest_path=TEMP_PATH)

    if not os.path.exists(TEMP_PATH+FILE_VERSION):
        print('ERORR : version.yml not exist')
        sys.exit()
    
    yaml_file: TextIOWrapper = open(TEMP_PATH+FILE_VERSION, 'r')
    yaml_content = load(yaml_file, Loader=Loader)
    
    autoUpdate()
    mainMenu()
