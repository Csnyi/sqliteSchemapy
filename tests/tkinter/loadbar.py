import time
import threading
import tkinter as tk
from tkinter import ttk

def load_bar():
    def iterating_func():
        for x in range(101):
            lbl["text"] = str(x)  # Frissíti a címkét
            progress["value"] = x  # Frissíti a progress bárt
            time.sleep(0.2)  # Szimulált művelet késleltetése

    def start_thread():
        threading.Thread(target=iterating_func, daemon=True).start()

    root = tk.Tk()
    root.geometry("300x150")

    progress = ttk.Progressbar(root, length=200, mode="determinate")
    lbl = tk.Label(root, text="Warming Up")

    lbl.pack(pady=10)
    progress.pack(pady=10)

    start_button = tk.Button(root, text="Start", command=start_thread)
    start_button.pack(pady=10)

    root.mainloop()

load_bar()

"""

import customtkinter as ctk
import threading
import time

def hosszabb_folyamat():
    #Ez szimulál egy hosszabb ideig tartó műveletet.
    progress_bar.start()  # ProgressBar elindítása
    time.sleep(5)  # Itt történne a valódi folyamat
    progress_bar.stop()  # ProgressBar leállítása
    print("Folyamat befejeződött.")

def indit_folyamat():
    #Egy új szálban indítja a hosszabb folyamatot, hogy a GUI ne fagyjon le.
    thread = threading.Thread(target=hosszabb_folyamat, daemon=True)
    thread.start()

root = ctk.CTk()
root.geometry("300x150")

progress_bar = ctk.CTkProgressBar(root, mode="indeterminate")
progress_bar.pack(pady=20)

start_button = ctk.CTkButton(root, text="Folyamat indítása", command=indit_folyamat)
start_button.pack(pady=10)

root.mainloop()
"""