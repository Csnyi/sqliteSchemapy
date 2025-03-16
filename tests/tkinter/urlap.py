import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("tkthemes/Anthracite.json")

FIELDS = [
    {
        'title': 'Frequency:',
        'type': 'str'
    },{
        'title': 'Local Oscillator:',
        'type': 'list',
        'data': [
            "5150", 
            "5750", 
            "5950", 
            "9750", 
            "10000", 
            "10050", 
            "10450", 
            "10600", 
            "10700", 
            "10750", 
            "11250", 
            "11300"
        ]
    },{
        'title': 'Symbol rate:',
        'type': 'str'
    },{
        'title': 'Polarization:',
        'type': 'list',
        'data': ["Horizontal", "Vertical"]
    },{
        'title': 'Tone:',
        'type': 'list',
        'data': ["Off", "On"]
    },{
        'title': 'DISEqC Port - Command:',
        'type': 'list',
        'data': [
            "Off",
            "--- 1.0, up to 4 ports ---",
            "01 - E01038F0",
            "02 - E01038F4",
            "03 - E01038F8",
            "04 - E01038FC",
            "--- 1.1, up to 16 ports ---",
            "--- UNCOMMITTED ---",
            "01 - E01039F0",
            "02 - E01039F1",
            "03 - E01039F2",
            "04 - E01039F3",
            "05 - E01039F4",
            "06 - E01039F5",
            "07 - E01039F6",
            "08 - E01039F7",
            "--- COMMITTED ---",
            "09 - E01039F8",
            "10 - E01039F9",
            "11 - E01039FA",
            "12 - E01039FB",
            "13 - E01039FC",
            "14 - E01039FD",
            "15 - E01039FE",
            "16 - E01039FF",
        ]
    },{
        'title': '3D converter polling:',
        'type': 'list',
        'data': ["Disabled", "Enabled"]
    }
]

scaling_values = ["80%", "90%", "100%", "110%", "120%", "150%"]

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, master, info, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("+100+100")
        self.title("Adatok")

        self.label = ctk.CTkLabel(self, text=info, justify="left")
        self.label.pack(padx=20, pady=20, fill="both", expand=True)

        self.button = ctk.CTkButton(self, text="Ok", command=self.destroy)
        self.button.pack(padx=20, pady=20)

    def update_text(self, new_text):
        """Szöveg frissítése az ablakban"""
        self.label.configure(text=new_text)

class CustomOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, parent, values, *args, **kwargs):
        super().__init__(parent, values=values, *args, **kwargs)
        self.old_value = values[0]  # Alapértelmezett érték
        self.configure(command=self.on_select)

    def on_select(self, choice):
        # Ellenőrizzük, hogy az adott érték tiltott-e
        if choice.startswith("---"):
            self.set(self.old_value)  # Ha tiltott, visszaállítjuk az előző értékre
        else:
            self.old_value = choice  # Frissítjük a régi értéket, ha szabályos a választás

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CustomTkinter Űrlap")
        self.geometry("+100+100")

        self.vcmd = self.register(self.validate_input)

        # Űrlap konténer frame
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, fill="both", expand=True)

        # Oszlopok méretezése
        self.form_frame.columnconfigure(0, weight=1)  # Label oszlop
        self.form_frame.columnconfigure(1, weight=2)  # Entry oszlop (nagyobb szélesség)

        self.entries = self.create_form(self.form_frame, FIELDS)

        # Gombok
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", padx=10, pady=5)
        self.button_frame.columnconfigure(1, weight=1)

        self.button_send = ctk.CTkButton(self.button_frame, text="Send", command=self.open_toplevel)
        self.button_send.pack(side="left", expand=True, fill="x")
        self.button_exit = ctk.CTkButton(self.button_frame, text="Exit", command=self.quit)
        self.button_exit.pack(side="right", expand=True, fill="x")
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.button_frame, values=scaling_values, command=self.ui_scaling)
        self.scaling_optionemenu.pack(expand=True, fill="x")

        self.toplevel_window = None

    def open_toplevel(self):
        info_text = self.show_data()
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self, info_text)  # Helyesen adjuk át a master-t
        else:
            self.toplevel_window.update_text(info_text)  # Ha létezik az ablak, fókuszáljunk rá
        self.toplevel_window.lift()

    def create_form(self, parent, fields):
        entries = {}
        for i, field in enumerate(fields):
            ctk.CTkLabel(parent, text=field["title"], anchor="w").grid(row=i, column=0, padx=10, pady=5, sticky="ew")

            if field["type"] == "str":
                entry = ctk.CTkEntry(parent, validate="key", validatecommand=(self.vcmd, "%P"))
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
                entries[field["title"]] = entry

            elif field["type"] == "list":
                option_menu = CustomOptionMenu(parent, values=field["data"])
                option_menu.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
                entries[field["title"]] = option_menu
        print(entries["DISEqC Port - Command:"].get())
        return entries

    def validate_input(self, value):
        """Csak számokat és egyetlen pontot engedélyez"""
        if value == "" or value.replace(".", "", 1).isdigit():
            return True
        return False

    def show_data(self):
        data = {key: entry.get() for key, entry in self.entries.items()}
        text = "\n".join(f"{key}: {value}" for key, value in data.items())
        return text

    def ui_scaling(self, choice):
        choice_scaling_float = int(choice.replace("%", "")) / 100
        ctk.set_widget_scaling(choice_scaling_float)

if __name__ == '__main__':
    app = App()
    app.mainloop()
 
