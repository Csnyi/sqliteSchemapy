from tkinter import *

root = Tk()
root.geometry("400x300")

def choosefunc(option):
    if option == "cancel":
        print("Cancel choosen")
        frame.destroy()
    else:
        print("OK choosen")

def popupfunc():

    tl = Toplevel(root)
    tl.title("Languages")

    frame = Frame(tl)
    frame.grid()

    canvas = Canvas(frame, width=100, height=130)
    canvas.grid(row=1, column=0)
    imgvar = PhotoImage(file="pyrocket.png")
    canvas.create_image(50,70, image=imgvar)
    canvas.image = imgvar

    msgbody1 = Label(frame, text="The", font=("Times New Roman", 20, "bold"))
    msgbody1.grid(row=1, column=1, sticky=N)
    lang = Label(frame, text="language(s)", font=("Times New Roman", 20, "bold"), fg='blue')
    lang.grid(row=1, column=2, sticky=N)
    msgbody2 = Label(frame, text="of this country is: Arabic", font=("Times New Roman", 20, "bold"))
    msgbody2.grid(row=1, column=3, sticky=N)

    cancelbttn = Button(frame, text="Cancel", command=tl.destroy, width=10)
    cancelbttn.grid(row=2, column=3)

    okbttn = Button(frame, text="OK", command=lambda: choosefunc("ok"), width=10)
    okbttn.grid(row=2, column=4)

label = Label(root, text="Click to proceed:")
label.grid()

button = Button(root, text="Click", command=popupfunc)
button.grid()

root.mainloop()