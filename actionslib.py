# -*- coding: utf-8 -*-

import os
import random
import sys
from subprocess import run

import dialog as dg
import skills
import support_skills as ss
from assistant import Assistant

talk = Assistant().speaks

homedir = os.getcwdb().decode(encoding='utf-8')
scriptdir: str = f'{homedir}/scripts/'

last_function = ''
last_cmdline = ''
yes_no = ''
global max_intersection_val, cmdline, command_word, function, on_off


def yesno_action(yesno: str) -> None:
    global last_function, last_cmdline, yes_no
    yes_no = yesno

    if yes_no == 'yes' and last_function and last_cmdline:
        globals()[last_function]()
    elif yes_no == 'no':
        last_function = ''
        last_cmdline = ''


def confirm_action(foo_name: str, isection: int) -> None:
    global last_cmdline, last_function
    if max_intersection_val >= isection:
        last_function = foo_name
        last_cmdline = cmdline
        talk(f'Вы уверены?')


def call_reboot_down(action: str) -> None:
    def execute_command(cmd):
        ss.answer_ok_and_pass()
        run(cmd, shell=True)
        sys.exit()

    if last_function == action == 'sys_down':
        return execute_command('systemctl poweroff')
    elif last_function == action == 'sys_reboot':
        return execute_command('systemctl reboot')
    confirm_action(action, 2)


def callfunc(command_line: str, action: str, maxintersect: int, onoff=None) -> None:
    global max_intersection_val, function, cmdline, command_word, on_off
    cmdline = command_line
    command_word = set(command_line.split(' '))
    function = action
    max_intersection_val = maxintersect
    on_off = onoff

    start_script(function) if 'start_script' in function else globals()[function]()


def hello() -> None:
    if 'день' not in cmdline \
            and 'вечер' not in cmdline \
            and 'добрый' not in cmdline:
        talk(random.choice(dg.hello_answer))
    else:
        if max_intersection_val >= 2:
            talk(random.choice(dg.hello_answer))


def thanks_output() -> None:
    talk(random.choice(dg.answer_thanks))


def i_am_output() -> None:
    if max_intersection_val > 1 and len(command_word) < 4:
        intersection_word = ss.get_intersection_word(function, cmdline, dg.actions_dict)

        if ss.check_word_sequence(cmdline, intersection_word):
            talk(f'{random.choice(dg.i_answer)} {random.choice(dg.i_answer_other)}')


# Пускаем весь интернет-трафик через Tor + toriptables2
def mode_anonim() -> None:
    skills.Anonimizer(max_intersection_val, on_off).start_stop_anonimizer()


def start_script(foo_str: str) -> None:
    skills.ScriptStarter(foo_str, max_intersection_val).run_script()


def search() -> None:
    skills.SearchEngine(cmdline, function, max_intersection_val).get_result()


def calculate() -> None:
    skills.Calculator(cmdline).tell_the_result()


def weather() -> None:
    skills.Sinoptik(cmdline, max_intersection_val).get_weather_forecast()


def stop_app() -> None:
    talk(random.choice(dg.answer_goodby))
    sys.exit()


def app_reboot() -> None:
    ss.restart_app()


def sys_down() -> None:
    call_reboot_down('sys_down')


def sys_reboot() -> None:
    call_reboot_down('sys_reboot')


def conf_settings() -> None:
    skills.AssistantSettings(cmdline).change_conf_set()


def volume_settings() -> None:
    skills.AssistantSettings(cmdline).change_volume()


def random_joke() -> None:
    global last_cmdline, last_function
    last_function = 'random_joke'
    last_cmdline = cmdline
    skills.Polyhistor(cmdline, max_intersection_val).get_result()


def show_sys_info() -> None:
    if max_intersection_val < 3:
        return
    ss.answer_ok_and_pass()
    puth = f'{homedir}/skills.py'
    run(f'{ss.choice_xterm("XtermInfo")} python3 {puth} &', shell=True)


def exchange_rates() -> None:
    skills.ExchangeRates(cmdline, max_intersection_val).get_exchange_rates()
