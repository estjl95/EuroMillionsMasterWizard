import requests
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

VERSAO_LOCAL = "1.5"
URL_VERSAO = "https://raw.githubusercontent.com/estjl95/EuroMillionsMasterWizard/main/versao.txt"
FICHEIRO_IGNORE = os.path.join(os.path.expanduser("~"), ".wizard_ignorar_versao.txt")


def obter_info_versao_remota():
    try:
        resposta = requests.get(URL_VERSAO, timeout=15)
        resposta.raise_for_status()

        linhas = resposta.text.strip().splitlines()
        info = {}

        for linha in linhas:
            if "=" in linha:
                partes = linha.split("=", 1)
                if len(partes) == 2:
                    chave, valor = partes
                    info[chave.strip()] = valor.strip()
            elif linha.lower().startswith("v"):
                info["versao"] = linha.strip()

        return info
    except requests.RequestException as e:
        raise RuntimeError(f"Erro ao obter versão remota: {e}")


def descarregar_instalador(link, destino):
    try:
        with requests.get(link, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(destino, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        if os.path.getsize(destino) < 1024:
            raise ValueError("Ficheiro de instalação inválido ou incompleto.")
    except (requests.RequestException, OSError, ValueError) as e:
        raise RuntimeError(f"Erro ao descarregar instalador: {e}")


def iniciar_instalacao(caminho_instalador):
    try:
        subprocess.Popen([caminho_instalador, "/SILENT"])
        sys.exit()
    except Exception as e:
        raise RuntimeError(f"Erro ao iniciar instalação: {e}")


def mostrar_janela_atualizacao(info, root=None):
    janela = tk.Toplevel(root)
    janela.title("🆕 Atualização disponível")
    janela.geometry("480x220")
    janela.resizable(False, False)

    versao_remota = info.get("versao", "v?")
    data_lancamento = info.get("data", "Data não especificada")
    descricao = info.get("descricao", "Sem descrição disponível.")
    link_download = info.get("link")

    tk.Label(janela, text=f"Nova versão: {versao_remota}", font=("Segoe UI", 11, "bold")).pack(pady=6)
    tk.Label(janela, text=f"📅 Lançamento: {data_lancamento}", font=("Segoe UI", 10)).pack()
    tk.Label(janela, text=f"📝 Notas: {descricao}", wraplength=440, justify="left", font=("Segoe UI", 9)).pack(pady=6)

    def atualizar():
        try:
            pasta_temp = os.path.join(os.path.dirname(sys.executable), "atualizacao_temp")
            os.makedirs(pasta_temp, exist_ok=True)
            setup_path = os.path.join(pasta_temp, "Setup.exe")

            descarregar_instalador(link_download, setup_path)
            iniciar_instalacao(setup_path)
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def ignorar():
        with open(FICHEIRO_IGNORE, "w") as ficheiro_ignorar:
            ficheiro_ignorar.write(versao_remota)
        janela.destroy()

    tk.Button(janela, text="🔄 Atualizar agora", command=atualizar).pack(pady=5)
    tk.Button(janela, text="⏸ Ignorar esta versão", command=ignorar).pack()

    janela.grab_set()
    janela.mainloop()


def verificar_atualizacao(root=None, forcar=True):
    try:
        info = obter_info_versao_remota()
        versao_remota = info.get("versao")
        link_download = info.get("link")

        if not versao_remota or not link_download:
            messagebox.showinfo("Atualização", "Informações de versão incompletas.")
            return

        if not forcar and os.path.exists(FICHEIRO_IGNORE):
            with open(FICHEIRO_IGNORE, "r") as ficheiro_ignorar:
                ignorada = ficheiro_ignorar.read().strip()
                if ignorada == versao_remota:
                    print(f"🔕 Versão {versao_remota} ignorada pelo utilizador.")
                    return

        if versao_remota != VERSAO_LOCAL:
            print("🪟 A mostrar janela de atualização...")
            mostrar_janela_atualizacao(info, root)
        else:
            messagebox.showinfo("✅ Atualização", f"Já estás com a versão mais recente: v{VERSAO_LOCAL}")

    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao verificar atualização:\n{e}")
