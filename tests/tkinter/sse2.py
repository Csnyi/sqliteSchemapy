import httpx
import json
import asyncio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sqlite3
import requests
import time
import threading
import queue

# STB API végpontok
STB_IP = "192.168.1.5"
BASE_URL = f"http://{STB_IP}/public"
INIT_URL = f"{BASE_URL}?command=initSmartSNR&state=on&mode=snr&freq=1333&sr=22300&pol=1"
SSE_URL = f"{BASE_URL}?command=startEvents"

# Adatbázis inicializálása
DB_FILE = "sse_data.db"

def init_db():
    """Létrehozza az SQLite adatbázist és a táblát, ha még nem létezik."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sse_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                snr REAL,
                lm_snr REAL,
                lnb_voltage REAL,
                psu_voltage REAL
            )
        """)
        conn.commit()

def store_data(snr, lm_snr, lnb_voltage, psu_voltage):
    """Elmenti az adatokat az SQLite adatbázisba."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sse_events (snr, lm_snr, lnb_voltage, psu_voltage) 
            VALUES (?, ?, ?, ?)
        """, (snr, lm_snr, lnb_voltage, psu_voltage))
        conn.commit()

def cleanup_db():
    """Törli a 24 óránál régebbi adatokat az adatbázisból."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM sse_events WHERE timestamp < datetime('now', '-1 day')
        """)
        conn.commit()

def db_maintenance():
    """Óránként lefutó tisztító folyamat, amely törli a régi adatokat."""
    while True:
        cleanup_db()
        time.sleep(3600)  # 1 óránként fut

maintenance_thread = threading.Thread(target=db_maintenance, daemon=True)
maintenance_thread.start()

# Adatok tárolására szolgáló sorok
snr_queue = asyncio.Queue()
voltage_queue = asyncio.Queue()

def init_snr():
    """Elküldi az inicializáló parancsot az STB-nek."""
    try:
        response = requests.get(INIT_URL, timeout=5)
        if response.status_code == 200:
            print("Sikeres inicializálás:", response.text)
        else:
            print("Hiba az inicializáláskor:", response.status_code)
    except requests.RequestException as e:
        print("Hálózati hiba az inicializálás során:", e)

async def sse_listener():
    """Aszinkron SSE figyelő"""
    while True:
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", SSE_URL, timeout=10) as response:
                    if response.status_code != 200:
                        print(f"Hibás HTTP státusz: {response.status_code}")
                        await asyncio.sleep(5)
                        continue  

                    print("Sikeres SSE kapcsolat.")

                    async for line in response.aiter_lines():
                        if line:
                            decoded_line = line.decode("utf-8").strip()
                            if decoded_line.startswith("data: "):
                                json_data = decoded_line[6:]
                                try:
                                    parsed_data = json.loads(json_data)

                                    # SNR és feszültségértékek kinyerése
                                    snr = float(parsed_data.get("snr", 0.0))
                                    lm_snr = float(parsed_data.get("lm_snr", 0.0))
                                    lnb_voltage = float(parsed_data.get("lnb_voltage", 0.0))
                                    psu_voltage = float(parsed_data.get("psu_voltage", 0.0))

                                    # SQLite mentés
                                    current_time = int(time.time())
                                    if current_time > last_time:
                                        store_data(snr, lm_snr, lnb_voltage, psu_voltage)
                                        last_time = current_time

                                    # Adatok átadása a grafikonhoz
                                    snr_queue.put((snr, lm_snr))
                                    voltage_queue.put((lnb_voltage, psu_voltage))

                                except json.JSONDecodeError:
                                    print("Hibás JSON:", json_data)

        except (httpx.RequestError, httpx.TimeoutException) as e:
            print(f"Hálózati hiba: {e}, újracsatlakozás 5 másodperc múlva...")
            await asyncio.sleep(5)

# Inicializáló parancs elküldése
init_db()
init_snr()

# === GRAFIKONOK FELTÖLTÉSE AZ ADATBÁZISBÓL ===
def load_data():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, snr, lm_snr, lnb_voltage, psu_voltage 
            FROM sse_events
            ORDER BY timestamp DESC
            LIMIT 200  -- Csak az utolsó 200 adatpontot kérjük
        """)
        return cursor.fetchall()[::-1]  # Fordított sorrendben adjuk vissza

# === GRAFIKON FRISSÍTÉS ===
x_data, y_data = [], []

def update_plot(frame):
    """Matplotlib animációs frissítés az SQLite adatok alapján."""
    data = load_data()
    if not data:
        return

    global ax1, ax2

    timestamps, snr_values, lm_snr_values, lnb_voltages, psu_voltages = zip(*data)

    ax1.clear()
    ax1.plot(timestamps, snr_values, marker="o", linestyle="-", color="b", label="SNR")
    ax1.plot(timestamps, lm_snr_values, marker="s", linestyle="-", color="r", label="LM SNR")
    ax1.set_title("SNR és LM SNR változás")
    ax1.set_xlabel("Idő")
    ax1.set_ylabel("dB")
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)

    ax2.clear()
    ax2.plot(timestamps, lnb_voltages, marker="o", linestyle="-", color="g", label="LNB Voltage")
    ax2.plot(timestamps, psu_voltages, marker="s", linestyle="-", color="m", label="PSU Voltage")
    ax2.set_title("LNB és PSU feszültség változás")
    ax2.set_xlabel("Idő")
    ax2.set_ylabel("Voltage")
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)

async def main():
    """Async fő program"""
    task = asyncio.create_task(sse_listener())

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    ani = animation.FuncAnimation(fig, update_plot, interval=1000)
    plt.show()

    await task

asyncio.run(main())
