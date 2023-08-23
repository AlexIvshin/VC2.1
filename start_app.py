#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import run
import tkinter as tk
from contextlib import redirect_stdout
from threading import Thread
import time
import subprocess as sub

from assistant import Listener, Voice
from dialog import title_app
from skills import SysInformer
from widgets.app_widget import AppWidget

run_flag: bool = False
num_scr_to_run = 0


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
    global run_flag, num_scr_to_run
    run_scripts = []
    """
    This function monitors the execution of scripts in the XTERM.
    Эта функция мониторит выполнение скриптов в XTERM.
    """

    def report_completion() -> None:
        talk = Voice().speaks
        talk(' Скрипт выполнен!', print_str=f'  Script: Completed!')

    try:
        pgrep_str = sub.check_output(f'pgrep -a xterm | grep -F ./ ', encoding='utf-8', shell=True).strip()
        [run_scripts.append(i.split('/')[-1]) if i not in run_scripts else None for i in pgrep_str.split('\n')]
        last_num = len(run_scripts)
        if num_scr_to_run > last_num:
            report_completion()
        num_scr_to_run = last_num
        run_flag = True

    except sub.CalledProcessError:
        num_scr_to_run = 0
        if run_flag:
            run_flag = False
            report_completion()
        pass


def thread_monitoring() -> None:
    sysmonitor = SysInformer()
    __interval = 2
    """
    This function in a loop with an interval of 2 sec monitors the main thread "tread",
    and if it is interrupted, closes the main widget, and monitors the system and the execution of bash scripts.
    Эта функция в цикле с интервалом 2 сек следит за главным потоком tread, и если он прерван,
    закрывает главный виджет, а также мониторится система и исполнение bash-скриптов.
    """

    while True:
        if not thread.is_alive():
            return AppWidget.close_widget()
        check_run_scr()
        sysmonitor.sys_monitoring()
        time.sleep(__interval)


thread = Thread(target=Listener().audio_stream_capture)  # Создаём главный поток.
is_alive_thread = Thread(target=thread_monitoring)  # Создаём поток слежки за главным потоком.


def startapp() -> None:
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
    startapp()
