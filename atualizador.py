import tkinter as tk
from tkinter import messagebox
import requests
import os
import sys
import subprocess

VERSAO_LOCAL = "1.4"
URL_VERSAO = "https://raw.githubusercontent.com/estjl95/EuroMillionsMasterWizard/main/versao.txt"
FICHEIRO_IGNORE = os.path.join(os.path.expanduser("~"), ".wizard_ignorar_versao.txt")

def verificar_atualizacao():
    try:
        resposta = requests.get(URL_VERSAO, timeout=15)
        if resposta.status_code != 200:
            messagebox.showerror("Erro", f"Erro ao aceder ao servidor (código {resposta.status_code})")
            return

        linhas = resposta.text.strip().splitlines()
        info = {}
        for linha in linhas:
            if "=" in linha:
                chave, valor = linha.split("=", 1)
                info[chave.strip()] = valor.strip()
            elif linha.startswith("v"):
                info["versao"] = linha.strip()

        versao_remota = info.get("versao")
        link_download = info.get("link")
        data_lancamento = info.get("data", "Data não especificada")
        descricao = info.get("descricao", "Sem descrição disponível.")

        # Verificar se o utilizador ignorou esta versão
        if os.path.exists(FICHEIRO_IGNORE):
            with open(FICHEIRO_IGNORE, "r") as f:
                ignorada = f.read().strip()
                if ignorada == versao_remota:
                    return  # Ignorar verificação

        if versao_remota and versao_remota != VERSAO_LOCAL and link_download:
            janela = tk.Toplevel()
            janela.title("🆕 Atualização disponível")
            janela.geometry("480x220")
            janela.resizable(False, False)

            tk.Label(janela, text=f"Nova versão: {versao_remota}", font=("Segoe UI", 11, "bold")).pack(pady=6)
            tk.Label(janela, text=f"📅 Lançamento: {data_lancamento}", font=("Segoe UI", 10)).pack()
            tk.Label(janela, text=f"📝 Notas: {descricao}", wraplength=440, justify="left", font=("Segoe UI", 9)).pack(pady=6)

            def atualizar():
                try:
                    pasta_temp = os.path.join(os.path.dirname(sys.executable), "atualizacao_temp")
                    os.makedirs(pasta_temp, exist_ok=True)

                    setup_path = os.path.join(pasta_temp, "Setup.exe")
                    with requests.get(link_download, stream=True) as r:
                        r.raise_for_status()
                        with open(setup_path, 'wb') as ficheiro_exe:
                            for chunk in r.iter_content(8192):
                                ficheiro_exe.write(chunk)

                    subprocess.Popen([setup_path, "/SILENT"])
                    sys.exit()
                except Exception as erro:
                    messagebox.showerror("Erro", f"Erro ao atualizar: {erro}")

            def ignorar():
                with open(FICHEIRO_IGNORE, "w") as ficheiro_ignorar:
                    ficheiro_ignorar.write(versao_remota)
                janela.destroy()

            # Botões
            tk.Button(janela, text="🔄 Atualizar agora", command=atualizar).pack(pady=5)
            tk.Button(janela, text="⏸ Ignorar esta versão", command=ignorar).pack()

            janela.transient(tk.Tk())
            janela.grab_set()
            janela.mainloop()
        else:
            messagebox.showinfo("✅ Atualização", f"Já estás com a versão mais recente: v{VERSAO_LOCAL}")

    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao verificar atualização: {e}")
