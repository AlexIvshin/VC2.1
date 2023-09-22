# -*- coding: utf-8 -*-

from subprocess import check_output, call
import sys
import random

import dialog as dg

from model_voice import Voice
talk = Voice().speaks

# Режимы и команды смены режима, используются в choice_mode()
notebook_mode = 'notebook'
notebook_cmd = 'режим блокнота'
default_mode = 'default'
default_cmd = 'обычный режим'
sleep_mode = 'sleep'
sleep_cmd = 'первая спи'
translator_mode = 'translator'
translator_cmd = 'режим перевода'
reverse_mode = 'translator-reverse'
reverse_cmd = 'реверс'
wakeup_cmd = 'первая проснись'


def get_displaysize() -> tuple[int, int]:
    size = check_output(
        f'''xrandr|grep 'Screen 0:'|awk -F ',' '{{print $2}}'|awk '{{print $2, $4}}' ''',
        encoding='utf-8',
        shell=True)
    displaysize_x, displaysize_y = int(size.split()[0]), int(size.split()[1])
    return displaysize_x, displaysize_y


def xterm_x_position(geom_w: int) -> int:
    return int((get_displaysize()[0] - geom_w * 10) / 2)


def choice_xterm(category: str) -> str:
    import configparser
    import pathlib

    config = configparser.ConfigParser()
    config.read(pathlib.Path(__file__).parent.absolute() / "settings.ini")

    category_list = ['Xterm', 'XtermSmall', 'XtermSearch']
    ctgr = 'Xterm' if category not in category_list else category
    title = ctgr

    x, y = int(config[ctgr]['x']), int(config[ctgr]['y'])
    fg, bg, fsize = config[ctgr]['fg'], config[ctgr]['bg'], int(config[ctgr]['fontsize'])
    fname = config[ctgr]['font']

    if ctgr == 'XtermSearch':
        pos_x, pos_y, hold = xterm_x_position(x), 380, '-hold'
    else:
        pos_x, pos_y, hold = 10, 20, ''

    return f'xterm -T {title} -fg {fg} -bg {bg} -geometry {x}x{y}+{pos_x}+{pos_y} -fa {fname} -fs {fsize} {hold} -e'


def restart_app() -> None:
    talk('Перезагружаюсь!')  # Ключевая фраза, которая ловится в start_app.py
    sys.exit()


def check_yesno_onoff(command: str, dictionary: dict) -> str:
    return ''.join([key for key, value in dictionary.items() if set(value) & set(command.split())])


def check_hand_input(words: str) -> bool:
    input_words = ['ручной', 'клавиатура', 'клавиатуры', 'ввод', 'вот', 'ручную']
    if len(set(words.split()) & set(input_words)) > 1:
        talk('Жду ввода с клавиатуры!')
        return True


def choice_action(command: str, d: dict) -> str | None:
    action = None
    for key in d.keys():
        # Проверка минимально допустимого кол-во вхождений(пересечений) для выбора реакции.
        if len(set(command.split()) & set(d[key][1:])) >= d[key][0]:
            action = key
    return action


def check_prg(command: str):  # Определяем програму и её наличие в системе
    prg = ''.join([key for key, value in dg.programs_dict.items() if set(value) & set(command.split(' '))])

    if prg and call(f'which {prg} >/dev/null', shell=True) != 0:
        print(f'Program: "{prg}"')
        return talk('Эта програма в системе не обнаружена!', print_str=f'Program: "{prg}"')
    return prg


def check_word_sequence(command: str, words: list) -> bool:  # Проверяем идут ли слова вхождения одно за другим
    indexes_words: list = []
    [indexes_words.append(command.split().index(i)) for i in words]  # список индексов слов вхождения
    indexes_words.sort()  # сортируем список
    return all(a - b == 1 for a, b in zip(indexes_words[1:], indexes_words))


def answer_ok_and_pass(answer=True, enter_pass=False) -> None:
    if answer:
        talk(random.choice(dg.answer_ok))
    if enter_pass:
        talk(random.choice(dg.enter_pass_answer))


def get_intersection_word(act: str, cmd: str, d: dict) -> list:
    isection_words = []
    [isection_words.append(word) if word == i and word not in isection_words
     else None for i in cmd.split() for word in d[act]]
    return isection_words


def get_meat(act: str, cmd: str, d: dict) -> str:  # Возвращает остаток строки после последнего вхождения
    split_cmd = cmd.split()
    isection_words = get_intersection_word(act, cmd, d)
    return ' '.join(split_cmd[split_cmd.index(isection_words[-1]) + 1:]) if isection_words else None


def check_internet() -> bool:  # internet check feature
    import socket

    host = '8.8.8.8'
    port = 53
    timeout = 3

    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as e:
        print(e)
        talk('Упс! Интернет отсутствует!')
        return False


def choice_mode(change_mode_cmd: str, var_mode) -> str:
    mode = var_mode

    def say_mode():
        if change_mode_cmd == notebook_cmd:
            talk('Режим блокнота активирован!')
        if change_mode_cmd == translator_cmd:
            talk('Переводчик активирован!')
        if change_mode_cmd == sleep_cmd:
            talk('Засыпаю...')
        if change_mode_cmd == default_cmd:
            talk('Обычный режим активирован!')
        if change_mode_cmd == wakeup_cmd:
            talk('Я снова в деле!')

    if (mode != sleep_mode and change_mode_cmd == notebook_cmd
            or mode == notebook_mode and change_mode_cmd != default_cmd):
        mode = notebook_mode

    if (mode != sleep_mode and change_mode_cmd == translator_cmd
            or mode == translator_mode and change_mode_cmd != default_cmd
            or mode == reverse_mode and change_mode_cmd != default_cmd
            or change_mode_cmd == reverse_cmd):
        if change_mode_cmd == translator_cmd:
            mode = translator_mode
        if change_mode_cmd == reverse_cmd:
            mode = reverse_mode if mode == translator_mode else translator_mode

    if change_mode_cmd == sleep_cmd or mode == sleep_mode:
        mode = sleep_mode

    if change_mode_cmd == default_cmd and mode != sleep_mode or change_mode_cmd == wakeup_cmd:
        mode = default_mode

    say_mode()
    return mode
