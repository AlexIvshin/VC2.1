# -*- coding: utf-8 -*-

import os
import random
import sys
from subprocess import run

import dialog as dg
import skills
import support_skills as ss

from model_voice import Voice
talk = Voice().speaks

homedir = os.getcwdb().decode(encoding='utf-8')
scriptdir: str = f'{homedir}/scripts/'

last_function = last_cmdline = ''
global cmdline, function, on_off


def yesno_action(yesno: str) -> None:
    global last_function, last_cmdline

    if yesno == 'yes' and last_function and last_cmdline:
        globals()[last_function]()
    elif yesno == 'no':
        last_function = last_cmdline = ''


def confirm_action(foo_name: str) -> None:
    global last_cmdline, last_function
    last_function, last_cmdline = foo_name, cmdline
    return talk(f'Вы уверены?')


def call_reboot_down(action: str) -> None:
    def execute_command(cmd):
        ss.answer_ok_and_pass()
        run(cmd, shell=True)
        sys.exit()

    if last_function == action == 'sys_down':
        return execute_command('systemctl poweroff')
    elif last_function == action == 'sys_reboot':
        return execute_command('systemctl reboot')
    return confirm_action(action)


def callfunc(command_line: str, action: str, onoff=None) -> None:
    global function, cmdline, on_off
    function, cmdline, on_off = action, command_line, onoff
    return start_script(function) if 'start_script' in function else globals()[function]()


def hello() -> None:
    return talk(random.choice(dg.hello_answer))


def thanks_output() -> None:
    return talk(random.choice(dg.answer_thanks))


def i_am_output() -> None:
    sequence = ss.check_word_sequence(cmdline, ss.get_intersection_word(function, cmdline, dg.actions_dict))
    if len(cmdline.split(' ')) < 4 and sequence:
        return talk(f'{random.choice(dg.i_answer)} {random.choice(dg.i_answer_other)}')


# Пускаем весь интернет-трафик через Tor + toriptables2
def mode_anonim() -> None:
    return skills.Anonimizer(on_off).start_stop_anonimizer()


def start_script(foo_str: str) -> None:
    return skills.ScriptStarter(foo_str).run_script()


def search() -> None:
    return skills.SearchEngine(cmdline, function).get_result()


def calculate() -> None:
    return skills.Calculator(cmdline).tell_the_result()


def weather() -> None:
    return skills.Sinoptik(cmdline).get_weather_forecast()


def stop_app() -> None:
    talk(random.choice(dg.answer_goodby))
    return sys.exit()


def app_reboot() -> None:
    return ss.restart_app()


def sys_down() -> None:
    return call_reboot_down('sys_down')


def sys_reboot() -> None:
    return call_reboot_down('sys_reboot')


def conf_settings() -> None:
    return skills.AssistantSettings(cmdline).change_conf_set()


def volume_settings() -> None:
    return skills.AssistantSettings(cmdline).change_volume()


def random_joke() -> None:
    global last_cmdline, last_function
    last_function = 'random_joke'
    last_cmdline = cmdline
    return skills.Polyhistor(cmdline).get_result()


def show_sys_info() -> None:
    from widgets.sysinfo_widget import show_sysinfo
    ss.answer_ok_and_pass()
    return show_sysinfo()


def exchange_rates() -> None:
    return skills.ExchangeRates(cmdline).get_exchange_rates()
