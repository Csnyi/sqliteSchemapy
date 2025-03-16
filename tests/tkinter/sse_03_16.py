import requests
import threading
import tkinter as tk
import customtkinter as ctk
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sseclient import SSEClient

STB_IP = "192.168.1.5"  # Állítsd be a megfelelő IP címet

class STBMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("STB Spectrum / SNR Vezérlő")
        self.geometry("800x600")

        self.event_source = None
        self.event_thread = None
        self.running = True  # Folyamatos SSE figyelés
        self.mode = "spectrum"  # Alapértelmezett mód

        # GUI elemek
        self.status_var = tk.StringVar(value="Kapcsolódás...")
        self.status_label = ctk.CTkLabel(self, textvariable=self.status_var, font=("Arial", 16))
        self.status_label.pack(pady=10)

        self.freq_entry = ctk.CTkEntry(self, placeholder_text="Frekvencia (MHz, pl. 1333)")
        self.freq_entry.pack(pady=5)

        self.sr_entry = ctk.CTkEntry(self, placeholder_text="Symbol Rate (pl. 63000)")
        self.sr_entry.pack(pady=5)

        # Módválasztó dropdown
        self.mode_var = tk.StringVar(value="spectrum")
        self.mode_selector = ctk.CTkOptionMenu(self, values=["snr", "spectrum", "blindscan"], 
                                               command=self.change_mode, variable=self.mode_var)
        self.mode_selector.pack(pady=5)

        self.send_button = ctk.CTkButton(self, text="Parancs Küldése", command=self.send_command)
        self.send_button.pack(pady=10)

        # Matplotlib ábra létrehozása
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.ax.set_title("Spektrum Analízis")
        self.ax.set_xlabel("Frekvencia pontok")
        self.ax.set_ylabel("Jelszint (dB)")
        self.line, = self.ax.plot([], [], "b-", lw=1)

        # Matplotlib integrálása a Tkinter ablakba
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(pady=10)

        # SSE események figyelésének indítása
        self.event_thread = threading.Thread(target=self.listen_sse, daemon=True)
        self.event_thread.start()

    def send_command(self):
        """Elküldi az initSmartSNR parancsot az STB-nek az aktuális mód és paraméterek alapján."""
        freq = self.freq_entry.get()
        sr = self.sr_entry.get()

        if not freq:
            self.status_var.set("Hiba: Adj meg frekvenciát!")
            return

        if not sr:
            sr = "63000"  # Spectrum módhoz fix érték

        url = f"http://{STB_IP}/public?command=initSmartSNR&state=on&mode={self.mode}&freq={freq}&sr={sr}&pol=1&tone=0&diseqc_hex=E01038F0"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                self.status_var.set(f"Parancs elküldve: {self.mode} mód")
            else:
                self.status_var.set(f"Hiba: {response.status_code}")
        except requests.RequestException as e:
            self.status_var.set(f"Hálózati hiba: {str(e)}")

    def change_mode(self, selected_mode):
        """Mód váltása (snr, spectrum, blindscan)."""
        self.mode = selected_mode
        self.status_var.set(f"Mód beállítva: {self.mode}")

    def listen_sse(self):
        """Folyamatos SSE figyelés háttérszálban."""
        url = f"http://{STB_IP}/public?command=startEvents"
        
        try:
            self.event_source = SSEClient(url)
            for event in self.event_source:
                if not self.running:
                    break
                data = event.data
                self.after(0, self.process_sse_data, data)
        except Exception as e:
            self.after(0, self.status_var.set, f"SSE hiba: {str(e)}")

    def process_sse_data(self, data):
        """GUI frissítése az SSE események alapján."""
        try:
            parsed_data = json.loads(data)

            # Scan status és lock állapot kiírása
            scan_status = parsed_data.get("scan_status", "N/A")
            lock = "Locked" if parsed_data.get("lock") == 1 else "Not Locked"
            self.status_var.set(f"Status: {scan_status} | Lock: {lock}")

            # Spektrum adatok frissítése, ha "spectrum_array" létezik
            if "spectrum_array" in parsed_data:
                spectrum_data = parsed_data["spectrum_array"]
                self.update_spectrum_chart(spectrum_data)

        except Exception:
            self.status_var.set(f"SSE adat: {data}")

    def update_spectrum_chart(self, spectrum_data):
        """Frissíti a matplotlib grafikont a kapott spektrum adatokkal."""
        x_values = list(range(len(spectrum_data)))  # 0-479 pont
        y_values = spectrum_data

        self.line.set_xdata(x_values)
        self.line.set_ydata(y_values)
        self.ax.relim()  # Újraértékeli a tengelyeket
        self.ax.autoscale_view()  # Automatikusan méretezi a grafikont

        self.canvas.draw()  # Frissíti a rajzot

if __name__ == "__main__":
    app = STBMonitor()
    app.mainloop()
