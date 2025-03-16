import customtkinter as ctk
import platform

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Scrollable Frame with Mouse Scroll")
        self.geometry("400x400")

        # Görgethető frame létrehozása
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=300, height=300)
        self.scrollable_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Több címke hozzáadása a görgethető frame-hez
        for i in range(20):
            ctk.CTkLabel(self.scrollable_frame, text=f"Item {i+1}").pack(pady=5)

        # Egér görgetés hozzárendelése a megfelelő eseményekhez
        self.scrollable_frame.bind("<Enter>", self.bind_scroll)
        self.scrollable_frame.bind("<Leave>", self.unbind_scroll)

    def bind_scroll(self, event):
        """Bekapcsolja az egérgörgős görgetést az aktív ScrollableFrame-re."""
        if platform.system() == "Linux":
            self.scrollable_frame._parent_canvas.bind_all("<Button-4>", self.on_mouse_wheel_linux)
            self.scrollable_frame._parent_canvas.bind_all("<Button-5>", self.on_mouse_wheel_linux)
        else:
            self.scrollable_frame._parent_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel_windows)

    def unbind_scroll(self, event):
        """Kikapcsolja az egérgörgős görgetést, ha az egér elhagyja a ScrollableFrame-et."""
        if platform.system() == "Linux":
            self.scrollable_frame._parent_canvas.unbind_all("<Button-4>")
            self.scrollable_frame._parent_canvas.unbind_all("<Button-5>")
        else:
            self.scrollable_frame._parent_canvas.unbind_all("<MouseWheel>")

    def on_mouse_wheel_windows(self, event):
        """Windows és macOS görgetési logika"""
        self.scrollable_frame._parent_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def on_mouse_wheel_linux(self, event):
        """Linux görgetési logika"""
        if event.num == 4:
            self.scrollable_frame._parent_canvas.yview_scroll(-1, "units")  # Felfelé görgetés
        elif event.num == 5:
            self.scrollable_frame._parent_canvas.yview_scroll(1, "units")  # Lefelé görgetés

# Alkalmazás indítása
app = App()
app.mainloop()

