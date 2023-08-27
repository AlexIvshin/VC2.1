# -*- coding: utf-8 -*-

import os
from typing import Union

# Модули приложения
from dialog import notebook_action_dict, yes_no_dict
from assistant import stack
from model_voice import Voice
from skills import File

from wordstonum import word2num_ru as w2n
import support_skills as ss

file_action = File()
talk = Voice().speaks

homedir = file_action.homedir
note_dir = file_action.note_dir

cmdline: str = ''
file: str = ''
action: str = ''


def files_list() -> bool:
    files = os.listdir(note_dir)
    print(f' {note_dir}')

    if not files:
        talk('Файлы не обнаружены.')
        return False

    print('#   Name')
    [print(f'{position} < {f}') for position, f in enumerate(files, 1)]
    print()
    return True


def notebook_reacts(commandline: str) -> None:
    global action, file, cmdline

    cmdline = commandline
    yes_no = ss.check_yesno_onoff(cmdline, dictionary=yes_no_dict)
    num_file = w2n(cmdline)
    action = ss.choice_action(cmdline, notebook_action_dict)
    mem_stack: list = stack.get_stack()

    if yes_no == 'cancel':
        file = ''
        return stack.clear_stack()

    print(f'  Выбран файл: "{file}"') if file else None

    if action:
        stack.ad_element(action)
        globals()[action]()

    if isinstance(num_file, int) and mem_stack:
        if len(mem_stack) > 1 and mem_stack[-1] == 'choice_file':
            file = choice_file(num=num_file)
            action = mem_stack[0]
            globals()[action]()

    if yes_no == 'yes' and mem_stack and file:
        if mem_stack[-1] == 'delete_file':
            file_action.delete_file(file, permission=True)
            stack.clear_stack()
            file = ''


def file_existence(function) -> ():
    def wrapper() -> None | str | list[str]:
        if not file:
            return choice_file()
        function()
    return wrapper


def file_existence_and_clear_stack(function) -> ():
    def wrapper() -> None:
        file_existence(function)
        stack.clear_stack()
    return wrapper


def choice_file(num=None) -> Union[None, str, list[str]]:
    global file
    files = os.listdir(note_dir)

    if not num and files_list():
        stack.ad_element('choice_file')
        return talk('Выберите файл блокнота по номеру.')

    try:
        if num and 0 < int(num) <= len(files):
            file = files[num - 1]
            print(f'  Выбран файл: {file}')
            return file

    except (ValueError, IndexError):
        talk('Не коректный выбор!')
        choice_file()


@file_existence
def read_file():
    file_action.read_file(file)


@file_existence
def edit_file():
    file_action.edit_file(file)


@file_existence
def rename_file():
    file_action.rename_file(file)


@file_existence_and_clear_stack
def delete_file():
    file_action.delete_file(file)


def create_file() -> bool:
    stack.clear_stack()
    return file_action.create_file()


def create_memo_file() -> bool:
    stack.clear_stack()
    return file_action.create_memo_file(cmdline)
