import os
import sys
import tkinter as tk
import requests
import shutil
import subprocess
from PIL import Image, ImageTk
from interface import InterfaceApp
from tkinter import messagebox

VERSAO_LOCAL = "1.0"
URL_VERSAO = "https://raw.githubusercontent.com/estjl95/versao/main/versao.txt"  # Substitui pelo link direto

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def verificar_atualizacao():
    try:
        resposta = requests.get(URL_VERSAO, timeout=5)
        if resposta.status_code == 200:
            conteudo = resposta.text.strip()
            partes = conteudo.split("|")
            if len(partes) == 2:
                versao_remota, link_download = partes
                if versao_remota != VERSAO_LOCAL:
                    janela = tk.Toplevel()
                    janela.title("Atualização disponível")
                    janela.geometry("400x150")
                    janela.resizable(False, False)

                    label = tk.Label(janela, text=f"Nova versão disponível: {versao_remota}", font=("Segoe UI", 11))
                    label.pack(pady=10)

                    info = tk.Label(janela, text="Clique abaixo para atualizar automaticamente.")
                    info.pack()

                    def atualizar():
                        try:
                            pasta_temp = os.path.join(os.path.dirname(sys.executable), "atualizacao_temp")
                            os.makedirs(pasta_temp, exist_ok=True)

                            novo_exe_path = os.path.join(pasta_temp, "novo.exe")
                            with requests.get(link_download, stream=True) as r:
                                with open(novo_exe_path, 'wb') as f:
                                    shutil.copyfileobj(r.raw, f) # type: ignore

                            script_path = os.path.join(pasta_temp, "atualizar.bat")
                            atual_path = sys.executable.replace('"', '')

                            with open(script_path, 'w') as f:
                                f.write(f"""@echo off
timeout /t 2 >nul
del "{atual_path}" >nul
move "{novo_exe_path}" "{atual_path}"
start "" "{atual_path}"
rmdir /s /q "{pasta_temp}"
""")

                            subprocess.Popen(['cmd', '/c', script_path])
                            sys.exit()

                        except Exception as erro:
                            messagebox.showerror("Erro", f"Erro ao atualizar: {erro}")

                    botao = tk.Button(janela, text="Atualizar agora", command=atualizar)
                    botao.pack(pady=10)

                    janela.transient(root)
                    janela.grab_set()
                    root.wait_window(janela)
    except (requests.RequestException, OSError, shutil.Error) as e:
        messagebox.showerror("Erro", f"Erro ao atualizar: {e}")

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