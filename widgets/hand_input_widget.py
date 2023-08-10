import tkinter as tk

input_text = ''


def keyboard_input(entry_text: str = '') -> None:

    def get_entry() -> None:
        global input_text
        input_text = entry.get().replace(' › ', '')
        entry.delete(0, 'end')
        input_window.destroy()

    input_window = tk.Tk()
    displaysize_x = input_window.winfo_screenwidth()
    w, h, y = 700, 35, 370
    x = int((displaysize_x - w) / 2)
    input_window.geometry(f"{w}x{h}+{x}+{y}")
    input_window.title('hand input')
    input_window.resizable(False, False)
    input_window.configure(border=0, background='#121721')
    input_window.wait_visibility(input_window)
    input_window.wm_attributes("-alpha", 0.9)

    entry = tk.Entry(
        input_window,
        borderwidth=1, relief='flat',
        background='#000000',
        insertbackground='#121721',
        insertwidth=1,
        highlightcolor='#242e42',
        foreground='#aab3a8',
        font='Arial 10',
        width=68
    )
    entry.insert(0, ' › ' + entry_text)
    entry.focus_set()
    entry.pack(side='left', padx=5, ipady=3)

    btn = tk.Button(
        input_window,
        command=get_entry,
        border='0',
        highlightthickness=0,
        text='Ok',
        font='Arial 8',
        activebackground='#2a3242',
        background='#1a212e',
        activeforeground='#53ff1a',
        foreground='#389918',
        width=5
    )
    btn.pack(side='right', padx=5)

    input_window.mainloop()


def get_input(text='') -> str:
    keyboard_input(text)
    print(input_text)
    return input_text
