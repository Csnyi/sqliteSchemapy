from dbschema import *
import datetime
import json
import tkinter as tk
import customtkinter as ctk

db = Database("stream.db")
table = Table(db, "data")

with open("SnrReport.json", "r") as file:
    data_stream = json.load(file)

def insert_stream():
    json_col=[]
    for add in data_stream:
        json_col.append({"json": json.dumps(add)})
    add_many(table, json_col)

def view_data():
    rows = table.fetch_all()
    data=[]
    for row in rows:
        json_text  = row["json"]
        data.append(json.loads(json_text))
        
    plate =[["lock", "snr", "lm snr", "timestamp"]]
    platerows = [[row["lock"], row["snr"], row["lm_snr"], datetime.datetime.fromtimestamp(row["timestamp"] / 1000.0)] for row in data]
    """ plate = [[row for row in data[0]]]
    platerows = [[v for v in row.values()] for row in data] """
    plate.extend(platerows)
    return tabulate(plate, headers="firstrow")

#insert_stream()
#print(view_data())
#list_data(table)
#empty_table(table)

# Main Window Properties
'''
window = tk.Tk()
window.title("Tkinter")
window.geometry("800x500")
window.configure(bg="#62a0ea")

textbox = ctk.CTkTextbox(window, text_color="#ffffff", height=600, width=600, bg_color="#62a0ea", fg_color="#62a0ea",)
#textbox.place(x=320, y=10)
textbox.pack(fill="both", expand=True, padx=10, pady=10)

# Szöveg hozzáadása
long_text = view_data()
textbox.insert("1.0", long_text)
textbox.configure(state="disabled")

Label_id3 = ctk.CTkLabel(
    master=window,
    text=view_data(),
    font=("Arial", 14),
    text_color="#000000",
    height=480,
    width=480,
    corner_radius=0,
    bg_color="#62a0ea",
    fg_color="#62a0ea",
    )
Label_id3.place(x=320, y=10)
Entry_id2 = ctk.CTkEntry(
    master=window,
    placeholder_text="Placeholder",
    placeholder_text_color="#454545",
    font=("Arial", 14),
    text_color="#000000",
    height=30,
    width=195,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#62a0ea",
    fg_color="#F0F0F0",
    )
Entry_id2.place(x=60, y=90)
Button_id1 = ctk.CTkButton(
    master=window,
    text="Button1",
    font=("undefined", 14),
    text_color="#000000",
    hover=True,
    hover_color="#949494",
    height=30,
    width=95,
    border_width=2,
    corner_radius=6,
    border_color="#000000",
    bg_color="#62a0ea",
    fg_color="#F0F0F0",
    )
Button_id1.place(x=60, y=40)

#run the main loop
window.mainloop() '''

#másik

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("elso")
root.geometry("400x300")

# Görgethető szövegdoboz létrehozása
#textbox = ctk.CTkTextbox(root, text_color="#ffffff", height=600, width=600, bg_color="#62a0ea", fg_color="#62a0ea",)
#textbox.place(x=320, y=10)
textbox = ctk.CTkTextbox(root)
textbox.pack(fill="both", expand=True, padx=10, pady=10)

# Szöveg hozzáadása
long_text = view_data()
textbox.insert("1.0", long_text)
textbox.configure(state="disabled")  # Csak olvashatóvá teszi

root.mainloop()
