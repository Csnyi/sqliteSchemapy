import requests
import threading
import tkinter as tk
import customtkinter as ctk
import json
from sseclient import SSEClient
import datetime
import time
import platform

STB_IP = "192.168.1.2"  # Állítsd be a megfelelő IP címet

# ctk
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("tkthemes/breeze.json")  # Themes: "blue" (standard), "green", "dark-blue"
#ctk.set_widget_scaling(1.5)

appWidth, appHeight, pozx, pozy = 960, 540, 100, 100

SNR_FIELDS = [
    {
        'name': 'freq',
        'title': 'Frequency:',
        'type': 'str'
    },{
        'name': 'lo',
        'title': 'Local Oscillator:',
        'type': 'list',
        'data': {
            "5150": 5150, 
            "5750": 5750, 
            "5950": 5950, 
            "9750": 9750, 
            "10000": 10000, 
            "10050": 10050, 
            "10450": 10450, 
            "10600": 10600, 
            "10700": 10700, 
            "10750": 10750, 
            "11250": 11250, 
            "11300": 11300
        }
    },{
        'name': 'sr',
        'title': 'Symbol rate:',
        'type': 'str'
    },{
        'name': 'pol',
        'title': 'Polarization:',
        'type': 'list',
        'data': {"Horizontal": 0, "Vertical": 1}
    },{
        'name': 'tone',
        'title': 'Tone:',
        'type': 'list',
        'data': {"Off": 0, "On": 1}
    },{
        'name': 'diseqc_hex',
        'title': 'DISEqC Port - Command:',
        'type': 'list',
        'data': {
            "Off": "",
            "--- 1.0, up to 4 ports ---": "",
            "01 - E01038F0": "E01038F0",
            "02 - E01038F4": "E01038F4",
            "03 - E01038F8": "E01038F8",
            "04 - E01038FC": "E01038FC",
            "--- 1.1, up to 16 ports ---": "",
            "--- UNCOMMITTED ---": "",
            "01 - E01039F0": "E01039F0",
            "02 - E01039F1": "E01039F1",
            "03 - E01039F2": "E01039F2",
            "04 - E01039F3": "E01039F3",
            "05 - E01039F4": "E01039F4",
            "06 - E01039F5": "E01039F5",
            "07 - E01039F6": "E01039F6",
            "08 - E01039F7": "E01039F7",
            "--- COMMITTED ---": "",
            "09 - E01039F8": "E01039F8",
            "10 - E01039F9": "E01039F9",
            "11 - E01039FA": "E01039FA",
            "12 - E01039FB": "E01039FB",
            "13 - E01039FC": "E01039FC",
            "14 - E01039FD": "E01039FD",
            "15 - E01039FE": "E01039FE",
            "16 - E01039FF": "E01039FF"
        }
    },{
        'name': 'smart_lnb_enabled',
        'title': '3D converter polling:',
        'type': 'list',
        'data': {"Disabled": 0, "Enabled": 1}
    }
]

SPECT_FIELDS = [
    {
        'name': 'sat_list',
        'title': 'Satellite List:',
        'type': 'list',
        'data': {}
    },{
        'name': 'tp_list',
        'title': 'TP List:',
        'type': 'list',
        'data': {}
    },{
        'name': 'report_list',
        'title': 'Report List:',
        'type': 'list',
        'data': {}
    }
]

STBIP_FIELDS = [
    {
        'name': 'stb_ip',
        'title': 'STB IP:',
        'type': 'str'
    }
]

SNR_LABELS_FIELDS = [
    "snr",
    "lm_snr",
    "carrier_offset",
    "lpg",
    "lnb_current",
    "lnb_voltage",
    "psu_voltage"
]

SPECT_LABELS_FIELDS = [
    "alfa",
    "beta",
    "gamma"
]

scaling_values = ["80%", "90%", "100%", "110%", "120%", "150%"]

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, master, info, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Sent data")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 300
        window_height = 300

        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        
        self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        self.label = ctk.CTkLabel(self, text=info, justify="left")
        self.label.pack(padx=20, pady=20, fill="both", expand=True)

        self.button = ctk.CTkButton(self, text="Ok", command=self.destroy)
        self.button.pack(padx=20, pady=20)

    def update_text(self, new_text):
        """Szöveg frissítése az ablakban"""
        self.label.configure(text=new_text)

class RamfApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- configure window
        self.title("R.A.M.F. Report")
        self.geometry(f"{appWidth}x{appHeight}+{pozx}+{pozy}")

        self.tp_list = None
        self.sat_list = []
        self.version_run = False
        self.event_source = None
        self.event_thread = None
        self.canvas_thread = None
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
        
        self.sidebar_frame = ctk.CTkFrame(self, width=100, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure((sidebar_bottom_row_index), weight=1)
        
        # stb ip frame
        self.sidebar_stbip_frame = ctk.CTkFrame(self.sidebar_frame)
        self.sidebar_stbip_frame.grid(row=0, column=0, sticky="nsew")
        
        self.sidebar_stbip_form = self.create_form(self.sidebar_stbip_frame, STBIP_FIELDS)
        
        # version labels
        self.sidebar_label_version_var = ctk.StringVar()
        self.sidebar_label_version = ctk.CTkLabel(self.sidebar_frame, textvariable=self.sidebar_label_version_var, font=ctk.CTkFont(size=10, weight="bold"), anchor="w")
        self.sidebar_label_version.grid(row=1, column=0, padx=20, pady=10)

        # buttons top
        self.sidebar_button_propert = ctk.CTkButton(self.sidebar_frame, text="Properties", command=self.start_progress)
        self.sidebar_button_propert.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_toggle = ctk.CTkButton(self.sidebar_frame, text="Toggle pb", command=self.togle_pb)
        self.sidebar_button_toggle.grid(row=5, column=0, padx=20, pady=10)
        self.sidebar_button_exit = ctk.CTkButton(self.sidebar_frame, text="Exit", command=self.quit)
        self.sidebar_button_exit.grid(row=6, column=0, padx=20, pady=10)

        # angles lables
        self.ang_lab_frame = ctk.CTkFrame(self.sidebar_frame)
        self.ang_lab_frame.grid(row=7, column=0, sticky="nsew")
        self.angles_labels = self.create_labels(self.ang_lab_frame, SPECT_LABELS_FIELDS)
        
        # buttons bottom
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=sidebar_bottom_row_index+1, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=sidebar_bottom_row_index+2, column=0, padx=20, pady=(10, 10))
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=sidebar_bottom_row_index+3, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=scaling_values, command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=sidebar_bottom_row_index+4, column=0, padx=20, pady=(10, 20))
        
        # --- create main bottom label (info row)
        self.info_frame = ctk.CTkFrame(self, corner_radius=0)
        self.info_frame.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.status_var = tk.StringVar(value="Kapcsolódás...")
        self.status_label = ctk.CTkLabel(master=self.info_frame, textvariable=self.status_var, font=("Arial", 16), anchor="w")
        self.status_label.grid(row=0, column=0, padx=10, pady=5)

        # --- create box top
        self.box_top = ctk.CTkScrollableFrame(self)
        self.box_top.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # box top labels
        self.box_top_labels = self.create_labels(self.box_top, SNR_LABELS_FIELDS)
        
        # --- create box bottom
        self.box_bottom = ctk.CTkTextbox(self)
        self.box_bottom.grid(row=2, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # --- create tabview
        self.tabview = ctk.CTkTabview(self, width=100)
        self.tabview.grid(row=1, column=2, rowspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Spectrum Report")
        self.tabview.tab("Spectrum Report").grid_columnconfigure(0, weight=1)
        self.tabview.add("SNR Report")
        self.tabview.tab("SNR Report").grid_rowconfigure((0,2), weight=0)
        self.tabview.tab("SNR Report").grid_rowconfigure(1, weight=1)

        ## Spectrum Report Form
        #Spect label
        self.spect_form_label = ctk.CTkLabel(self.tabview.tab("Spectrum Report"), text="Spectrum Form")
        self.spect_form_label.grid(row=0, column=0)

        # spect form frame
        self.spect_form_frame = ctk.CTkFrame(self.tabview.tab("Spectrum Report"), border_width=0)
        self.spect_form_frame.grid(row=1, column=0, sticky="nsew")

        self.spect_form_row = self.create_form(self.spect_form_frame, SPECT_FIELDS)
        self.spect_form_row["sat_list"].configure(command=self.sat_list_changed)
        self.spect_form_row["tp_list"].configure(command=self.tp_list_changed)
        
        # Spect Button
        self.spect_button_create_report = ctk.CTkButton(self.tabview.tab("Spectrum Report"), text="Create Report", command=lambda: self.open_input_dialog_event(self.spect_form_row["sat_list"]))
        self.spect_button_create_report.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.spect_button_open_report = ctk.CTkButton(self.tabview.tab("Spectrum Report"), text="Open Report", command=lambda: self.open_toplevel("spect"))
        self.spect_button_open_report.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")
        
        ## SNR Report Form

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

        # --- SSE események figyelésének indítása
        self.event_thread = threading.Thread(target=self.listen_sse, daemon=True)
        self.event_thread.start()

        #self.change_mode(self.mode)

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
        """ Handle the satellite list changed event """
        try:
            freq = int(elem.split(" - ")[0])
            tp = next(tp for tp in self.tp_list if tp["freq"] == freq)
            
            url = f"http://{STB_IP}/public?command=initSmartSNR&state=on&mode={self.mode}&freq={tp['freq']}&sr=63000&pol={tp['polarity']}&tone={tp['tone']}"
        
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
    
    def get_version(self):
        url = f"http://{STB_IP}/public?command=version"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                self.status_var.set(f"Parancs elküldve: version")
                data = response.json()
                q = data["serial"]
                self.sidebar_label_version_var.set(f'{data["stb_name"]}\n{q[0:4]}:{q[4:8]}:{q[8:12]}:{q[12:16]}\n{data["version"]["stb"]}\n')
                self.get_satlist()
            else:
                self.status_var.set(f"Hiba: {response.status_code}")
        except requests.RequestException as e:
            self.status_var.set(f"Hálózati hiba: {str(e)}")
 
    def get_satlist(self):
        url = f"http://{STB_IP}/public?command=returnSATList"
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
        url = f"http://{STB_IP}/public?command=returnTPList&sat_id={sat_id}"
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
                self.first_send_initSmartSNR()
            else:
                self.status_var.set(f"Hiba: {response.status_code}")
        except requests.RequestException as e:
            self.status_var.set(f"Hálózati hiba: {str(e)}")
    
    def first_send_initSmartSNR(self):
        tp = self.tp_list[0]
        sat = next(sat for sat in self.sat_list if sat["sat_id"] == tp["sat_id"])
        mid_freq = tp["freq"] - sat["lnb_low_freq"] if tp["freq"] < 11700 else tp["freq"] - sat["lnb_high_freq"]
        url = f"http://{STB_IP}/public?command=initSmartSNR&state=on&mode={self.mode}&freq={mid_freq}&sr=63000&pol={tp['polarity']}&tone={tp['tone']}"
        #url = f"http://{STB_IP}/public?command=initSmartSNR&state=on&mode={self.mode}&freq={tp['freq']}&sr=63000&pol={tp['polarity']}&tone={tp['tone']}"
        
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

        self.box_bottom.insert("0.0", f"{freq_IF, lo, sr, pol_val, tone_val, diseqc_hex_val, smart_lnb_enabled_val}")
        
        url = f"http://{STB_IP}/public?command=initSmartSNR&state=on&mode={self.mode}&freq={freq_IF}&sr={sr_value}&pol={pol_val}&tone={tone_val}&diseqc_hex={diseqc_hex_val}"
        
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
        """if self.mode == "spectrum":
            self.box_top.grid_forget()
            self.box_bottom.grid(row=1, column=1, rowspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        elif self.mode == "snr":
            self.box_bottom.grid_forget()
            self.box_top.grid(row=1, column=1, rowspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        """
        
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
            self.event_source = None
            # Várunk 2 másodpercet, majd újra próbálkozunk
            time.sleep(2)  
            self.restart_sse()

    def restart_sse(self):
        """Újraindítja az SSE kapcsolatot egy új szálban."""
        if not self.running:
            return  # Ha a programot leállítottuk, ne próbáljuk újra
        self.event_thread = threading.Thread(target=self.listen_sse, daemon=True)
        self.event_thread.start()
    
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
                spectrum_data = parsed_data.get("spectrum_array", [])
                self.box_bottom.delete("0.0", "end")
                self.box_bottom.insert("0.0", spectrum_data)
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

                
    # ====== sse ==== end
    
    def get_form_data_val(self, choice, fields):
        return  next(field["data"][choice] for field in fields if choice in list(field.get("data", {}).keys()))
    
    def long_progress(self):
        #Ez szimulál egy hosszabb ideig tartó műveletet.
        self.progressbar_1.start()  # ProgressBar elindítása
        time.sleep(5)  # Itt történne a valódi folyamat
        self.progressbar_1.stop()  # ProgressBar leállítása
        self.togle_pb()

    def start_progress(self):
        self.togle_pb()
        #Egy új szálban indítja a hosszabb folyamatot, hogy a GUI ne fagyjon le.
        thread = threading.Thread(target=self.long_progress, daemon=True)
        thread.start()

    def open_toplevel(self, form):
        if form == "snr":
            info_text = self.show_data(form)
        elif form == "spect":
            info_text = self.show_data(form)
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self, info_text)  # Helyesen adjuk át a master-t
        else:
            self.toplevel_window.update_text(info_text)  # Ha létezik az ablak, fókuszáljunk rá
        self.toplevel_window.lift()

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

    def create_labels(self, parent, fields):
        labels = {}
        for i, field in enumerate(fields):
            var = ctk.StringVar()  # Minden mezőhöz külön StringVar kell!
            label = ctk.CTkLabel(parent, textvariable=var, anchor="w")  # Label létrehozása
            label.grid(row=i, column=0, padx=10, sticky="ew")  # Grid külön hívva!
            labels[field] = {"label": label, "var": var}  # Tároljuk a Label és a StringVar párost
        return labels

    def validate_input(self, value):
        if value == "" or value.replace(".", "", 3).isdigit():
            return True
        return False

    def snr_dsqch_on_select(self, choice):
        # Ellenőrizzük, hogy az adott érték tiltott-e
        if not hasattr(self, "old_diseqc_value"):  # Ha még nincs, inicializáljuk
            self.old_diseqc_value = "Off"
        if choice.startswith("---"):
            self.snr_form_row["diseqc_hex"].set(self.old_diseqc_value)  # Ha tiltott, visszaállítjuk az előző értékre
        else:
            self.old_diseqc_value = choice  # Frissítjük a régi értéket, ha szabályos a választás

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
    app.mainloop()
    