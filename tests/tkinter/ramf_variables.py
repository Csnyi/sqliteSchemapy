
appWidth, appHeight = 960, 540

def wpos_center(window_width, window_height, root):
    """Kiszámolja az ablak középre helyezéséhez szükséges koordinátákat."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    pos_x = (screen_width // 2) - (window_width // 2)
    pos_y = (screen_height // 2) - (window_height // 2)
    return f"{window_width}x{window_height}+{pos_x}+{pos_y}"


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

VER_LABELS_FIELDS = [
    "name",
    "serial",
    "stb"
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

SCALING_VALUES = ["80%", "90%", "100%", "110%", "120%", "150%"]
