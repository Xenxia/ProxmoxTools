#!/bin/bash

declare -A LIST_SOFTWARE
declare -n latest

#color

RESET="\u001b[0m"
DIM="\e[2m"

RED="\u001b[38;5;160m"
GREEN="\u001b[38;5;82m"
YELLOW="\u001b[38;5;226m"
ORANGE="\e[38;5;208m"
BLUE="\e[38;5;4m"

# /!\ don't modify below /!\

INSTALL_PATH="/usr/local/bin/"
TEMP_PATH="/tmp/"
URL_DOWNLOAD="https://github.com/Xenxia/ProxmoxTools/releases/download/Download/"

LIST_SOFTWARE=( [1 NAME]="vm_cli" [1 COMMAND]="vm" [1 INSTALL]="false" [1 UPDATE]="None" [1 CURRENT]="None" [1 LATEST]="None"
)

###############################################################################
# FONCTION

install_Soft() {
  wget "$1-$2" -O "$3"
  chmod 755 $3
}

###############################################################################
# SCRIPT

DATE=$(date +%D)
if [ -e ${TEMP_PATH}date.pts ]; then
  source "${TEMP_PATH}date.pts"
  if [ $DATE_UPDATE_PTS != $DATE ]; then
    echo "DL_VERSION"
    wget -q "${URL_DOWNLOAD}version" -O "${TEMP_PATH}version.pts"
  fi
else
  echo "DL_VERSION"
  echo "DATE_UPDATE_PTS=$DATE" >> ${TEMP_PATH}date.pts
  wget -q "${URL_DOWNLOAD}version" -O "${TEMP_PATH}version.pts"
fi

source "${TEMP_PATH}version"
line=$(wc -l ${TEMP_PATH}version | awk -F ' ' '{print $1}')

Navig=Setup

while :
do
  case "$Navig" in

    Setup)
      for i in `seq 1 ${line}`; do

        latest=${LIST_SOFTWARE[$i NAME]}
        LIST_SOFTWARE[$i LATEST]=${latest}

      done
      Navig=Check
    ;;

    Check)
      for i in `seq 1 ${line}`; do
        if [ -e ${INSTALL_PATH}${LIST_SOFTWARE[$i COMMAND]} ]; then

          LIST_SOFTWARE[$i INSTALL]="true"

          current=$(${INSTALL_PATH}${LIST_SOFTWARE[$i COMMAND]} --version)
          LIST_SOFTWARE[$i CURRENT]=$current        

          if [ ${current} = ${LIST_SOFTWARE[$i LATEST]} ]; then
            LIST_SOFTWARE[$i UPDATE]="false"
          else
            LIST_SOFTWARE[$i UPDATE]="true"
          fi
        else
          LIST_SOFTWARE[$i INSTALL]="false"
          LIST_SOFTWARE[$i UPDATE]="None"
          LIST_SOFTWARE[$i CURRENT]="None"
        fi
      done
      Navig=Main_Menu
    ;;

    Main_Menu)
      clear
      echo -e "\n"
      # echo ${LIST_SOFTWARE[1 NAME]}
      # echo ${LIST_SOFTWARE[1 COMMAND]}
      # echo ${LIST_SOFTWARE[1 INSTALL]}
      # echo ${LIST_SOFTWARE[1 UPDATE]}
      # echo ${LIST_SOFTWARE[1 CURRENT]}
      # echo ${LIST_SOFTWARE[1 LATEST]}

      for i in `seq 1 $line`; do

        if [ ${LIST_SOFTWARE[$i INSTALL]} = "true" ]; then

          if [ ${LIST_SOFTWARE[$i UPDATE]} = "false" ]; then
            echo -e "${GREEN}●${RESET} $i : ${LIST_SOFTWARE[$i NAME]} - v${LIST_SOFTWARE[$i CURRENT]}"
          else
            echo -e "${YELLOW}●${RESET} $i : ${LIST_SOFTWARE[$i NAME]} - Current v${LIST_SOFTWARE[$i CURRENT]} -> Latest v${LIST_SOFTWARE[$i LATEST]}"
          fi
        else
          echo -e "${RED}●${RESET} $i : ${LIST_SOFTWARE[$i NAME]} - Not installed"
        fi

      done
      echo -e "${BLUE}●${RESET} 0 : exit\n"
      read -p "Choix : " num_soft

      case $num_soft in
        0) Navig=Exit ;;
        [1-$line]) Navig=Menu_Software ;;
        *) Navig=Main_Menu ;;
      esac
    ;;

    Menu_Software)
      clear

      soft_NAME=${LIST_SOFTWARE[$num_soft NAME]}
      soft_COMMAND=${LIST_SOFTWARE[$num_soft COMMAND]}
      soft_CURRENT_VERSION=${LIST_SOFTWARE[$num_soft CURRENT]}
      soft_LATEST_VERSION=${LIST_SOFTWARE[$num_soft LATEST]}

      echo "NAME    : $soft_NAME"
      echo "CURRENT : $soft_CURRENT_VERSION"
      echo "LATEST  : $soft_LATEST_VERSION"
      echo "===================="
      if [ ${LIST_SOFTWARE[$num_soft INSTALL]} = "true" ]; then
        echo -e "${DIM}1 : install${RESET}"

        if [ ${LIST_SOFTWARE[$i UPDATE]} = "false" ]; then
          echo -e "${DIM}2 : Update${RESET}"
          echo -e "3 : Uninstall"
        else
          echo -e "2 : Update"
          echo -e "3 : Uninstall"
        fi

      else
        echo -e "1 : install"
        echo -e "${DIM}2 : Update${RESET}"
        echo -e "${DIM}3 : Uninstall${RESET}"
      fi
      echo -e "0 : exit\n"
      read -p "Choice : " choice

      case $choice in
        0) Navig=Exit ;;
        1)
          if [ ${LIST_SOFTWARE[$num_soft INSTALL]} = "false" ]; then
            echo -e "\n${ORANGE}--- INSTALL ---${RESET}"
            install_Soft "${URL_DOWNLOAD}${soft_NAME}" "${soft_LATEST_VERSION}" "${INSTALL_PATH}${soft_COMMAND}"
            sleep 2
            Navig=Check
          fi
        ;;
        2)
          if [ ${LIST_SOFTWARE[$i UPDATE]} = "true" ]; then
            echo -e "\n${ORANGE}--- UPDATE ---${RESET}"
            rm ${INSTALL_PATH}${soft_COMMAND}
            install_Soft "${URL_DOWNLOAD}${soft_NAME}" "${soft_LATEST_VERSION}" "${INSTALL_PATH}${soft_COMMAND}"
            sleep 2
            Navig=Check
          fi
        ;;
        3)
          if [ ${LIST_SOFTWARE[$num_soft INSTALL]} = "true" ]; then
            echo -e "\n${ORANGE}--- UNINSTALL ---${RESET}"
            rm -f ${INSTALL_PATH}${soft_COMMAND}
            sleep 2
            Navig=Check
          fi
        ;;
        *) Navig=Menu_Software ;;
      esac

    ;;

    Exit)
      clear
      echo ""
      exit

    ;;

  esac
done
