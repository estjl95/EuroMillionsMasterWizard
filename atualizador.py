import tkinter as tk
from tkinter import messagebox
import requests
import os
import sys
import subprocess

VERSAO_LOCAL = "1.2"
URL_VERSAO = "https://raw.githubusercontent.com/estjl95/EuroMillionsMasterWizard/main/versao.txt"

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
                                r.raise_for_status()
                                with open(novo_exe_path, 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)

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

                    janela.transient(tk.Tk())
                    janela.grab_set()
                    janela.mainloop()
                else:
                    messagebox.showinfo("✅ Atualização", f"Já estás com a versão mais recente: v{VERSAO_LOCAL}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao verificar atualização: {e}")