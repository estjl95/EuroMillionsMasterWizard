import os
import sys
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
from atualizador import verificar_atualizacao
from interface import InterfaceApp
from tema import style  # 👉 style já definido no tema.py

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def aplicar_fonte_personalizada():
    try:
        fonte_path = resource_path("assets/OpenSans-Regular.ttf")
        if os.path.exists(fonte_path):
            font.Font(name="DejaVuSans", file=fonte_path) # type:ignore
            font.nametofont("TkDefaultFont").configure(family="DejaVuSans")
    except Exception as e:
        print(f"⚠️ Falha ao aplicar fonte personalizada: {e}")

def mostrar_splash(callback):
    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.geometry("1024x1024+200+100")

    img_path = resource_path("assets/splash.png")
    img = Image.open(img_path)
    photo = ImageTk.PhotoImage(img)

    panel = tk.Label(splash, image=photo) # type: ignore
    panel.image = photo
    panel.pack()

    splash.after(5000, lambda *_args: [splash.destroy(), callback()]) # type: ignore

def iniciar_app():
    InterfaceApp(root, style)
    verificar_atualizacao()

# 🖥️ Estilo global e root inicial
root = style.master

if __name__ == "__main__":
    aplicar_fonte_personalizada()  # Aplica antes de mostrar qualquer janela
    root.withdraw()
    mostrar_splash(lambda: [root.deiconify(), iniciar_app()])
    root.mainloop()
