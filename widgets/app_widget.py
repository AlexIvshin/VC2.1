import configparser
import sys
import pathlib
import tkinter as tk
from typing import Any

# Модули приложения
from dialog import title_app

config_path = pathlib.PurePosixPath(pathlib.Path(__file__).parent.absolute()).parent / "settings.ini"
config = configparser.ConfigParser()
config.read(config_path)


class AppWidget:
    root = tk.Tk()
    displaysize_x = root.winfo_screenwidth()
    w = int(config['WidgetSize']['width'])
    h = int(config['WidgetSize']['height'])
    x = int((displaysize_x - w) / 2)
    root.geometry(f"{w}x{h}+{x}+20")
    root.title(title_app)
    root.resizable(False, False)
    root.wait_visibility(root)
    root.wm_attributes("-alpha", 0.8)
    # root.configure(border=2)

    label = tk.Label(
        root,
        text=title_app,
        background='#090c10',
        foreground='#53ff1a',
        font='Hack 7',
        anchor='center',
        padx=7)
    label.pack(fill='x')

    text = tk.Text(
        root,
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

    info_label = tk.Label(
        root,
        compound="bottom",
        background='#000000',
        foreground='#00cc00',
        font='Hack 7',
        anchor='w',
        padx=7)
    info_label.pack(expand=True, fill='x')

    @classmethod
    def close_widget(cls) -> Any:
        cls.root.quit()
        try:
            cls.root.destroy()
        except RuntimeError:
            pass
        return sys.exit()
