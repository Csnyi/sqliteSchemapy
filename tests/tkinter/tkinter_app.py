import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class MyFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.text = "valami valami szigony"
        
        def optionmenu_callback(choice):
            print("optionmenu dropdown clicked:", choice)

        self.optionmenu = ctk.CTkOptionMenu(self, values=["option 1", "option 2"], command=optionmenu_callback)
        self.optionmenu.set("option 2")
        self.optionmenu.grid()
        
        # add widgets onto the frame, for example:
        self.label = ctk.CTkLabel(self, text=self.text)
        self.label.grid(row=1, column=0, padx=20)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x200")
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

        self.my_frame = MyFrame(master=self)
        self.my_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


app = App()
app.mainloop()