import os
from dialog import notebook_action_dict, yes_no_dict
from assistant import Assistant, stack
from skills import FileLife
from wordstonum import word2num_ru as w2n
import utils as tls

file_action = FileLife()
model = Assistant()
talk = model.speaks

homedir = file_action.homedir
note_dir = file_action.note_dir

cmdline = None
file = None
action = None


def files_list():
    files = os.listdir(note_dir)
    print(note_dir)

    if not files:
        talk('Файлы не обнаружены.')
        return False

    print('#   Name')
    [print(f'{position} < {f}') for position, f in enumerate(files, 1)]
    print()
    return True


def notebook_reacts(commandline):
    global action, file, cmdline

    cmdline = commandline
    yes_no = tls.check_yesno_onoff(cmdline, dictionary=yes_no_dict)
    num_file = w2n(cmdline)
    action, intersection = tls.choice_action(cmdline, notebook_action_dict)
    mem_stack: list = stack.get_stack()

    if yes_no == 'cancel':
        file = None
        return stack.clear_stack()
    print(f'Выбран файл: "{file}"') if file else None

    if action and intersection > 1:
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
            file = None


def file_existence(function):
    def wrapper():
        if not file:
            return choice_file()
        function()
    return wrapper


def file_existence_and_clear_stack(function):
    def wrapper():
        file_existence(function)
        stack.clear_stack()
    return wrapper


def choice_file(num=None):
    global file
    files = os.listdir(note_dir)

    if not num and files_list():
        stack.ad_element('choice_file')
        return talk('Выберите файл блокнота по номеру.')

    try:
        if num and 0 < int(num) <= len(files):
            file = files[num - 1]
            print(f'Выбран файл: {file}')
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


def create_file():
    stack.clear_stack()
    return file_action.create_file()


def create_memo_file():
    stack.clear_stack()
    return file_action.create_memo_file(cmdline)
