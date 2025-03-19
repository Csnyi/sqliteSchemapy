import tkinter as tk
import requests
from sseclient import SSEClient
import threading

class SSEApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SSE Client GUI")

        self.label = tk.Label(root, text="Várakozás az adatokra...")
        self.label.pack(pady=20)

        self.start_button = tk.Button(root, text="Indítás", command=self.start_sse)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Leállítás", command=self.stop_sse, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.event_source = None
        self.running = False

        # GUI bezárás eseménykezelő
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_sse(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        threading.Thread(target=self.sse_listener, daemon=True).start()

    def sse_listener(self):
        url = "http://192.168.1.4/public?command=startEvents"
        try:
            self.event_source = SSEClient(url)
            for event in self.event_source:
                if not self.running:
                    break
                self.label.config(text=f"Kapott adat: {event.data}")
        except Exception as e:
            print("Hiba az SSE kapcsolatban:", e)

    def stop_sse(self):
        self.running = False
        self.event_source = None
        self.label.config(text="Kapcsolat leállítva")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def on_close(self):
        print("GUI bezárása... SSE kapcsolat leállítása")
        self.stop_sse()
        self.root.destroy()  # Ablak bezárása

# Indítás
root = tk.Tk()
app = SSEApp(root)
root.mainloop()
