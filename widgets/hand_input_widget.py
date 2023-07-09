import tkinter as tk

input_text = ''


def keyboard_input(entry_text=''):
    def get_entry():
        global input_text
        input_text = entry.get().replace(' › ', '')
        entry.delete(0, 'end')
        input_window.destroy()

    input_window = tk.Tk()
    input_window.title('hand input')
    input_window.geometry("550x35+400+280")
    input_window.resizable(False, False)
    input_window.configure(border=0, background='#121721')
    input_window.wait_visibility(input_window)
    input_window.wm_attributes("-alpha", 0.8)

    entry = tk.Entry(input_window,
                     borderwidth=1, relief='flat',
                     background='#000000',
                     insertbackground='#121721',
                     insertwidth=1,
                     highlightcolor='#242e42',
                     foreground='#53ff1a',
                     font='Hack 9',
                     width=68)
    entry.insert(0, ' › ' + entry_text)
    entry.focus_set()
    entry.pack(side='left', padx=5, ipady=3)

    btn = tk.Button(input_window,
                    command=get_entry,
                    border='1', relief='flat',
                    text='OK',
                    font='Arial 8',
                    activebackground='#090c10',
                    background='#000000',
                    activeforeground='#ffffff',
                    foreground='#53ff1a',
                    width=4)
    btn.pack(side='right', padx=5)

    input_window.mainloop()


def get_input(text=''):
    keyboard_input(text)
    print(input_text)
    return input_text
