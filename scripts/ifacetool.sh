#!/usr/bin/env bash
# shellcheck disable=SC2001

noco=$(tput sgr0)
red=$(tput setaf 160)
grey=$(tput setaf 242)
darkgrey=$(tput setaf 235)
sky=$(tput setaf 33)
bir=$(tput setaf 24)
birb=$(tput bold setaf 24)
green=$(tput setaf 2)
indigo=$(tput setaf 92)
bordo=$(tput setaf 88)
bordob=$(tput bold setaf 88)
blue=$(tput setaf 21)
blueb=$(tput bold setaf 21)
indigo=$(tput setaf 90)
yellow=$(tput setaf 226)
violet=$(tput setaf 54)

# Global value
symb="${grey}<${noco}"
symbs="${grey}>>> ${noco}"
symb_ok="${green}[+] ${noco}"
symb_no="${red}[-] ${noco}"
choice_option_line="${sky} Выбери опцию:${noco}"
choice_iface_line="${bordob}    Выбери другой или введи <${noco} q ${bordob}>, чтобы выйти!${noco}"
bad_choice="${red} Не корректный выбор!${noco}"


# check root
ROOT_UID=0
E_NOTROOT=67

if [ "$UID" != "$ROOT_UID" ]
    then echo -e "${red} Нет прав на исполнение! Только root! ${noco}"
         exit $E_NOTROOT
fi
clear

Choice_exit() {

    while read -r var_exit; do
        echo
        case ${var_exit} in

            [yY][eE][sS]|[yY])
                clear
                return 0
                break; ;;

            [nN][oO]|[nN])
                #return 1
                ${function_name}
                break; ;;

            *) echo -en "${red} Enter (Y/N)! ${symbs} ${noco}"; ;;
        esac
    done
}
trap 'echo -en "${red}\n Выйти? (Y/N) ${symbs} ${noco}"; Choice_exit && exit 1' SIGINT

Line_gen() {

    lengthstr="$(echo "${3}" | awk '{print length}')"
    lengthsymb=$(( ( ${1} - lengthstr ) / 2  ))
    color=${4}
    color_2=${5}
    symbol=${color}${2}${noco}

    if [ "$color_2" == "" ]; then
        head_str="$color""${3}""$noco"
    else head_str="$color_2""${3}""$noco"
    fi

    Symb_line() { c=0; while [ $c -le "$lengthsymb" ]; do echo -en "${2}"; c=$(( c + 1 )); done }

    Symb_line "$lengthsymb" "$symbol"
    echo -en "$head_str"

    if [ "$(( lengthstr % 2 ))" != "0" ]; then lengthsymb=$(( lengthsymb + 1 )); fi
    Symb_line "$lengthsymb" "$symbol"
    echo -e "$noco"
}

Check_env() {

    case ${env} in
        "iface_tools") Line_gen 48 "~" " IFACE TOOLS " "${bordob}"; ;;
             "ifaces") Line_gen 48 "~" " INTERFACES " "${bordob}"; ;;
       "rename_iface") Line_gen 48 "~" " RENAME " "${bordob}"; ;;
    esac
}

