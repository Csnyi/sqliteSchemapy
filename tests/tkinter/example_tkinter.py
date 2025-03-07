#https://www.tutorialspoint.com/python/python_gui_programming.htm
from tkinter.colorchooser import askcolor
from tkinter.simpledialog import askinteger
from tkinter.simpledialog import askfloat
from tkinter import messagebox
from tkinter import *

top = Tk()
top.geometry("100x100")

def showB():
   color = askcolor()
   print(color)
   
B = Button(top, text ="askcolor", command = showB)
B.place(x=50,y=50)

def showC():
   num = askinteger("Input", "Input an Integer")
   print(num)
   
C = Button(top, text ="askinteger", command = showC)
C.place(x=50,y=150)

def showD():
   num = askfloat("Input", "Input a floating point number")
   print(num)
   
D = Button(top, text ="askfloat", command = showD)
D.place(x=50, y=250)
#D.grid(row=1, column=0, padx=20)

top.mainloop()