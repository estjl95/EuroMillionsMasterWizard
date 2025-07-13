import os
import sys
import tkinter as tk
from atualizador import verificar_atualizacao
from PIL import Image, ImageTk
from interface import InterfaceApp

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def mostrar_splash(callback):
    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.geometry("1024x1024+200+100")

    img_path = resource_path("splash.png")
    img = Image.open(img_path)
    photo = ImageTk.PhotoImage(img)

    panel = tk.Label(splash, image=photo) # type: ignore
    panel.image = photo
    panel.pack()

    splash.after(5000, lambda: [splash.destroy(), callback()]) # type: ignore

def iniciar_app():
    app = InterfaceApp(root)  # noqa: F841
    verificar_atualizacao()

# Janela principal
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    mostrar_splash(lambda: [root.deiconify(), iniciar_app()])
    root.mainloop()