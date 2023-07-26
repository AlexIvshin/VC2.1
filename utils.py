# -*- coding: utf-8 -*-

import random
import requests
from subprocess import check_output, call
import sys
import os
from bs4 import BeautifulSoup
import re

from typing import Optional

import dialog as dg
from assistant import Assistant

talk = Assistant().speaks

# Режимы
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
        f'''xrandr | grep 'Screen 0:' | awk -F ',' '{{print $2}}' | awk '{{print $2, $4}}' ''',
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

    category_list = ['Xterm', 'XtermSmall', 'XtermInfo', 'XtermSearch']
    ctgr = 'Xterm' if category not in category_list else category
    title = ctgr

    x, y = int(config[ctgr]['x']), int(config[ctgr]['y'])
    fg, bg, fontsize = config[ctgr]['fg'], config[ctgr]['bg'], int(config[ctgr]['fontsize'])

    if ctgr == 'XtermInfo':
        pos_x, pos_y = 10, 20
    else:
        pos_x, pos_y = xterm_x_position(x), 350

    hold = '-hold' if ctgr in category_list[2:] else ''
    return f'xterm -T {title} -fg {fg} -bg {bg} -geometry {x}x{y}+{pos_x}+{pos_y} -fa fixed -fs {fontsize} {hold} -e'


def restart_app() -> None:
    talk('Перезагружаюсь!')  # Ключевая фраза которая ловится в start_app.py
    sys.exit()


def check_yesno_onoff(command: str, dictionary: dict) -> str:
    return ''.join([key for key, value in dictionary.items() if set(value) & set(command.split(' '))])


def check_hand_input(words: str) -> None:
    input_words = ['ручной', 'клавиатура', 'клавиатуры', 'ввод', 'вот', 'ручную']
    talk('Жду ввода с клавиатуры!') if len(set(words.split(' ')) & set(input_words)) > 1 else None


def choice_action(command: str, d: dict) -> tuple:
    max_intersection, action = 0, None

    for key, value in d.items():
        len_val = len(set(value) & set(command.split(' ')))  # кол-во вхождений(пересечений)
        if len_val > max_intersection:
            max_intersection, action = len_val, key

    if action:
        return action, max_intersection
    else:
        return None, None


def check_prg(command: str) -> Optional[None, str]:  # Определяем програму и её наличие в системе
    prg = ''.join([key for key, value in dg.programs_dict.items() if set(value) & set(command.split(' '))])

    if prg and call(f'which {prg} >/dev/null', shell=True) != 0:
        print(f'Program: "{prg}"')
        return talk('Эта програма в системе не обнаружена!', print_str=f'Program: "{prg}"')
    return prg


def check_word_sequence(command: str, words: list) -> bool:  # Проверяем идут ли слова вхождения одно за другим
    indexes_words: list = []
    [indexes_words.append(command.split(' ').index(i)) for i in words]  # список индексов слов вхождения
    indexes_words.sort()  # сортируем список
    return all(a - b == 1 for a, b in zip(indexes_words[1:], indexes_words))


def answer_ok_and_pass(answer=True, enter_pass=False) -> None:
    if answer:
        talk(random.choice(dg.answer_ok))
    if enter_pass:
        talk(random.choice(dg.enter_pass_answer))


def get_intersection_word(act: str, cmd: str, d: dict) -> list:
    isection_words = []
    [isection_words.append(word) if word == i else None for i in cmd.split(' ') for word in d[act]]
    return isection_words


def get_meat(act: str, cmd: str, d: dict) -> str:  # Возвращает остаток строки после последнего вхождения
    split_cmd = cmd.split(' ')
    isection_words = get_intersection_word(act, cmd, d)
    return ' '.join(split_cmd[split_cmd.index(isection_words[-1]) + 1:]) if isection_words else None


def get_ip() -> Optional[str]:
    try:
        url = "https://pr-cy.ru/browser-details/"
        r = requests.get(url)
        if r.status_code != 200:
            return
        soup = BeautifulSoup(r.text, "html.parser")
        ip_addr = soup.find('div', class_="ip-myip").text
        info = soup.find_all('div', class_="group-box__desc")
        my_info = []
        [my_info.append(re.sub(r'[^A-zА-яё0123456789.,:;!?-]', ' ', str(title.text.strip()))) for title in info]

        print(f'     IP: {ip_addr}')
        print(f'Country: {my_info[1]}')
        print(f'    ISP: {my_info[0]}')
        return ip_addr
    except requests.exceptions.ConnectionError:
        pass


def check_internet() -> bool:  # internet check feature
    import socket

    host = '8.8.8.8'
    port = 53
    timeout = 3

    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        print('  Интернет... OK')
        return True

    except socket.error as e:
        print(e)
        talk('Упс! Интернет отсутствует!')
        return False


def choice_mode(change_mode_cmd: str, var_mode='default') -> str:
    mode = var_mode

    if mode != sleep_mode and change_mode_cmd == notebook_cmd \
            or mode == notebook_mode and change_mode_cmd != default_cmd:

        if change_mode_cmd == notebook_cmd:
            talk('Режим блокнота активирован!')
        print('Mode: Notebook', end='')
        mode = notebook_mode

    if mode != sleep_mode and change_mode_cmd == translator_cmd \
            or mode == translator_mode and change_mode_cmd != default_cmd \
            or mode == reverse_mode and change_mode_cmd != default_cmd \
            or change_mode_cmd == reverse_cmd:

        if change_mode_cmd == translator_cmd:
            talk('Переводчик активирован!')
            mode = translator_mode

        if mode == translator_mode and change_mode_cmd == reverse_cmd:
            mode = reverse_mode
        elif mode == reverse_mode and change_mode_cmd == reverse_cmd:
            mode = translator_mode

        if mode == translator_mode:
            print('Mode: Translator', end='')

        if mode == reverse_mode:
            print('Mode: Translitor-reverse', end='')

    if change_mode_cmd == sleep_cmd or mode == sleep_mode:
        if change_mode_cmd == sleep_cmd:
            talk('Засыпаю...')
        os.system('clear')
        print('Mode: Sleep...!', end='')
        mode = sleep_mode

    if change_mode_cmd == default_cmd \
            and mode != sleep_mode \
            or change_mode_cmd == wakeup_cmd:
        talk('Обычный режим активирован!')

        if change_mode_cmd == wakeup_cmd:
            talk('Я снова в деле!')

        print('Mode: Default', end='')
        mode = default_mode

    return mode
