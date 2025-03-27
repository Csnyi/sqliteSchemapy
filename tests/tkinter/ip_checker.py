import customtkinter as ctk
import re
import ipaddress

class IPValidator:
    @staticmethod
    def validate_partial_ip(value):
        #Gépelés közbeni IP-rész validálása (gyors, memóriakímélő).
        if value == "":
            return True
        if not re.match(r"^[0-9.]*$", value):  # Csak szám és pont
            return False
        parts = value.split(".")
        for part in parts:
            if part and (not part.isdigit() or int(part) > 255):
                return False
        return len(parts) <= 4  # Max 4 oktett

    @staticmethod
    def validate_full_ip(ip):
        #Teljes IP-cím ellenőrzése ipaddress segítségével.
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IP Input")
        self.geometry("300x150")

        self.sidebar_frame = ctk.CTkFrame(self)
        self.sidebar_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.sidebar_stbip_label = ctk.CTkLabel(self.sidebar_frame, text="STB IP:")
        self.sidebar_stbip_label.pack()

        self.vcmdip = (self.register(self.validate_input), "%P")
        self.sidebar_stbip_entry = ctk.CTkEntry(self.sidebar_frame, validate="key", validatecommand=self.vcmdip)
        self.sidebar_stbip_entry.pack()

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="")
        self.status_label.pack()

        self.sidebar_stbip_entry.bind("<KeyRelease>", self.on_ip_typing)

    def validate_input(self, value):
        #Hook a tkinter input validálásához (csak számok és pontok)
        return IPValidator.validate_partial_ip(value)

    def on_ip_typing(self, event):
        #Amikor a felhasználó beírja az IP-t, teljes validációt végzünk.
        ip = self.sidebar_stbip_entry.get().strip()
        if IPValidator.validate_full_ip(ip):
            self.status_label.configure(text=f"✔ Érvényes IP: {ip}", text_color="green")
        else:
            self.status_label.configure(text="❌ Érvénytelen IP", text_color="red")

app = MyApp()
app.mainloop()

