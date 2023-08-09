#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from subprocess import run
import tkinter as tk
from contextlib import redirect_stdout
from threading import Thread
import time
import subprocess as sub

from assistant import Assistant
from skills import SysInformer

import configparser
import pathlib

config_path = pathlib.Path(__file__).parent.absolute() / "settings.ini"
config = configparser.ConfigParser()
config.read(config_path)
run_script: bool = False


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
            self.label_field.configure(text='VCom 2.1 • ' + text)

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


class AppWidget:
    root = tk.Tk()
    displaysize_x = root.winfo_screenwidth()
    w = int(config['WidgetSize']['width'])
    h = int(config['WidgetSize']['height'])
    x = int((displaysize_x - w) / 2)
    root.geometry(f"{w}x{h}+{x}+20")
    root.title('VCom 2.1')
    root.resizable(False, False)
    root.wait_visibility(root)
    root.wm_attributes("-alpha", 0.8)
    # root.configure(border=2)

    label = tk.Label(root,
                     text='VCom 2.1',
                     background='#090c10',
                     foreground='#53ff1a',
                     font='Hack 7',
                     anchor='center',
                     padx=7)
    label.pack(fill='x')

    text = tk.Text(root,
                   height=17,
                   border=0,
                   background='#000000',
                   selectbackground='#303d30',
                   highlightthickness=0,
                   insertwidth=0,
                   font='Hack 9',
                   wrap='word',
                   padx=7)
    text.mark_set('insert', 'end')
    text.pack(fill='x')

    info_label = tk.Label(root,
                          # border='1', relief='flat',
                          compound="bottom",
                          background='#000000',
                          foreground='#00cc00',
                          font='Hack 7',
                          anchor='w',
                          padx=7)
    info_label.pack(expand=True, fill='x')

    @classmethod
    def close_widget(cls) -> None:
        cls.root.quit()
        try:
            cls.root.destroy()
        except RuntimeError:
            pass
        sys.exit()


def check_run_scr() -> None:
    global run_script
    try:
        pgrep_str = sub.check_output(f'pgrep -a xterm | grep -F ".sh" ', encoding='utf-8', shell=True)
        scr_name = pgrep_str.split('/')[-1]
        run_script = True
    except sub.CalledProcessError:
        scr_name = ''
        pass

    if run_script and not scr_name:
        talk = Assistant().speaks
        talk(' Скрипт выполнен!', print_str=f'  Script: Done completed!')
        run_script = False


def thread_monitoring() -> None:
    sysmonitor = SysInformer()
    while True:
        if not thread.is_alive():
            return AppWidget.close_widget()
        # Определяем выполняется ли скрипт '*.sh' в XTERM.
        # Для корректной работы, расширение файла скрипта обязательно 'sh'!
        check_run_scr()
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
    with redirect_stdout(TextWrapper(text, label, info_label)):  # Перенаправляем весь STDOUT в tkinter.
        thread.start()  # Запускаем главный поток.
        is_alive_thread.start()  # Запускаем поток слежки за главным потоком.
        widget.protocol('WM_DELETE_WINDOW', widget.destroy)
        widget.mainloop()


if __name__ == '__main__':
    main()
