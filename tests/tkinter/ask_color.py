#https://www.tutorialspoint.com/python/python_gui_programming.htm
from tkinter.colorchooser import askcolor
from tkinter import *
import customtkinter as ctk

top = ctk.CTk()
top.geometry("400x250")

ctk.set_widget_scaling(2)

def showB():
   color = askcolor()
   L.configure(text=f"A kiválasztott szín kódja: \n{color}")
   
B = ctk.CTkButton(top, text ="Ask Color", command = showB)
B.grid(row=0, column=0, padx=20, pady=10)

L = ctk.CTkLabel(top, text="A kiválasztott szín kódja: ")
L.grid(row=1, column=0, padx=20, pady=10)

top.mainloop()