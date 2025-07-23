import json
import os
from ttkbootstrap import Style

# Caminho do ficheiro de preferências
CAMINHO_PREFS = "preferencias.json"

# 👁️‍🗨️ Tema por defeito
TEMA_PADRAO = "darkly"

def carregar_tema():
    tema = TEMA_PADRAO  # valor por defeito

    if os.path.exists(CAMINHO_PREFS):
        try:
            with open(CAMINHO_PREFS, "r") as f:
                prefs = json.load(f)
                tema = prefs.get("tema", TEMA_PADRAO)
        except (json.JSONDecodeError, IOError):
            pass  # mantém tema por defeito

    return Style(theme=tema)

def carregar_preferencias():
    caminho = os.path.join(os.getcwd(), CAMINHO_PREFS)
    if not os.path.exists(caminho):
        return {"tema": TEMA_PADRAO}  # valores padrão
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"tema": TEMA_PADRAO}  # fallback seguro

def guardar_tema(novo_tema):
    try:
        with open(CAMINHO_PREFS, "w", encoding="utf-8") as f:
            json.dump({"tema": novo_tema}, f)
    except IOError:
        pass  # Ignora falha silenciosamente

# 🔧 Instanciar estilo com tema carregado
style = carregar_tema()