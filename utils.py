import random
import requests
from subprocess import check_output, call
import sys
import os
from bs4 import BeautifulSoup
import re
import dialog as dg
from assistant import Assistant

model = Assistant()
talk = model.speaks

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
    size = check_output(f'''xrandr | grep 'Screen 0:' | awk -F ',' '{{print $2}}' | awk '{{print $2, $4}}' ''',
                        encoding='utf-8', shell=True)
    displaysize_x, displaysize_y = int(size.split()[0]), int(size.split()[1])
    return displaysize_x, displaysize_y


def xterm_x_position(geom_w: int) -> int:
    return int((get_displaysize()[0] - geom_w * 10) / 2)


def choice_xterm(category) -> str:
    import configparser
    import pathlib

    config_path = pathlib.Path(__file__).parent.absolute() / "settings.ini"
    config = configparser.ConfigParser()
    config.read(config_path)
    category_list = ['Xterm', 'XtermSmall', 'XtermInfo', 'XtermSearch']

    if category not in category_list:
        raise AttributeError(
            'Функция принимает только один из зтих аргументов: [Xterm, XtermSmall, XtermInfo, XtermSearch]'
        )

    x = int(config[category]['x'])
    y = int(config[category]['y'])
    fg = config[category]['fg']
    bg = config[category]['bg']
    fontsize = int(config[category]['fontsize'])
    title = category
    pos_x = xterm_x_position(x)
    pos_y = 350
    hold = ''

    if category == 'XtermInfo':
        pos_x = 10
        pos_y = 20

    if category in category_list[2:]:
        hold = '-hold'
    return f'xterm -T {title} -fg {fg} -bg {bg} -geometry {x}x{y}+{pos_x}+{pos_y} -fa fixed -fs {fontsize} {hold} -e'


def restart_app():
    talk('Перезагружаюсь!')  # Ключевая фраза которая ловится в start_app.py
    sys.exit()


def check_yesno_onoff(command, dictionary: dict) -> str:
    return ''.join([key for key, value in dictionary.items() if set(value).intersection(set(command.split(' ')))])


def check_hand_input(words) -> bool:
    input_words = ['ручной', 'клавиатура', 'клавиатуры', 'ввод', 'вот', 'ручную']

    if len(set(words.split(' ')).intersection(set(input_words))) > 1:
        talk('Жду ввода с клавиатуры!')
        return True


def choice_action(command, actions_dict) -> tuple:
    command_word = set(command.split(' '))
    max_intersection: int = 0
    action = None

    for key, value in actions_dict.items():
        len_val = len(set(value).intersection(command_word))  # кол-во вхождений(пересечений)
        if len_val > max_intersection:
            max_intersection = len_val
            action = key

    if action:
        return action, max_intersection
    else:
        return None, None


def check_prg(command) -> str:
    command_word = set(command.split(' '))
    prg = ''.join([key for key, value in dg.programs_dict.items() if set(value).intersection(command_word)])
    if prg and call(f'which {prg} >/dev/null', shell=True) != 0:
        print(f'Program: "{prg}"')
        return talk('Эта програма в системе не обнаружена!', print_str=f'Program: "{prg}"')
    return prg


def check_word_sequence(command, words) -> bool:
    indexes_words: list = []
    [indexes_words.append(command.split(' ').index(i)) for i in words]  # список индексов слов вхождения
    indexes_words.sort()  # сортируем список

    count = 0
    while count < len(indexes_words) - 1:
        if indexes_words[count] - indexes_words[count + 1] != -1:
            return False
        count += 1
    return True


def answer_ok_and_pass(answer=True, enter_pass=False) -> None:
    if answer:
        talk(random.choice(dg.answer_ok))
    if enter_pass:
        talk(random.choice(dg.enter_pass_answer))


def get_intersection_word(action, command, dictionary: dict) -> list:
    intersection_words = []

    for word in command.split(' '):
        for i in dictionary[action]:
            if word == i:
                intersection_words.append(word)
    return intersection_words


def get_meat(action, command, dictionary: dict) -> str:
    command_words = command.split(' ')
    keywords = get_intersection_word(action, command, dictionary)
    keyword = keywords[-1]
    keyindex = command_words.index(keyword)
    meat = ' '.join(command_words[keyindex + 1:])
    return meat


def get_ip() -> str:
    try:
        url = "https://pr-cy.ru/browser-details/"
        r = requests.get(url)

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            ip_addr = soup.find('div', class_="ip-myip").text
            info = soup.find_all('div', class_="group-box__desc")

            my_info = []

            for title in info:
                article_title = title.text.strip()
                str_info = re.sub(r'[^A-zА-яё0123456789.,:;!?-]', ' ', str(article_title))
                my_info.append(str_info)

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
        print('Интернет... OK')
        return True

    except socket.error as e:
        print(e)
        talk('Упс! Интернет отсутствует!')
        return False


def choice_mode(change_mode_cmd, var_mode='default') -> str:
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
