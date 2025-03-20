import requests
import threading
import tkinter as tk
import customtkinter as ctk
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sseclient import SSEClient
import datetime
import time
import platform

STB_IP = "192.168.1.4"  # Állítsd be a megfelelő IP címet

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
        'name': 'sr',
        'title': 'Symbol rate:',
        'type': 'str'
    },{
        'name': 'pol',
        'title': 'Polarization:',
        'type': 'list',
        'data': ["Horizontal", "Vertical"]
    },{
        'name': 'tone',
        'title': 'Tone:',
        'type': 'list',
        'data': ["Off", "On"]
    },{
        'name': 'diseqc_hex',
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
        'name': 'smart_lnb_enabled',
        'title': '3D converter polling:',
        'type': 'list',
        'data': ["Disabled", "Enabled"]
    }
]

SPECT_FIELDS = [
    {
        'name': 'sat_list',
        'title': 'Satellite List:',
        'type': 'list',
        'data': []
    },{
        'name': 'tp_list',
        'title': 'TP List:',
        'type': 'list',
        'data': []
    },{
        'name': 'report_list',
        'title': 'Report List:',
        'type': 'list',
        'data': []
    }
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

        self.tp_list = []
        self.sat_list = []
        self.version_run = False
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
        sidebar_bottom_row_index = 7
        
        self.sidebar_frame = ctk.CTkFrame(self, width=100, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure((sidebar_bottom_row_index), weight=1)
        
        # stb ip
        self.sidebar_stbip_label = ctk.CTkLabel(self.sidebar_frame, text="STB IP:", anchor="w")
        self.sidebar_stbip_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.sidebar_stbip_entry = ctk.CTkEntry(self.sidebar_frame)
        self.sidebar_stbip_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # version labels
        self.sidebar_label_version_var = ctk.StringVar()
        self.sidebar_label_version = ctk.CTkLabel(self.sidebar_frame, textvariable=self.sidebar_label_version_var, font=ctk.CTkFont(size=10, weight="bold"), anchor="w")
        self.sidebar_label_version.grid(row=2, column=0, padx=20, pady=10)

        self.f_text_var = ctk.StringVar()
        self.sidebar_f_text = ctk.CTkLabel(master=self.sidebar_frame, textvariable=self.f_text_var)
        self.sidebar_f_text.grid(row=3, column=0)

        # buttons top
        self.sidebar_button_propert = ctk.CTkButton(self.sidebar_frame, text="Properties", command=self.start_progress)
        self.sidebar_button_propert.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_toggle = ctk.CTkButton(self.sidebar_frame, text="Toggle pb", command=self.togle_pb)
        self.sidebar_button_toggle.grid(row=5, column=0, padx=20, pady=10)
        self.sidebar_button_exit = ctk.CTkButton(self.sidebar_frame, text="Exit", command=self.quit)
        self.sidebar_button_exit.grid(row=6, column=0, padx=20, pady=10)

        # buttons bottom
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=sidebar_bottom_row_index+1, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=sidebar_bottom_row_index+2, column=0, padx=20, pady=(10, 10))
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=sidebar_bottom_row_index+3, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%", "150%"], command=self.change_scaling_event)
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
        
        # --- create box bottom
        self.box_bottom = ctk.CTkFrame(self, width=250)
        self.box_bottom.grid(row=2, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # Matplotlib ábra létrehozása
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.ax.set_title("Spektrum Analízis")
        self.ax.set_xlabel("Frekvencia pontok")
        self.ax.set_ylabel("Jelszint (dB)")
        self.line, = self.ax.plot([], [], "b-", lw=1)

        # Matplotlib integrálása a Tkinter ablakba
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.box_bottom)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        
        #self.box_bottom.bind("<Configure>", self.resize_bottom_plot)

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

    # ====== SSE ====== start
        
    def sat_list_changed(self, elem):
        """ Handle the satellite list changed event """
        try:
            sat_id = next(sat["sat_id"] for sat in self.sat_list if sat["sat_name"] == elem)
            self.f_text_var.set(sat_id)
            self.get_tplist(sat_id)
        except StopIteration as err:
            self.f_text_var.set(f"Error: {err}")
    
    def get_version(self):
        url = f"http://{STB_IP}/public?command=version"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                self.status_var.set(f"Parancs elküldve: version")
                data = response.json()
                q = data["serial"]
                self.sidebar_label_version_var.set(f'STB nane - {data["stb_name"]}\nSerial - {q[0:4]}:{q[4:8]}:{q[8:12]}:{q[12:16]}\nSTB - {data["version"]["stb"]}\nWebApi - {data["version"]["web_api"]}')
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
                self.f_text_var.set(data["sat_num"])
                self.sat_list = data["sat_list"]
                sat_names = []
                for sat in self.sat_list:
                    sat_names.append(sat["sat_name"])
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

        if not sr:
            sr = "63000"  # Spectrum módhoz fix érték

        pol = self.snr_form_row["pol"].get()

        tone = self.snr_form_row["tone"].get()

        diseqc_hex = self.snr_form_row["diseqc_hex"].get()

        smart_lnb_enabled = self.snr_form_row["smart_lnb_enabled"].get()

        url = f"http://{STB_IP}/public?command=initSmartSNR&state=on&mode={self.mode}&freq={freq_IF}&sr={sr}&pol={pol}&tone={tone}&diseqc_hex={diseqc_hex}"
        
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

            # SNR Scan status és lock állapot kiírása
            if parsed_data["tune_mode"] == 0:
                scan_status = parsed_data.get("scan_status", "N/A")
                lock = "Locked" if parsed_data.get("lock") == 1 else "Not Locked"
                self.status_var.set(f"Status: {scan_status} | Lock: {lock}")
            
            # Spektrum adatok frissítése, ha "spectrum_array" létezik
            if parsed_data["tune_mode"] == 1:
                spectrum_data = parsed_data["spectrum_array"]
                self.update_spectrum_chart(spectrum_data)
            
            # bind scan
            if parsed_data["tune_mode"] == 3:
                self.status_var.set("bindscan")
            
        except Exception:
            self.status_var.set("Connected")
            # version indítása
            if not self.version_run:
                self.version_thread = threading.Thread(target=self.get_version, daemon=True)
                self.version_thread.start()
                self.version_run = True
    
    def update_spectrum_chart(self, spectrum_data):
        """Frissíti a matplotlib grafikont a kapott spektrum adatokkal."""
        x_values = list(range(len(spectrum_data)))  # 0-479 pont
        y_values = spectrum_data

        self.line.set_xdata(x_values)
        self.line.set_ydata(y_values)
        self.ax.relim()  # Újraértékeli a tengelyeket
        self.ax.autoscale_view()  # Automatikusan méretezi a grafikont

        self.canvas.draw()  # Frissíti a rajzot

    def resize_bottom_plot(self, event):
        """Frissíti a Matplotlib ábra méretét a CTkFrame méretéhez igazítva"""
        new_width = self.box_bottom.winfo_width() / 100  # Inchbe konvertálás
        new_height = self.box_bottom.winfo_height() / 100

        self.fig.set_size_inches(new_width, new_height, forward=True)  # Új méret beállítása
        self.canvas.draw_idle()  # Frissítés
    
    # ====== sse ==== end
    
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
                entry = ctk.CTkOptionMenu(parent, values=field["data"])
            entry.grid(row=row_index, column=0, padx=5, pady=5, sticky="ew")
            entries[field["name"]] = entry
            row_index += 1
        return entries

    def validate_input(self, value):
        if value == "" or value.replace(".", "", 1).isdigit():
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
    