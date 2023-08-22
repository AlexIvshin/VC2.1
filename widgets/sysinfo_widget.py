import tkinter as tk
from skills import SysInformer


class InfoWidget:

    @staticmethod
    def insert_text(text_field: tk.Text) -> None:
        [text_field.insert('end', string) for string in SysInformer().get_sysinfo()]

    infowid = tk.Tk()
    infowid.geometry(f"580x935+10+20")
    infowid.title('System Information')
    infowid.wm_attributes("-alpha", 0.8)

    text = tk.Text(
        infowid,
        height=55,
        border=0,
        background='#000000',
        selectbackground='#303d30',
        foreground='#66b3ff',
        highlightthickness=0,
        insertwidth=0,
        font='Hack 9',
        wrap='word',
        padx=7)

    insert_text(text)

    text.mark_set('insert', 'end')
    text.pack(fill='x')


def show_sysinfo() -> None:
    InfoWidget.infowid.mainloop()
