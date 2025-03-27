import customtkinter as ctk
import ipaddress
import random  # Szimulált hálózati hibához

def wpos_center(w, h, root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = w
    window_height = h
    pos_x = (screen_width // 2) - (window_width // 2)
    pos_y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("tkthemes/breeze.json")  # Themes: "blue" (standard), "green", "dark-blue"

class IPInputDialog(ctk.CTkToplevel):
    def __init__(self, master=None, title="IP Cím Bekérése"):
        super().__init__(master)
        self.title(title)
        
        wpos_center(300, 150, self)
        self.resizable(False, False)

        # Fő címke (itt jelenik meg az IP kérés és a hibaüzenet is)
        self.label = ctk.CTkLabel(self, text="Adjon meg egy IP-címet:")
        self.label.pack(pady=10)

        # IP beviteli mező
        self.entry = ctk.CTkEntry(self)
        self.entry.pack(pady=5)
        self.entry.bind("<KeyRelease>", self.validate_ip)

        # OK gomb
        self.ok_button = ctk.CTkButton(self, text="OK", state="disabled", command=self.on_ok)
        self.ok_button.pack(pady=10)

        # ENTER gomb hozzárendelése az OK funkcióhoz
        self.bind("<Return>", self.on_ok) 

        self.result = None
        self.grab_set()  # Az ablak modális lesz

    def validate_ip(self, event=None):
        """Érvényesíti az IP-címet."""
        ip = self.entry.get().strip()
        try:
            ipaddress.ip_address(ip)
            self.ok_button.configure(state="normal")
            self.label.configure(text="Adjon meg egy IP-címet:", text_color="#4b8899")  # Alapértelmezett szöveg visszaállítása
        except ValueError:
            self.ok_button.configure(state="disabled")

    def show_error(self, message):
        """Megjeleníti a hibaüzenetet a label-ben piros színnel."""
        self.label.configure(text=message, text_color="red")

    def on_ok(self, event=None):
        """Az OK gomb megnyomásakor validálja az IP-t és ellenőrzi a hálózatot."""
        ip = self.entry.get().strip()

        # Hálózati ellenőrzés
        if not network_check(ip):
            self.show_error("❌ Hálózati hiba! Próbáljon meg másik IP-t.")
            return  # Ne zárja be az ablakot, hadd módosítsa az IP-t

        self.result = ip  # Ha sikeres, elmentjük az eredményt
        self.destroy()  # Ablak bezárása

def ask_for_ip():
    """IP-cím bekérése a felhasználótól, amíg nem sikerül kapcsolódni."""
    while True:
        app.update()  # A főablak frissítése a megjelenítéshez

        dialog = IPInputDialog()
        dialog.wait_window()  # Megvárjuk, míg bezáródik

        if not dialog.result:  
            print("❌ Nincs IP megadva, kilépés...")
            app.destroy()  # Kilépünk az egész alkalmazásból
            return None  

        return dialog.result  # Visszaadja az érvényes IP-t

def network_check(ip):
    """Hálózati kapcsolat ellenőrzése (szimulált)."""
    return random.choice([True, False])  # Véletlenszerűen siker vagy hiba

# 🔥 Fő program
app = ctk.CTk()

wpos_center(640, 480, app)

app.withdraw()  # A főablak elrejtése

ip = ask_for_ip()

if ip:
    app.deiconify()  # Ha sikerült, megjelenítjük a főablakot
    print(f"✅ Sikeres kapcsolat az IP-hez: {ip}")
    app.mainloop()
else:
    print("🚪 Kilépés...")
