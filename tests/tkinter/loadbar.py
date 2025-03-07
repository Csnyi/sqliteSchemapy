from tkinter import *
from tkinter import ttk
import time


def load_bar():
    def iterating_func():
        for x in range(101):
            lbl["text"] = str(x)
            progress['value'] = x 
            root.update_idletasks() 
            time.sleep(0.02)  # slow down the loop

    root = Tk()
    progress = ttk.Progressbar(root)	
    lbl = Label(root, text="Warming Up")
    lbl.pack()
    progress.pack()

    root.after(1000, iterating_func)
    root.mainloop()

load_bar()