Check_iface_name() {

    if ! iw dev | grep Interface | awk '{print $2}' >/dev/null; then
        echo -e "${symb_no}${red} Интерфейс не найден!${noco}"; exit
    fi
    clear
    function_name="main"
    env="ifaces"
    Check_env

    case $1 in
               "error_mode") echo -e "${symb_no}${red}${iface} не поддерживает режим мониторинга!!!${noco}"
                             echo -e "${choice_iface_line}"
                             Line_gen 48 "-" "" "${red}"; ;;

           "no_such_device") echo -e "${symb_no}${red}Выбраный интерфейс не найден!!!${noco}"
                             echo -e "${choice_iface_line}"
                             Line_gen 48 "-" "" "${red}"; ;;

  "Operation not supported") echo -e "${symb_no}${red}Смена MAC адреса невозможна!"
                             echo -e "    ${iface} ${red}не поддерживает эту функцию.${noco}"
                             echo -e "${choice_iface_line}"
                             Line_gen 48 "-" "" "${red}"; ;;
    esac

    echo
    echo -e "${bir} Обнаружены беспроводные интерфейсы:${noco}"
    Line_gen 48 "~" "" "${grey}"
    count=1

    iw dev | grep Interface | awk '{print $2}' |
    while read -r line; do
        echo -e "${sky} ${count}${noco} ${symb} ${blueb}${line}${noco}"
        count=$(( count + 1 ))
    done

    Line_gen 48 "~" "" "${grey}"

    while echo -e "${sky} Выбери интерфейс или введи <${noco} q ${sky}>, чтобы выйти!${noco}"
          echo -en " ${symbs} "; read -r num_str; do

        if [ "${num_str}" == "q" ]
            then clear; NM_start; exit
        elif [ "$(iw dev | grep Interface | awk 'NR == '"${num_str}"'{print$2}' 2> /dev/null)" == "" ]
            then echo -e "${bad_choice}${red} Или интерфейс отсутствует.${noco}"
        else iface="$(iw dev | grep Interface | awk 'NR == '"${num_str}"'{print$2}')"
             break
        fi
    done

    clear
    Check_env
    echo
    echo -e "${bir} Выбран интерфейс - ${noco}""${blue}${iface}${noco}"
    Line_gen 48 "-" "" "${grey}"

    sleep 1s
}

Check_iface_on() { if ! iwconfig "${iface}" >/dev/null 2>&1; then Check_iface_name "no_such_device"; fi; }

Check_Iface_tool() {

    ip link set "${iface}" down
    if ! macchanger -r "${iface}" > /dev/null 2>&1; then 
        ip link set "${iface}" up
        Check_iface_name "Operation not supported"
    else ip link set "${iface}" down
        macchanger -p "${iface}" > /dev/null 2>&1
        ip link set "${iface}" up
    fi
}

Iface_info() {

    Check_iface_on
    current_mac="$(macchanger -s "${iface}" | grep "Current MAC" | awk '{print $3}')"
    permanent_mac="$(macchanger -s "${iface}" | grep "Permanent MAC" | awk '{print $3}')"
    iface_mode="$(iw "${iface}" info | grep "type" | awk '{print $2}')"
    iface_ch="$(iw "${iface}" info | grep "channel" | awk '{print $2,$3,$4}' | sed 's/,//')"


    if ip -o link show | grep "$iface" | grep -o 'MULTICAST,UP' >/dev/null 2>&1; then
        echo -e "${bir}                   State: ${green}UP${noco}"
    else echo -e "${bir}                   State: ${bordo}DOWN${noco}"
    fi

    Line_gen 48 "-" " interface info " "${grey}"
    echo -e "${symb_ok}${bir} ${iface}..................: Mode: ${yellow}${iface_mode}${noco}"

    if [ "${iface_mode}" == "monitor" ]; then echo -e "${symb_ok}${bir} Current channel........: ${yellow}${iface_ch}${noco}"; fi

    if [ "${current_mac}" == "${permanent_mac}" ]; then
        echo -e "${symb_ok}${bir} Current & Permanent MAC: ${current_mac}${noco}"
    else echo -e "${symb_ok}${indigo} Current MAC............: ${current_mac}${noco}"
         echo -e "${symb_ok}${bir} Permanent MAC..........: ${permanent_mac}${noco}"
    fi

    Line_gen 48 "~" "" "${grey}"
}

Mode_monitor() {

    Check_iface_on
    if ! iw "${iface}" info | grep -o "monitor" >/dev/null; then
        ip link set "${iface}" down
        iw "${iface}" set monitor control 2> /dev/null
        if iw "${iface}" info | grep -o "managed" >/dev/null; then
            ip link set "${iface}" up
            Check_iface_name "error_mode"
        else ip link set "${iface}" up
        fi
    fi
}

Mode_managed() {

    Check_iface_on
    ip link set "${iface}" down
    iw "${iface}" set type managed 2> /dev/null
    ip link set "${iface}" up
}

