#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import run
import tkinter as tk
from contextlib import redirect_stdout
from threading import Thread
import time
import subprocess as sub

from assistant import Assistant
from dialog import title_app
from skills import SysInformer
from widgets.app_widget import AppWidget

run_script: bool = False
num_scripts_to_run = 0


class TextWrapper:

    def __init__(self, text_field: tk.Text, label_field: tk.Label, info_label_field: tk.Label):
        self.text_field = text_field
        self.label_field = label_field
        self.info_label_field = info_label_field

    def get_output(self, text: str) -> None:
        input_color = '#99ff66'
        output_color = '#66b3ff'

        if 'Перезагружаюсь!' in text:
            self.text_field.delete(1.0, 'end')
            run(f'python3 start_app.py &', shell=True)

        if 'очист' in text.lower() and 'экран' in text:
            self.text_field.delete(1.0, 'end')

        if 'Mode:' in text:
            self.label_field.configure(text=f'{title_app} • {text}')

        elif '-infolabele-' in text:
            sys_info_string = ''
            string = text.replace('-infolabele-', '')

            if 'Core' in text:
                sys_info_string = string

            if 'runtime' in text and 'Core' in self.info_label_field['text']:
                runtime = string.replace('runtime', '')
                sys_info_string = self.info_label_field['text'].replace('no process', runtime)

            self.info_label_field.configure(text=sys_info_string)

        else:
            index_str = self.text_field.index('insert')
            self.text_field.insert('end', text)
            self.text_field.see('end')
            self.text_field.tag_add('input', index_str, 'end')
            self.text_field.tag_add('output', index_str, 'end')
            rm_tag = work_tag = color = ''

            if '◄' in text:
                rm_tag, work_tag, color = 'output', 'input', input_color
            elif '►' in text:
                rm_tag, work_tag, color = 'input', 'output', output_color

            self.text_field.tag_remove(rm_tag, index_str, 'end')
            self.text_field.tag_config(work_tag, foreground=color)

    def write(self, text_: str) -> None:
        self.get_output(text_)

    def flush(self) -> None:
        self.text_field.update()
        self.label_field.update()
        self.info_label_field.update()


def check_run_scr() -> None:
    """
    This function monitors the execution of scripts in the system.
    (only reacts to files with "sh" extension)
    Эта функция мониторит выполнение скриптов в системе.
    (реагирует только на файлы с расширением "sh")
    """
    global run_script, num_scripts_to_run
    run_scripts = []

    def report_completion() -> None:
        talk = Assistant().speaks
        talk(' Скрипт выполнен!', print_str=f'  Script: Completed!')

    try:
        pgrep_str = sub.check_output(f'pgrep -a xterm | grep -F ".sh" ', encoding='utf-8', shell=True).strip()
        [run_scripts.append(i.split('/')[-1]) for i in pgrep_str.split('\n')]
        n = len(run_scripts)
        if num_scripts_to_run > n:
            report_completion()
        num_scripts_to_run = n
        run_script = True

    except sub.CalledProcessError:
        num_scripts_to_run = 0
        pass

    if run_script and num_scripts_to_run == 0:
        run_script = False
        report_completion()


def thread_monitoring() -> None:
    sysmonitor = SysInformer()

    while True:
        if not thread.is_alive():  # Слежка за главным потоком.
            return AppWidget.close_widget()
        check_run_scr()  # Слежка за выполнением скриптов в системе.
        sysmonitor.sys_monitoring()  # Слежка за системой.
        time.sleep(2)


thread = Thread(target=Assistant().listening)  # Создаём главный поток.
is_alive_thread = Thread(target=thread_monitoring)  # Создаём поток слежки за главным потоком.


def main() -> None:
    text = AppWidget.text
    label = AppWidget.label
    info_label = AppWidget.info_label
    widget = AppWidget.root

    # noinspection PyTypeChecker
    with redirect_stdout(TextWrapper(text, label, info_label)):  # Перенаправляем весь STDOUT в окно tkinter.
        thread.start()  # Запускаем главный поток.
        is_alive_thread.start()  # Запускаем поток слежки за главным потоком.
        widget.protocol('WM_DELETE_WINDOW', widget.destroy)
        widget.mainloop()


if __name__ == '__main__':
    main()
