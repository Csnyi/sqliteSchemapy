import customtkinter as ctk

class CustomComboBox(ctk.CTkComboBox):
    def __init__(self, parent, values, disabled_values=None, **kwargs):
        super().__init__(parent, values=values, **kwargs)
        self.disabled_values = disabled_values if disabled_values else []
        self.previous_value = values[0]  # Kezdő érték

        self.set(self.previous_value)
        self.bind("<<ComboboxSelected>>", self.on_select)

    def on_select(self, event=None):
        """Ha tiltott értéket választanak, visszaáll az előző értékre."""
        current_value = self.get()
        if current_value in self.disabled_values:
            self.set(self.previous_value)  # Visszaáll az előző érvényes értékre
        else:
            self.previous_value = current_value  # Frissítjük az érvényes értéket

# Alkalmazás létrehozása
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("400x300")

options = [
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

# Inaktív értékek (ezek nem választhatók)
disabled_options = [
    "--- 1.0, up to 4 ports ---",
    "--- 1.1, up to 16 ports ---",
    "--- UNCOMMITTED ---",
    "--- COMMITTED ---",
]

combo = CustomComboBox(app, values=options, disabled_values=disabled_options)
combo.pack(pady=20, padx=20)

app.mainloop()
