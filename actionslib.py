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
# mic_sins = model.mic_sensitivity

homedir = os.getcwdb().decode(encoding='utf-8')
scriptdir: str = f'{homedir}/scripts/'
xterm_options_b = (f'-fg "#8787ff" -bg "#06090f" -geometry 93x25+340+300 '
                   f'-fn -misc-fixed-medium-r-normal--14-130-75-75-c-70-iso10646-1')
xterm_options_s = (f'-fg "#8787ff" -bg "#06090f" -geometry 77x15+405+300 '
                   f'-fn -misc-fixed-medium-r-normal--14-130-75-75-c-70-iso10646-1')
xterm_options_info = (f'-fg "#6666ff" -bg "#00091a" -geometry 65x47+900+10 '
                      f'-fn -misc-fixed-medium-r-normal--14-130-75-75-c-70-iso10646-1')

XTERM_b = f'xterm {xterm_options_b} -e'  # Большое окно терминала XTERM
XTERM_s = f'xterm {xterm_options_s} -e'  # Маленькое окно терминала XTERM
XTERM_info = f'xterm {xterm_options_info} -hold -e'  # Окно терминала XTERM для вывода информации о системе

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

    try:
        if 'start_script' in function:
            start_script(function)
        else:
            globals()[function]()
    except KeyError:
        pass


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
    anonim = skills.Anonimizer(max_intersection_val, on_off)
    anonim.start_stop_anonimizer()


def start_script(foo_str):
    script = skills.ScriptStarter(foo_str, max_intersection_val)
    script.run_script()


def search():
    search_engine = skills.SearchEngine(cmdline, function, max_intersection_val)
    search_engine.get_result()


def calculate():
    calc = skills.Calculator(cmdline, function)
    calc.tell_the_result()


def weather():
    sinoptik = skills.Sinoptik(cmdline, max_intersection_val)
    sinoptik.get_weather_forecast()


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
    if max_intersection_val >= 2:
        tls.answer_ok_and_pass()
        run(f'systemctl reboot', shell=True)
        sys.exit()


def conf_settings():
    setconfig = skills.AssistantSettings(cmdline)
    setconfig.change_conf_set()


def volume_settings():
    setvolume = skills.AssistantSettings(cmdline)
    setvolume.change_volume()


def random_joke():
    global last_cmdline, last_function
    last_function = 'random_joke'
    last_cmdline = cmdline
    result = skills.Polyhistor(cmdline, max_intersection_val)
    result.get_result()


def show_sys_info():
    if max_intersection_val < 3:
        return
    tls.answer_ok_and_pass()
    puth = f'{homedir}/skills.py'
    run(f'{XTERM_info} python3 {puth} &', shell=True)


def exchange_rates():
    rates = skills.ExchangeRates(cmdline, max_intersection_val)
    rates.get_exchange_rates()
