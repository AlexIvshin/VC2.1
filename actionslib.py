import os
import random
import sys
from subprocess import run

import dialog as dg
import skills
import utils as tls
from assistant import Assistant

model = Assistant()
talk = model.speaks

homedir = os.getcwdb().decode(encoding='utf-8')
scriptdir: str = f'{homedir}/scripts/'

last_function = ''
last_cmdline = ''
yes_no = ''
global max_intersection_val, cmdline, command_word, function, on_off


def yesno_action(yesno):
    global last_function, last_cmdline, yes_no
    yes_no = yesno

    if yes_no == 'yes' and last_function and last_cmdline:
        globals()[last_function]()
    elif yes_no == 'no':
        last_function = ''
        last_cmdline = ''


def callfunc(command_line, action, maxintersect, onoff=None):
    global max_intersection_val, function, cmdline, command_word, on_off
    cmdline = command_line
    command_word = set(command_line.split(' '))
    function = action
    max_intersection_val = maxintersect
    on_off = onoff

    start_script(function) if 'start_script' in function else globals()[function]()


def hello():
    if 'день' not in cmdline \
            and 'вечер' not in cmdline \
            and 'добрый' not in cmdline:
        talk(random.choice(dg.hello_answer))
    else:
        if max_intersection_val >= 2:
            talk(random.choice(dg.hello_answer))


def thanks_output():
    talk(random.choice(dg.answer_thanks))


def i_am_output():
    if max_intersection_val > 1 and len(command_word) <= 3:
        intersection_word = tls.get_intersection_word(function, cmdline, dg.actions_dict)

        if tls.check_word_sequence(cmdline, intersection_word):
            talk(f'{random.choice(dg.i_answer)} {random.choice(dg.i_answer_other)}')


# Пускаем весь интернет-трафик через Tor + toriptables2
def mode_anonim():
    skills.Anonimizer(max_intersection_val, on_off).start_stop_anonimizer()


def start_script(foo_str):
    skills.ScriptStarter(foo_str, max_intersection_val).run_script()


def search():
    skills.SearchEngine(cmdline, function, max_intersection_val).get_result()


def calculate():
    skills.Calculator(cmdline, function).tell_the_result()


def weather():
    skills.Sinoptik(cmdline, max_intersection_val).get_weather_forecast()


def stop_app():
    talk(random.choice(dg.answer_goodby))
    sys.exit()


def app_reboot():
    tls.restart_app()


def sys_down():
    if max_intersection_val >= 2:
        tls.answer_ok_and_pass()
        run(f'systemctl poweroff', shell=True)
        sys.exit()


def sys_reboot():
    global last_cmdline, last_function

    if last_function == 'sys_reboot':
        tls.answer_ok_and_pass()
        run(f'systemctl reboot', shell=True)
        sys.exit()

    if max_intersection_val >= 2:
        talk(f'Вы уверены?')
        last_function = 'sys_reboot'
        last_cmdline = cmdline
        return 


def conf_settings():
    skills.AssistantSettings(cmdline).change_conf_set()


def volume_settings():
    skills.AssistantSettings(cmdline).change_volume()


def random_joke():
    global last_cmdline, last_function
    last_function = 'random_joke'
    last_cmdline = cmdline
    skills.Polyhistor(cmdline, max_intersection_val).get_result()


def show_sys_info():
    if max_intersection_val < 3:
        return
    tls.answer_ok_and_pass()
    puth = f'{homedir}/skills.py'
    run(f'{tls.choice_xterm("XtermInfo")} python3 {puth} &', shell=True)


def exchange_rates():
    skills.ExchangeRates(cmdline, max_intersection_val).get_exchange_rates()
