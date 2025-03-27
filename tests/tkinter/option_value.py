import customtkinter as ctk
import requests

STB_IP = "192.168.1.2"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CTkOptionMenu - API alapú frissítés")
        self.geometry("400x250")

        # CTkOptionMenu kezdeti értékek
        self.option_values = {}  # Szótár az sat_name -> sat_id tárolására

        self.selected_var = ctk.StringVar(value="")  # Kezdőérték
        self.option_menu = ctk.CTkOptionMenu(self, values=[],  # Kezdetben üres lista
                                             variable=self.selected_var,
                                             command=self.on_option_change)
        self.option_menu.pack(pady=20)

        # Label a kiválasztott numerikus értékhez
        self.value_label = ctk.CTkLabel(self, text="Kiválasztott sat_id: N/A")
        self.value_label.pack(pady=10)

        # Gomb az adatok frissítésére
        self.update_button = ctk.CTkButton(self, text="Frissítés", command=self.update_options_from_api)
        self.update_button.pack(pady=20)

        # Automatikus API lekérdezés indításkor
        self.update_options_from_api()

    def on_option_change(self, choice):
        """ Amikor a felhasználó választ, frissítjük a numerikus értéket """
        selected_value = self.option_values.get(choice, "N/A")  # Ha nincs adat, akkor "N/A"
        self.value_label.configure(text=f"Kiválasztott sat_id: {selected_value}")

    def update_options_from_api(self):
        """ API lekérdezés és a CTkOptionMenu frissítése """
        url = f"http://{STB_IP}/public?command=returnSATList"  # API végpont
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                
                if "sat_list" in data:
                    # Az új adatok feldolgozása
                    self.option_values = {sat["sat_name"]: sat["sat_id"] for sat in data["sat_list"]}
                    new_keys = list(self.option_values.keys())  # Szöveges lista a legördülő menühöz

                    # CTkOptionMenu frissítése az új értékekkel
                    self.option_menu.configure(values=new_keys)
                    if new_keys:
                        self.option_menu.set(new_keys[0])  # Első elem beállítása alapértelmezettként
                        self.on_option_change(new_keys[0])  # Alapértelmezett érték frissítése

        except requests.RequestException as e:
            self.value_label.configure(text=f"Hálózati hiba: {e}")

app = App()
app.mainloop()
