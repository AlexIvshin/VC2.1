import tkinter as tk
from skills import SysInformer


class InfoWidget:
    sysinfo = SysInformer().get_sysinfo()

    infowid = tk.Tk()
    infowid.geometry(f"580x900+10+10")
    infowid.title('Sys Info')
    infowid.wm_attributes("-alpha", 0.9)

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

    for string in sysinfo:
        text.insert('end', string)

    text.mark_set('insert', 'end')
    text.pack(fill='x')


def show_sysinfo():
    widget = InfoWidget.infowid
    widget.mainloop()