Rename_iface() {

    clear
    env="rename_iface"
    Check_env
    echo -e "${grey}* Для корректной работы, имя должно начинаться с \"w\""
    echo -en "${sky} Введите имя интерфейса: ${symbs} "; read -r iface_name
    ip link set "${iface}" down
    ip link set "${iface}" name "${iface_name}"
    ip link set "${iface_name}" up
    iface=${iface_name}
    clear
    Check_env
    echo
    echo -e "${grey} Интерфейсу присвоено имя - ${birb}${iface}"
}

NM_start() { if systemctl status NetworkManager | grep -o "dead" >/dev/null; then service NetworkManager start; fi }

Iface_tool() {

    Check_iface_on
    clear
    env="iface_tools"
    Check_env
    Iface_info
    echo -e "${sky} 0 ${noco}${symb}${sky} EXIT"
    Line_gen 48 "-" " macchanger " "${darkgrey}"
    echo -e "${sky} 1 ${noco}${symb}${indigo} Random change MAC "
    echo -e "${sky} 2 ${noco}${symb}${indigo} Change MAC"
    echo -e "${sky} 3 ${noco}${symb}${indigo} Permanent MAC"
    Line_gen 48 "-" " change mode " "${darkgrey}"
    echo -e "${sky} 4 ${noco}${symb}${yellow} Monitor mode"
    echo -e "${sky} 5 ${noco}${symb}${yellow} Manage mode"
    Line_gen 48 "-" " rename " "${darkgrey}"
    echo -e "${sky} 6 ${noco}${symb}${violet} Change name"
    Line_gen 48 "-" " ON/OFF " "${darkgrey}"

    if ip -o link show | grep "$iface" | grep -o 'MULTICAST,UP' >/dev/null 2>&1
        then echo -e "${sky} 7 ${noco}${symb}${bordo} OFF${noco}"
        else echo -e "${sky} 7 ${noco}${symb}${green} ON${noco}"
    fi
    Line_gen 48 "~" "" "${grey}"

    Format_error() {

        Line_gen 48 "-" "" "${bordo}"
        echo -e "${red} Не корректный ввод! "
        echo -e "${bir} Корректный формат - XX:XX:XX:XX:XX:XX ${noco}"; echo -en " ${symbs} "
    }

    while echo -en "${choice_option_line} ${symbs} "; read -r num; do
        case ${num} in

            0) clear
               exit; ;;

            1) Line_gen 48 "*" "  waiting  " "${grey}"
               Check_Iface_tool
               ip link set "${iface}" down
               macchanger -r "${iface}" 2>&1 > /dev/null | grep -q "Operation not supported"
               ip link set "${iface}" up
               Iface_tool; ;;

            2) Check_Iface_tool
               echo -e "${bir} Введи возможный желаемый MAC XX:XX:XX:XX:XX:XX ${noco}"; echo -en " ${symbs} "
               
               while read -r m; do
                   mac="$(echo "${m}" | sed 's/.*/\L&/')"
                   if [ "${mac:2:1}${mac:5:1}${mac:8:1}${mac:11:1}${mac:14:1}" != ":::::" ]
                       then Format_error
                   elif [ "$(echo "${mac}" | awk '{print length}')" != "17" ]
                       then Format_error
                   else Line_gen 48 "*" "  waiting  " "${grey}"
                        ip link set "${iface}" down
                        ip link set dev "${iface}" address "${mac}"
                        ip link set "${iface}" up
                        Iface_tool
                        break
                   fi
               done; ;;

            3) Line_gen 48 "*" "  waiting  " "${grey}"
               ip link set "${iface}" down
               macchanger -p "${iface}" > /dev/null
               ip link set "${iface}" up
               Iface_tool; ;;

            4) Mode_monitor
               Iface_tool; ;;

            5) Mode_managed
               Iface_tool; ;;

            6) Rename_iface
               Iface_tool; ;;

            7) if ip -o link show | grep "$iface" | grep -o 'MULTICAST,UP' >/dev/null 2>&1
                   then ip link set "${iface}" down
               else ip link set "${iface}" up
               fi
               Iface_tool; ;;

            *) echo -e "${bad_choice}"; ;;
        esac
    done
}

Check_iface_name
Iface_tool
