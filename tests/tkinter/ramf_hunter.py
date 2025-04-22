import requests
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import json
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sseclient import SSEClient
from ramf_variables import *
import time
import platform
import re
import logging

# Alapértelmezett beállítások: naplófájlba mentés és konzolra is ír
logging.basicConfig(
    filename="app.log",  # Naplófájl neve
    level=logging.INFO,   # INFO szintű loggolás
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("========= Program indítása =========")
## logging.warning("Ez egy figyelmeztetés!")
## logging.error("Valami hiba történt!")

# ctk
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("tkthemes/breeze.json")  # Themes: "blue" (standard), "green", "dark-blue"

class IPInputDialog(ctk.CTkToplevel):
    def __init__(self, master=None, title="IP Cím Bekérése"):
        super().__init__(master)
        self.title(title)
        
        self.geometry(wpos_center(300, 150, self))
        self.resizable(False, False)

        # Fő címke (itt jelenik meg az IP kérés és a hibaüzenet is)
        self.label = ctk.CTkLabel(self, text="STB IP:", anchor="w")
        self.label.pack(pady=10)

        # IP beviteli mező
        self.vcmdip = self.register(self.validate_ip)
        self.entry = ctk.CTkEntry(self, validate='key', validatecommand=(self.vcmdip, "%P"))
        self.entry.pack(pady=5)
        self.entry.bind("<KeyRelease>", self.on_ip_typing)

        # OK gomb
        self.ok_button = ctk.CTkButton(self, text="OK", state="disabled", command=self.on_ok)
        self.ok_button.pack(pady=10)

        # ENTER gomb hozzárendelése az OK funkcióhoz
        self.bind("<Return>", self.on_ok) 
        
        self.result = None
        self.grab_set()  # Az ablak modális lesz

    
    # ====== ip valid and refress ====== start

    def validate_ip(self, value):
        """Gépelés közbeni IP-cím validálás"""
        if value == "":  
            return True  # Üres mező engedélyezett

        # Csak számokat és pontot engedélyezünk
        if not re.match(r"^[0-9.]*$", value):
            return False

        # Oktettek validálása
        parts = value.split(".")
        for part in parts:
            if part and (not part.isdigit() or int(part) > 255):  
                return False  # Csak 0-255 közötti számokat engedünk

        # Legfeljebb 4 oktett lehet
        if len(parts) > 4:
            return False

        return True  # Ha minden megfelel, érvényes lehet

    def on_ip_change_delayed(self):
        """Késleltetve ellenőrzi, hogy az IP-cím teljes-e"""
        ip = self.entry.get()
        if re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", ip):  # Csak ha teljes IP-cím
            self.ok_button.configure(state="normal")
            self.label.configure(text="STB IP:", text_color="#4b8899")

    def on_ip_typing(self, event):
        """Minden billentyű lenyomás után törli az előző időzítést és újat indít"""
        if hasattr(self, "typing_delay"):
            self.after_cancel(self.typing_delay)  # Meglévő időzítés törlése
        self.typing_delay = self.after(500, self.on_ip_change_delayed)  # 500ms késleltetés

    # ====== ip valid and refress ====== end

    def show_error(self, message):
        #Megjeleníti a hibaüzenetet a label-ben piros színnel.
        self.label.configure(text=message, text_color="red")

    def on_ok(self, event=None):
        """Az OK gomb megnyomásakor validálja az IP-t és ellenőrzi a hálózatot."""
        ip = self.entry.get().strip()

        # Hálózati ellenőrzés
        if not network_check(ip):
            self.show_error("STB IP:")
            return  # Ne zárja be az ablakot, hadd módosítsa az IP-t

        self.result = ip  # Ha sikeres, elmentjük az eredményt
        self.destroy()  # Ablak bezárása

def save_settings_ip(ip):
    with open("settings.json", "w") as f:
        json.dump({"ip": ip}, f)

def load_settings_ip():
    try:
        with open("settings.json") as f:
            return json.load(f).get("ip", "")
    except FileNotFoundError:
        return ""

def ask_for_ip():
    """IP-cím bekérése a felhasználótól, amíg nem sikerül kapcsolódni."""
    while True:
        dialog = IPInputDialog()
        dialog.wait_window()  # Megvárjuk, míg bezáródik

        if not dialog.result:  
            logging.info("Nincs IP megadva, kilépés...")
            app.destroy()  # Kilépünk az egész alkalmazásból
            return None  

        save_settings_ip(dialog.result)

        return dialog.result  # Visszaadja az érvényes IP-t

def network_check(ip):
    """GET kéréssel ellenőrzi, hogy az IP elérhető-e."""
    url = f"http://{ip}/public?command=version"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            logging.info(f"Hálózat rendben az IP-n: {ip}")
            return True  # Csak jelezzük, hogy működik
    except requests.RequestException:
        pass 
        
    logging.error(f"Hálózati hiba {ip}-n, próbáljon másik IP-t!")
    # CTkMessagebox(title="Error", message="Something went wrong!!!", icon="cancel")
    tk.messagebox.showerror(title="Error", message=f"Hálózati hiba {ip}-n, próbáljon másik IP-t!")
    return False

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, master, title, call, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Sent data")

        self.geometry(wpos_center(300, 350, self))

        self.label = ctk.CTkLabel(self, text=title, justify="left")
        self.label.pack(padx=5, pady=5, fill="both", expand=True)

            # Matplotlib ábra létrehozása
        self.fig, self.ax = plt.subplots(figsize=(6, 2))
        self.ax.set_title("Spektrum Analízis")
        self.ax.set_xlabel("Frekvencia pontok")
        self.ax.set_ylabel("Jelszint (dB)")
        self.line, = self.ax.plot([], [], "b-", lw=1)

            # Matplotlib integrálása a Tkinter ablakba
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.button = ctk.CTkButton(self, text="Exit", command=self.destroy)
        self.button.pack(padx=10, pady=10)

        if callable(call):  
            call(self)

    def update_chart(self, data):
        """Frissíti a matplotlib grafikont a kapott adatokkal."""
        x_values = list(range(len(data))) 
        y_values = data  

        self.line.set_xdata(x_values)
        self.line.set_ydata(y_values)
        self.ax.relim()  # Újraértékeli a tengelyeket
        self.ax.autoscale_view()  # Automatikusan méretezi a grafikont

        self.canvas.draw()  # Frissíti a rajzot

    def update_text(self, new_text):
        """Szöveg frissítése az ablakban"""
        self.label.configure(text=new_text)

class RamfApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.stb_ip = ""

        # --- configure window
        self.title("R.A.M.F. Report")
        self.geometry(wpos_center(appWidth, appHeight, self))

        self.tp_list = []
        self.sat_list = []
        self.dir_list = []
        self.report_list = {}
        self.report_data = []
        self.report_data_rssi = []
        self.version_run = False
        self.widget_scaling = 1

        self.event_source = None
        self.event_thread = None
        self.running = True  # Folyamatos SSE figyelés
        self.mode = "spectrum"  # Alapértelmezett mód

        # --- configure grid layout (3x4)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        self.vcmd = self.register(self.validate_input)

        # --- create sidebar frame with widgets

        sidebar_bottom_row_index = 8
        
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure((sidebar_bottom_row_index), weight=1)

            # version labels
        self.ver_lab_frame = ctk.CTkFrame(self.sidebar_frame)
        self.ver_lab_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.version_labels = self.create_labels(self.ver_lab_frame, VER_LABELS_FIELDS)

            # buttons top
        self.sidebar_button_propert = ctk.CTkButton(self.sidebar_frame, text="Event start", command=self.restart_sse)
        self.sidebar_button_propert.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_toggle = ctk.CTkButton(self.sidebar_frame, text="Event close", command=lambda: self.event_close(2))
        self.sidebar_button_toggle.grid(row=5, column=0, padx=20, pady=10)
        self.sidebar_button_exit = ctk.CTkButton(self.sidebar_frame, text="Exit", command=self.on_close)
        self.sidebar_button_exit.grid(row=6, column=0, padx=20, pady=10)

            # angles lables
        self.ang_lab_frame = ctk.CTkFrame(self.sidebar_frame)
        self.ang_lab_frame.grid(row=7, column=0, padx=20, pady=10, sticky="nsew")
        self.angles_labels = self.create_labels(self.ang_lab_frame, SPECT_LABELS_FIELDS)

            # buttons bottom
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=sidebar_bottom_row_index+1, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=sidebar_bottom_row_index+2, column=0, padx=20, pady=(10, 10))
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=sidebar_bottom_row_index+3, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=SCALING_VALUES, command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=sidebar_bottom_row_index+4, column=0, padx=20, pady=(10, 20))
        
        # --- create main bottom label (info row)

        self.info_frame = ctk.CTkFrame(self, corner_radius=0)
        self.info_frame.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.status_var = tk.StringVar(value="Kapcsolódás...")
        self.status_label = ctk.CTkLabel(master=self.info_frame, textvariable=self.status_var, font=("Arial", 16), anchor="w")
        self.status_label.grid(row=0, column=0, padx=10, pady=5)

        # --- create box top

        self.box_top = ctk.CTkFrame(self)
        self.box_top.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        self.box_top_labels = self.create_labels(self.box_top, SNR_LABELS_FIELDS)
        
        # --- create graph bottom

            # Matplotlib ábra létrehozása
        self.fig, self.ax = plt.subplots(figsize=(6, 2))
        self.ax.set_title("Spektrum Analízis")
        self.ax.set_xlabel("Frekvencia pontok")
        self.ax.set_ylabel("Jelszint (dB)")
        self.line, = self.ax.plot([], [], "b-", lw=1)

            # Matplotlib integrálása a Tkinter ablakba
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=2, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # --- create tabview 

        self.tabview = ctk.CTkTabview(self, width=100)
        self.tabview.grid(row=1, column=2, rowspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Spectrum Report")
        self.tabview.tab("Spectrum Report").grid_columnconfigure(0, weight=1)
        self.tabview.add("SNR Report")
        self.tabview.tab("SNR Report").grid_rowconfigure((0,2), weight=0)
        self.tabview.tab("SNR Report").grid_rowconfigure(1, weight=1)
        
            ## --- Spectrum Report Form

            #Spect label
        self.spect_form_label = ctk.CTkLabel(self.tabview.tab("Spectrum Report"), text="Spectrum Form")
        self.spect_form_label.grid(row=0, column=0)

            # spect form frame
        self.spect_form_frame = ctk.CTkFrame(self.tabview.tab("Spectrum Report"), border_width=0)
        self.spect_form_frame.grid(row=1, column=0, sticky="nsew")

        self.spect_form_row = self.create_form(self.spect_form_frame, SPECT_FIELDS)
        self.spect_form_row["sat_list"].configure(command=self.sat_list_changed)
        self.spect_form_row["tp_list"].configure(command=self.tp_list_changed)
        self.spect_form_row["report_list"].configure(command=self.report_list_changed)
        
            # Spect Button
        self.spect_button_create_report = ctk.CTkButton(self.tabview.tab("Spectrum Report"), text="Report", command=lambda: self.open_input_dialog_event(self.spect_form_row["sat_list"]))
        self.spect_button_create_report.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.spect_button_open_report = ctk.CTkButton(self.tabview.tab("Spectrum Report"), text="Open Report", command=lambda: self.open_toplevel("RSSI", self.toplevel_chart_update))
        self.spect_button_open_report.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")
        
            ## --- SNR Report Form

            # snr label
        self.snr_form_label = ctk.CTkLabel(self.tabview.tab("SNR Report"), text="SNR Form")
        self.snr_form_label.grid(row=0, column=0)

            # Snr form frame
        self.snr_form_frame = ctk.CTkScrollableFrame(self.tabview.tab("SNR Report"), border_width=0)
        self.snr_form_frame.grid(row=1, column=0, sticky="nsew")

        self.snr_form_row = self.create_form(self.snr_form_frame, SNR_FIELDS)
        self.snr_form_row["diseqc_hex"].configure(command=self.snr_dsqch_on_select)

            # Egér görgetés hozzárendelése a megfelelő eseményekhez
        self.snr_form_frame.bind("<Enter>", self.bind_scroll)
        self.snr_form_frame.bind("<Leave>", self.unbind_scroll)
        
            # Módválasztó dropdown
        self.mode_var = tk.StringVar(value="spectrum")
        self.mode_selector = ctk.CTkOptionMenu(self.tabview.tab("SNR Report"), values=["snr", "spectrum", "blindscan"], 
                                               command=self.change_mode, variable=self.mode_var)
        self.mode_selector.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

            # Snr send Buttons
        self.snr_button_send = ctk.CTkButton(self.tabview.tab("SNR Report"), text="Send", command=self.send_initSmartSNR)
        self.snr_button_send.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")

        # --- toplevel window set

        self.toplevel_window = None
        
        # --- create progressbar frame

        self.progressbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progressbar_frame.grid(row=0, column=1, columnspan=2,padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.progressbar_frame.grid_columnconfigure(0, weight=1)
        self.progressbar_1 = ctk.CTkProgressBar(self.progressbar_frame)
        self.progressbar_1.grid(row=1, column=0, padx=(10, 10), pady=(10, 10), sticky="ew")
        
        # --- set default values

        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.progressbar_1.configure(mode="indeterminate")
        self.progressbar_frame.grid_forget()

        # --- GUI bezárás eseménykezelő

        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    # ====== SSE ====== start
        
    def sat_list_changed(self, elem):
        """ Handle the satellite list changed event """
        try:
            sat_name = elem.split(" - ")[1]
            sat_id = next(sat["sat_id"] for sat in self.sat_list if sat["sat_name"] == sat_name)
            self.get_tplist(sat_id)
        except StopIteration as err:
            self.status_var.set(f"Error: {err}")
    
    def tp_list_changed(self, elem):
        """ Handle the transponder list changed event """
        try:
            freq = int(elem.split(" - ")[0])
            tp = next(tp for tp in self.tp_list if tp["freq"] == freq)
            sat = next(sat for sat in self.sat_list if sat["sat_id"] == tp["sat_id"])
            mid_freq = tp["freq"] - sat["lnb_low_freq"] if tp["freq"] < 11700 else tp["freq"] - sat["lnb_high_freq"]
            url = f"http://{self.stb_ip}/public?command=initSmartSNR&state=on&mode={self.mode}&freq={mid_freq}&sr=63000&pol={tp['polarity']}&tone={tp['tone']}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.status_var.set(f"Parancs elküldve: {self.mode} mód")
                else:
                    self.status_var.set(f"Hiba: {response.status_code}")
            except requests.RequestException as e:
                self.status_var.set(f"Hálózati hiba: {str(e)}")
    
        except StopIteration as err:
            self.status_var.set(f"Error: {err}")
    
    def report_list_changed(self, elem):
        logging.info(f"# report list changed {elem}")
        report_name = self.report_list[elem]
        # http://192.168.1.56/public?command=returnReport&report_name=e:/rpt_3_585E_2021-01-07_11_14_58.json
        url = f'http://{self.stb_ip}/public?command=returnReport&report_name=e:/{report_name}.json'
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                self.status_var.set(f"Report lekérve: {report_name}")
                self.report_data = response.json()
                logging.info(f"Report lekérve: {report_name}")
                logging.info(f'Report rssi: {self.process_report_data(self.report_data)}')
                self.report_data_rssi = self.process_report_data(self.report_data)
            else:
                self.status_var.set(f"Hiba: {response.status_code}")
        except requests.RequestException as e:
            self.status_var.set(f"Hálózati hiba: {str(e)}")
    
    def process_report_data(self, data):
        return [common_param["rssi"] for common_param in data["common_param"]]
    
    def get_version(self):
        url = f"http://{self.stb_ip}/public?command=version"
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                self.status_var.set(f"Parancs elküldve: version")
                data = response.json()
                q = data.get("serial")
                self.version_labels["name"]["var"].set(data.get("stb_name"))
                self.version_labels["serial"]["var"].set(f'{q[0:4]}:{q[4:8]}:{q[8:12]}:{q[12:16]}')
                self.version_labels["stb"]["var"].set(data.get("version").get("stb"))
                self.get_satlist()
            else:
                self.status_var.set(f"Hiba: {response.status_code}")
        except requests.RequestException as e:
            self.status_var.set(f"Hálózati hiba: {str(e)}")
 
    def get_satlist(self):
        url = f"http://{self.stb_ip}/public?command=returnSATList"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                self.status_var.set(f"Parancs elküldve: returnTPList")
                data = response.json()
                self.sat_list = data["sat_list"]
                sat_names = []
                for sat in self.sat_list:
                    sat_names.append(f'{sat["sat_degree"]}{sat["direction"]} - {sat["sat_name"]}')
                self.spect_form_row["sat_list"].configure(values = sat_names)
                self.spect_form_row["sat_list"].set(sat_names[0])
                self.get_tplist(0)
            else:
                self.status_var.set(f"Hiba: {response.status_code}")
        except requests.RequestException as e:
            self.status_var.set(f"Hálózati hiba: {str(e)}")
    
    def get_tplist(self, sat_id):
        url = f"http://{self.stb_ip}/public?command=returnTPList&sat_id={sat_id}"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                self.status_var.set(f"Parancs elküldve: returnTPList")
                data = response.json()
                self.tp_list = data["tp_list"]
                tps = []
                for tp in self.tp_list:
                    tps.append(f'{tp["freq"]} - {"H" if tp["polarity"]==0 else "V" } - {tp["sr"]}')
                self.spect_form_row["tp_list"].configure(values = tps)
                self.spect_form_row["tp_list"].set(tps[0])
                self.get_reportlist()
            else:
                self.status_var.set(f"Hiba: {response.status_code}")
        except requests.RequestException as e:
            self.status_var.set(f"Hálózati hiba: {str(e)}")

    def make_new_report_name(self, name):
        return name.replace("_",".")[4:-7]
    
    def json_report_name(self, name):
        return name[:-4]

    def get_reportlist(self):
        url = f"http://{self.stb_ip}/mnt/flash/e/ls.json"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                self.status_var.set(f"Parancs elküldve: returnTPList")
                data = response.json()

                self.report_list = {self.make_new_report_name(report["name"]): self.json_report_name(report["name"]) for report in data["dir_list"]}
                new_keys = list(self.report_list.keys())

                self.spect_form_row["report_list"].configure(values=new_keys)
                self.spect_form_row["report_list"].set(new_keys[0])
                self.first_send_initSmartSNR()
            else:
                self.status_var.set(f"Hiba: {response.status_code}")
        except requests.RequestException as e:
            self.status_var.set(f"Hálózati hiba: {str(e)}")
    
    def first_send_initSmartSNR(self):
        tp = self.tp_list[0]
        sat = next(sat for sat in self.sat_list if sat["sat_id"] == tp["sat_id"])
        mid_freq = tp["freq"] - sat["lnb_low_freq"] if tp["freq"] < 11700 else tp["freq"] - sat["lnb_high_freq"]
        url = f"http://{self.stb_ip}/public?command=initSmartSNR&state=on&mode={self.mode}&freq={mid_freq}&sr=63000&pol={tp['polarity']}&tone={tp['tone']}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                self.status_var.set(f"Parancs elküldve: {self.mode} mód")
            else:
                self.status_var.set(f"Hiba: {response.status_code}")
        except requests.RequestException as e:
            self.status_var.set(f"Hálózati hiba: {str(e)}")

    def send_initSmartSNR(self):
        """Elküldi az initSmartSNR parancsot az STB-nek az aktuális mód és paraméterek alapján."""
        freq = self.snr_form_row["freq"].get()
        lo = self.snr_form_row["lo"].get()

        if not freq or freq == '':
            self.status_var.set("Hiba: Adj meg frekvenciát!")
            return
        else:
            freq_IF = float(freq) - float(lo)

        sr = self.snr_form_row["sr"].get()
        sr_value = 63000 if not sr or self.mode == 'spectrum' else sr

        pol = self.snr_form_row["pol"].get()
        pol_val = self.get_form_data_val(pol, SNR_FIELDS)
        
        tone = self.snr_form_row["tone"].get()
        tone_val = self.get_form_data_val(tone, SNR_FIELDS)
        
        diseqc_hex = self.snr_form_row["diseqc_hex"].get()
        diseqc_hex_val = self.get_form_data_val(diseqc_hex, SNR_FIELDS)

        smart_lnb_enabled = self.snr_form_row["smart_lnb_enabled"].get()
        smart_lnb_enabled_val = self.get_form_data_val(smart_lnb_enabled, SNR_FIELDS)

        logging.info(f"{self.mode} / freq_IF: {freq_IF}, lo: {lo}, sr: {sr_value}, pol: {pol_val}, tone: {tone_val}, diseqc_hex: {diseqc_hex_val}, smart_lnb: {smart_lnb_enabled_val}")
        
        url = f"http://{self.stb_ip}/public?command=initSmartSNR&state=on&mode={self.mode}&freq={freq_IF}&sr={sr_value}&pol={pol_val}&tone={tone_val}&diseqc_hex={diseqc_hex_val}"
        
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
        url = f"http://{self.stb_ip}/public?command=startEvents"
        
        try:
            self.event_source = SSEClient(url)
            for event in self.event_source:
                if not self.running:
                    break
                data = event.data
                self.after(0, self.process_sse_data, data)
        except Exception as e:
            self.after(0, self.status_var.set, f"SSE hiba: {str(e)}")
            self.restart_sse()

    def start_sse(self):
        self.event_thread = threading.Thread(target=self.listen_sse, daemon=True)
        self.event_thread.start()
    
    def restart_sse(self):
        """Újraindítja az SSE kapcsolatot egy új szálban."""
        self.event_close(2)  # Biztosítsuk, hogy az előző kapcsolat bezáródott
        self.running = True  # Újraindítás előtt engedélyezzük a futást
        self.event_thread = threading.Thread(target=self.listen_sse, daemon=True)
        self.event_thread.start()

    def event_close(self, sec=0):
        """ Lezárja az SSE kapcsolatot és visszaállítja az STB-t standard módba. """
        self.running = False  # SSE futás leállítása

        # SSE kapcsolat tényleges lezárása
        if self.event_source:
            try:
                self.event_source.close()  # Ha létezik close(), lezárjuk
            except AttributeError:
                pass  
        self.event_source = None  # SSE kapcsolat objektumának törlése

        # STB visszaállítása normál módba (commonEvent)
        url = f"http://{self.stb_ip}/public?command=commonEvent"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                self.status_var.set("STB visszaállítva standard módba")
            else:
                self.status_var.set(f"commonEvent hiba: {response.status_code}")
        except requests.RequestException as e:
            self.status_var.set(f"Hálózati hiba: {e}")

        # Szálkezelés: Biztosan beállítjuk, hogy ne legyen régi szál hivatkozás
        if self.event_thread:
            self.event_thread = None

        time.sleep(sec)  # Várunk, hogy az STB feldolgozza a bontást 

    def process_sse_data(self, data):
        """GUI frissítése az SSE események alapján."""
        try:
            parsed_data = json.loads(data)

            # Ha van "ret_code", frissítsük a status változót
            ret_code = parsed_data.get("ret_code")  # Ha nincs ilyen kulcs, None lesz
            if ret_code:  
                self.status_var.set(ret_code)  # Ha van értéke, akkor kiírjuk

            # SNR Scan status és lock állapot kiírása
            if parsed_data.get("tune_mode") == 0:
                scan_status = parsed_data.get("scan_status", "N/A")
                lock = "Locked" if parsed_data.get("lock") == 1 else "Not Locked"
                self.status_var.set(f"Status: {scan_status} | Lock: {lock}")
                self.box_top_labels["snr"]["var"].set(f'SNR: {parsed_data.get("snr", "N/A")} dB')
                self.box_top_labels["lm_snr"]["var"].set(f'LM SNR: {parsed_data.get("lm_snr", "N/A")} dB')
                self.box_top_labels["carrier_offset"]["var"].set(f'Carrier Offset: {parsed_data.get("carrier_offset", "N/A")} kHz')
                self.box_top_labels["lpg"]["var"].set(f'LPG: {parsed_data.get("lpg", "N/A")}')
                self.box_top_labels["lnb_current"]["var"].set(f'LNB Current: {parsed_data.get("lnb_current", "N/A")} mA')
                self.box_top_labels["lnb_voltage"]["var"].set(f'LNB Voltage: {parsed_data.get("lnb_voltage", "N/A")} mV')
                self.box_top_labels["psu_voltage"]["var"].set(f'PSU Voltage: {parsed_data.get("psu_voltage", "N/A")} mV')
                self.angles_labels["alfa"]["var"].set(f'Alfa: {parsed_data.get("alfa", "N/A")}')
                self.angles_labels["beta"]["var"].set(f'Beta: {parsed_data.get("beta", "N/A")}')
                self.angles_labels["gamma"]["var"].set(f'Gamma: {parsed_data.get("gamma", "N/A")}')

            # Spektrum adatok frissítése, ha "spectrum_array" létezik
            elif parsed_data.get("tune_mode") == 1:
                self.spectrum_data = parsed_data.get("spectrum_array", [])
                self.update_spectrum_chart(self.spectrum_data)
                self.angles_labels["alfa"]["var"].set(f'Alfa: {parsed_data.get("alfa", "N/A")}')
                self.angles_labels["beta"]["var"].set(f'Beta: {parsed_data.get("beta", "N/A")}')
                self.angles_labels["gamma"]["var"].set(f'Gamma: {parsed_data.get("gamma", "N/A")}')

            # Bind scan
            elif parsed_data.get("tune_mode") == 3:
                self.status_var.set("bind scan")

        except Exception:
            self.status_var.set("Connected")
            # Version indítása
            if not self.version_run:
                self.version_thread = threading.Thread(target=self.get_version, daemon=True)
                self.version_thread.start()
                self.version_run = True

    def toplevel_chart_update(self, window):
        """Folyamatosan frissíti a grafikont 1 másodpercenként új adatokkal"""
        def update():
            if window.winfo_exists():
                window.update_chart(self.report_data_rssi)
                window.after(10, update)  # 1 másodpercenként frissítés
        update()

    def update_spectrum_chart(self, spectrum_data):
        """Frissíti a matplotlib grafikont a kapott spektrum adatokkal."""
        x_values = list(range(len(spectrum_data)))  # 0-479 pont
        y_values = spectrum_data

        self.line.set_xdata(x_values)
        self.line.set_ydata(y_values)
        self.ax.relim()  # Újraértékeli a tengelyeket
        self.ax.autoscale_view()  # Automatikusan méretezi a grafikont

        self.canvas.draw()  # Frissíti a rajzot
        
    def on_close(self):
        if messagebox.askyesno("Kilépés", "Biztosan kilépsz?"):
            logging.info("GUI bezárása... SSE kapcsolat leállítása")
            plt.close('all')
            self.event_close()
            self.destroy()
        else:
            logging.info("Kilépés megszakítva")
    
    # ====== sse ==== end

    def long_progress(self):
        #Ez szimulál egy hosszabb ideig tartó műveletet.
        self.progressbar_1.start()  # ProgressBar elindítása
        time.sleep(5)  # Itt történne a valódi folyamat
        self.progressbar_1.stop()  # ProgressBar leállítása
        self.togle_pb()

    def start_progress(self): # command=self.start_progress
        self.togle_pb()
        #Egy új szálban indítja a hosszabb folyamatot, hogy a GUI ne fagyjon le.
        thread = threading.Thread(target=self.long_progress, daemon=True)
        thread.start()

    def open_toplevel(self, title, call):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self, title, call)  # Helyesen adjuk át a master-t
        else:
            self.toplevel_window.update_text(title)  # Ha létezik az ablak, fókuszáljunk rá
        self.toplevel_window.lift()

    def get_form_data_val(self, choice, fields):
        return  next(field["data"][choice] for field in fields if choice in list(field.get("data", {}).keys()))
    
    def create_form(self, parent, fields):
        entries = {}
        row_index = 0
        for field in fields:
            ctk.CTkLabel(parent, text=field["title"], anchor="w").grid(row=row_index, column=0, padx=10, pady=5, sticky="ew")
            row_index += 1 
            if field["type"] == "str":
                entry = ctk.CTkEntry(parent, validate='key', validatecommand=(self.vcmd, "%P"))
            elif field["type"] == "list":
                entry = ctk.CTkOptionMenu(parent, values=list(field.get("data").keys()))
            entry.grid(row=row_index, column=0, padx=5, pady=5, sticky="ew")
            entries[field["name"]] = entry
            row_index += 1
        return entries

    def snr_dsqch_on_select(self, choice): 
        # Ellenőrizzük, hogy az adott érték tiltott-e
        if not hasattr(self, "old_diseqc_value"):  # Ha még nincs, inicializáljuk
            self.old_diseqc_value = "Off"
        if choice.startswith("---"):
            self.snr_form_row["diseqc_hex"].set(self.old_diseqc_value)  # Ha tiltott, visszaállítjuk az előző értékre
        else:
            self.old_diseqc_value = choice  # Frissítjük a régi értéket, ha szabályos a választás

    def create_labels(self, parent, fields):
        labels = {}
        for i, field in enumerate(fields):
            var = ctk.StringVar()  # Minden mezőhöz külön StringVar kell!
            label = ctk.CTkLabel(parent, textvariable=var, anchor="w")  # Label létrehozása
            label.grid(row=i, column=0, padx=10, pady=5, sticky="ew")  # Grid külön hívva!
            labels[field] = {"label": label, "var": var}  # Tároljuk a Label és a StringVar párost
        return labels

    def validate_input(self, value):
        if value == "" or value.replace(".", "", 1).isdigit():
            return True
        return False

    def show_data(self, form):
        if form == "snr":
            data = {key: form_row.get() for key, form_row in self.snr_form_row.items()}
            text = "\n".join(f"{key}: {value}" for key, value in data.items())
            return text
        elif form == "spect":
            data = {key: form_row.get() for key, form_row in self.spect_form_row.items()}
            text = "\n".join(f"{key}: {value}" for key, value in data.items())
            return text

    def open_input_dialog_event(self, option_menu):
        selected_value = option_menu.get()
        dialog_text = f"Selected Value: {selected_value}"
        dialog = ctk.CTkInputDialog(text=dialog_text, title="Input Dialog")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def togle_pb(self):
        if self.progressbar_frame.winfo_ismapped():
            self.progressbar_frame.grid_forget()
        else:
            self.progressbar_frame.grid(row=0, column=1, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")

    # ====== scroll mouse snr form ====== 
    
    def bind_scroll(self, event):
        """Bekapcsolja az egérgörgős görgetést az aktív ScrollableFrame-re."""
        if platform.system() == "Linux":
            self.snr_form_frame._parent_canvas.bind_all("<Button-4>", self.on_mouse_wheel_linux)
            self.snr_form_frame._parent_canvas.bind_all("<Button-5>", self.on_mouse_wheel_linux)
        else:
            self.snr_form_frame._parent_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel_windows)

    def unbind_scroll(self, event):
        """Kikapcsolja az egérgörgős görgetést, ha az egér elhagyja a ScrollableFrame-et."""
        if platform.system() == "Linux":
            self.snr_form_frame._parent_canvas.unbind_all("<Button-4>")
            self.snr_form_frame._parent_canvas.unbind_all("<Button-5>")
        else:
            self.snr_form_frame._parent_canvas.unbind_all("<MouseWheel>")

    def on_mouse_wheel_windows(self, event):
        """Windows és macOS görgetési logika"""
        self.snr_form_frame._parent_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def on_mouse_wheel_linux(self, event):
        """Linux görgetési logika"""
        if event.num == 4:
            self.snr_form_frame._parent_canvas.yview_scroll(-1, "units")  # Felfelé görgetés
        elif event.num == 5:
            self.snr_form_frame._parent_canvas.yview_scroll(1, "units")  # Lefelé görgetés

if __name__ == "__main__":
    app = RamfApp()
    app.withdraw()  # A főablak elrejtése

    try:
        ip = load_settings_ip()
        if not ip or not network_check(ip):
            ip = ask_for_ip()
    except Exception as e:
        logging.warning(f"Hiba történt az IP betöltésnél vagy ellenőrzésnél: {e}")
        ip = ask_for_ip()

    if ip:
        app.stb_ip = ip
        app.deiconify()  # Ha sikerült, megjelenítjük a főablakot
        logging.info(f"Sikeres kapcsolat az IP-hez: {ip}")
        app.start_sse()
        app.mainloop()
    else:
        logging.info("Kilépés...")
    