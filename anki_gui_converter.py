import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import json
import uuid
import genanki
from PIL import Image, ImageTk
import sys
import os

import tkinter as tk
import ttkbootstrap as tb

def show_splash_and_start_main():
    splash = tk.Tk()
    splash.overrideredirect(True)  # Remove window decorations
    splash.geometry("300x150+500+300")  # Size and position (adjust as needed)
    splash_label = tb.Label(splash, text="Loading JSON to Anki Converter...", font=("Segoe UI", 14))
    splash_label.pack(expand=True)

    # After 2000 ms (2 seconds), destroy splash and open main app
    def start_main():
        splash.destroy()
        start_main_window()

    splash.after(4000, start_main)  # Show splash for 2 seconds
    splash.mainloop()


def safe_id():
    return int(str(uuid.uuid4().int)[:9])

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        entry_file_path.delete(0, END)
        entry_file_path.insert(0, file_path)

def generate_apkg():
    json_path = entry_file_path.get()
    deck_name = entry_deck_name.get().strip()
    output_name = entry_output_file.get().strip()

    if not os.path.exists(json_path):
        messagebox.showerror("Error", "Selected JSON file does not exist.")
        return
    if not deck_name or not output_name:
        messagebox.showerror("Error", "Deck name and output file name cannot be empty.")
        return
    if not output_name.endswith(".apkg"):
        output_name += ".apkg"

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            flashcards = json.load(f)

        model = genanki.Model(
            model_id=safe_id(),
            name='Universal Flashcard Model',
            fields=[{'name': 'Question'}, {'name': 'Answer'}],
            templates=[{
                'name': 'Card Template',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            }],
            css=".card { font-family: arial; font-size: 14px; text-align: left; }"
        )

        deck = genanki.Deck(
            deck_id=safe_id(),
            name=deck_name
        )

        for card in flashcards['questions']:
            question = card.get("question", "").strip()
            answer = card.get("answer", "").strip()
            tags = card.get("tags", [])
            if question and answer:
                note = genanki.Note(
                    model=model,
                    fields=[question, answer],
                    tags=tags
                )
                deck.add_note(note)

        genanki.Package(deck).write_to_file(output_name)
        messagebox.showinfo("Success", f"Anki deck created: {output_name}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Main GUI Window
root = tb.Window(themename="darkly")  # Try 'minty', 'journal', 'superhero', 'cyborg'
root.title("JSON to Anki .apkg Converter")
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

icon_path = resource_path("icon.ico")
icon = ImageTk.PhotoImage(file=icon_path)
root.iconphoto(False, icon)
root.geometry("520x340")
root.resizable(False, False)

frame = tb.Frame(root, padding=20)
frame.pack(fill=BOTH, expand=True)

# File Selection
tb.Label(frame, text="Select JSON File:", font=("Segoe UI", 10)).pack(anchor="w")
entry_file_path = tb.Entry(frame, width=60)
entry_file_path.pack(pady=(0, 5))
tb.Button(frame, text="Browse", command=select_file, bootstyle="info-outline").pack(pady=(0, 15))

# Deck Name
tb.Label(frame, text="Deck Name:", font=("Segoe UI", 10)).pack(anchor="w")
entry_deck_name = tb.Entry(frame, width=60)
entry_deck_name.pack(pady=(0, 15))

# Output File Name
tb.Label(frame, text="Output File Name (.apkg):", font=("Segoe UI", 10)).pack(anchor="w")
entry_output_file = tb.Entry(frame, width=60)
entry_output_file.pack(pady=(0, 20))

# Generate Button
tb.Button(
    frame,
    text="Generate .apkg",
    command=generate_apkg,
    bootstyle="success-outline"
).pack(ipadx=10, ipady=5)

root.mainloop()
