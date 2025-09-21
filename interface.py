import pandas as pd
import numpy as np
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import datetime
import sys
import requests
import os
import unicodedata
import traceback
import json
from atualizador import verificar_atualizacao
from tkinter import ttk, messagebox, filedialog, simpledialog
from simulador import EuroMillionsMasterWizard
from scipy.stats import poisson
from collections import Counter
from fpdf import FPDF
from datetime import datetime

IDIOMAS_DISPONIVEIS = {
    "pt": "🇵🇹 PT",
    "en": "🇬🇧 EN",
    "fr": "🇫🇷 FR",
    "it": "🇮🇹 IT",
    "de": "🇩🇪 DE",
    "es": "🇪🇸 ES",
    "tr": "🇹🇷 TR"
}


class InterfaceApp:
    def __init__(self, root, style):
        self.root = root
        self.style = style  # 👉 guardar referência ao style

        self.modo_escuro_ativo = True

        self.root.title("EuroMillions Master Wizard v1.6")
        self.root.geometry("1080x920")

        self.simulador = EuroMillionsMasterWizard("dados/resultados_euromilhoes.xlsx")
        self.historico_previsoes = []

        self.posicoes = {
            "N1": 1,
            "N2": 2,
            "N3": 3,
            "N4": 4,
            "N5": 5,
            "Estrela 1": "Star 1",
            "Estrela 2": "Star 2"
        }

        # Subtítulos
        self.label_utilitarios_titulo = None
        self.label_previsao_markov = None
        self.label_comparar_chaves = None
        self.label_seleciona_posicao = None
        self.label_poisson_titulo = None

        self.posicoes_traduzidas = {}

        # Carregar idioma padrão
        self.textos = self.carregar_textos("pt")

        self.valores_poisson_numeros = []
        self.observadas_poisson_numeros = []
        self.valores_poisson_estrelas = []
        self.observadas_poisson_estrelas = []

        # Título
        self.label_titulo = ttk.Label(
            self.root,
            text="🔢 EuroMillions Master Wizard v1.6",
            font=("Segoe UI", 16, "bold")
        )
        self.label_titulo.pack(pady=10)

        # 📦 Container central para os separadores
        self.container_tabs = ttk.Frame(self.root)
        self.container_tabs.pack()

        # Separadores com largura definida e centrados
        self.tabs = ttk.Notebook(self.container_tabs, width=460, height=300)
        self.tabs.pack()

        self.tab_previsoes = ttk.Frame(self.tabs)
        self.tab_acertos = ttk.Frame(self.tabs)
        self.tab_estatisticas = ttk.Frame(self.tabs)
        self.tab_utilitarios = ttk.Frame(self.tabs)
        self.tab_idiomas = ttk.Frame(self.tabs)
        self.tab_sair = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_previsoes, text="🔮 Previsões")
        self.tabs.add(self.tab_acertos, text="✅ Acertos")
        self.tabs.add(self.tab_estatisticas, text="📊 Estatísticas")
        self.tabs.add(self.tab_utilitarios, text="📁 Utilitários")
        self.tabs.add(self.tab_idiomas, text="🌎 Idiomas")
        self.tabs.add(self.tab_sair, text="🚪 Sair")

        self.combo_estatistica = ttk.Combobox(self.tab_estatisticas, values=list(self.posicoes.keys()),
                                              state="readonly")

        # Declaração antecipada dos botões
        self.botao_multi_prever = ttk.Button(self.tab_previsoes)
        self.botao_comparar = ttk.Button(self.tab_acertos)
        self.botao_estatisticas = ttk.Button(self.tab_estatisticas)
        self.botao_poisson = ttk.Button(self.tab_estatisticas) # ✅ botão para ativar Poisson
        self.botao_poisson_estrelas = ttk.Button(self.tab_estatisticas) # ✅ botão para ativar Poisson
        self.combo_estatistica = ttk.Combobox(self.tab_estatisticas, values=list(self.posicoes.keys()),
                                              state="readonly")

        # Idiomas
        self.combo_idioma = ttk.Combobox(
            self.tab_idiomas,
            values=list(IDIOMAS_DISPONIVEIS.values()),
            state="readonly"
        )
        self.combo_idioma.set(IDIOMAS_DISPONIVEIS["pt"])
        self.combo_idioma.pack(pady=10)
        self.combo_idioma.bind("<<ComboboxSelected>>", lambda e: self.mudar_idioma(
            self.obter_codigo_idioma(self.combo_idioma.get())
        ))

        # Canvas para mostrar gráfico
        self.canvas_poisson = tk.Canvas(self.tab_estatisticas, width=720, height=440)  # ✅ canvas puro

        # Importar/exportar
        self.botao_importar = ttk.Button(self.tab_utilitarios)
        self.botao_estado = ttk.Button(self.tab_utilitarios)
        self.botao_exportar = ttk.Button(self.tab_utilitarios)
        self.botao_atualizar = ttk.Button(self.tab_utilitarios)
        self.botao_tema = ttk.Button(self.tab_utilitarios)

        # Outros idiomas
        self.botao_idiomas = ttk.Button(self.tab_idiomas)

        # Sair do programa
        self.botao_sair = ttk.Button(self.tab_sair)

        temas = ["darkly", "litera", "solar", "cyborg", "superhero"]
        self.combo_tema = ttk.Combobox(self.tab_utilitarios, values=temas, state="readonly")
        self.combo_tema.set("darkly")
        self.combo_tema.pack(pady=5)
        self.combo_tema.bind("<<ComboboxSelected>>", lambda e: self.style.theme_use(self.combo_tema.get()))

        # Resultado visual abaixo dos separadores
        self.resultado = tk.Label(self.root, text="", font=("Segoe UI Emoji", 11))
        self.resultado.pack(pady=15)

        self.criar_widgets()

        # Área de histórico com 'scroll'
        self.frame_historico = ttk.Frame(self.root)
        self.frame_historico.pack(expand=True, fill="both")

        self.scrollbar = ttk.Scrollbar(self.frame_historico)
        self.scrollbar.pack(side="right", fill="y")

        self.texto_historico = tk.Text(self.frame_historico, height=8, wrap="word", yscrollcommand=self.scrollbar.set)
        self.texto_historico.pack(side="left", fill="both", expand=True)

    def alternar_modo(self):
        if self.style.theme.name == "darkly":
            self.style.theme_use("litera")
            self.modo_escuro_ativo = False
            self.botao_tema.config(text="🌞 Modo Claro")
        else:
            self.style.theme_use("darkly")
            self.modo_escuro_ativo = True
            self.botao_tema.config(text="🌙 Modo Escuro")

    @staticmethod
    def carregar_textos(idioma="pt"):
        caminho = os.path.join("lang", f"{idioma}.json")
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def obter_codigo_idioma(texto_selecionado):
        for codigo, nome in IDIOMAS_DISPONIVEIS.items():
            if nome == texto_selecionado:
                return codigo
        return "pt", "en", "fr", "it", "de", "es", "tr"

    def mudar_idioma(self, idioma):
        self.textos = self.carregar_textos(idioma)
        self.atualizar_interface()

        # Depuração
        print(self.textos["label_utilitarios_titulo"])
        print("Idioma atualizado para:", idioma)
        print("Novo texto:", self.textos["label_utilitarios_titulo"])

    def atualizar_interface(self):
        self.label_titulo.config(text=self.textos["titulo"])
        if self.label_utilitarios_titulo:
            self.label_utilitarios_titulo.config(
                text=self.textos.get("label_utilitarios_titulo", "Temas e outras opções:")
            )
        self.label_previsao_markov.config(text=self.textos.get("label_previsao_markov"))
        self.label_comparar_chaves.config(text=self.textos.get("label_comparar_chaves"))
        self.label_seleciona_posicao.config(text=self.textos.get("label_seleciona_posicao"))
        self.label_poisson_titulo.config(text=self.textos.get("label_poisson_titulo"))
        self.label_utilitarios_titulo.config(text=self.textos.get("label_utilitarios_titulo"))
        self.botao_multi_prever.config(
            text=self.textos.get("botao_multi_prever", "🔮 Prever sequências")
        )
        self.botao_comparar.config(
            text=self.textos.get("botao_comparar", "🧮 Verificar acertos")
        )
        self.botao_estatisticas.config(text=self.textos["botao_estatisticas"])
        self.botao_poisson.config(text=self.textos["botao_poisson"])
        self.botao_poisson_estrelas.config(text=self.textos["botao_poisson_estrelas"])
        self.botao_importar.config(text=self.textos["botao_importar"])
        self.botao_estado.config(text=self.textos["botao_estado"])
        self.botao_exportar.config(text=self.textos["botao_exportar"])
        self.botao_atualizar.config(
            text=self.textos.get("botao_atualizar", "🔍 Verificar atualizações")
        )
        self.botao_tema.config(text=self.textos["botao_tema"])
        self.botao_idiomas.config(text=self.textos["botao_idiomas"])
        self.botao_sair.config(text=self.textos["botao_sair"])
        self.tabs.tab(self.tab_previsoes, text=self.textos["tab_previsoes"])
        self.tabs.tab(self.tab_acertos, text=self.textos["tab_acertos"])
        self.tabs.tab(self.tab_estatisticas, text=self.textos["tab_estatisticas"])
        self.tabs.tab(self.tab_utilitarios, text=self.textos["tab_utilitarios"])
        self.tabs.tab(self.tab_idiomas, text=self.textos["tab_idiomas"])
        self.tabs.tab(self.tab_sair, text=self.textos["tab_sair"])

    def fechar_programa(self):
        titulo = self.textos.get("msg_confirmar_saida_titulo", "Confirmar saída")
        mensagem = self.textos.get("msg_confirmar_saida_texto", "Tens a certeza que pretendes sair?")
        if messagebox.askokcancel(titulo, mensagem):
            self.root.quit()
            sys.exit()

    def criar_widgets(self):
        # 🔮 Previsão sequencial completa
        self.label_previsao_markov = ttk.Label(
            self.tab_previsoes,
            text=self.textos.get("label_previsao_markov", "Prever padrões sequenciais com a Cadeia de Markov:"),
            font=("Segoe UI", 10, "bold")
        )
        self.label_previsao_markov.pack(pady=10)

        self.botao_multi_prever = tk.Button(
            self.tab_previsoes,
            text=self.textos.get("botao_multi_prever", "🔮 Prever sequências"),
            command=self.prever_sequencia
        )
        self.botao_multi_prever.pack(pady=5)

        # ✅ Comparação de acertos
        self.label_comparar_chaves = ttk.Label(
            self.tab_acertos,
            text=self.textos.get("label_comparar_chaves", "Comparar a chave jogada com a chave sorteada:"),
            font=("Segoe UI", 10, "bold")
        )
        self.label_comparar_chaves.pack(pady=10)

        self.botao_comparar = tk.Button(
            self.tab_acertos,
            text=self.textos.get("botao_comparar", "🧮 Verificar acertos"),
            command=self.comparar_com_chave_oficial
        )
        self.botao_comparar.pack(pady=5)

        # 📊 Estatísticas — Posição
        self.label_seleciona_posicao = ttk.Label(
            self.tab_estatisticas,
            text=self.textos.get("label_seleciona_posicao", "Seleciona a posição"),
            font=("Segoe UI", 10, "bold")
        )
        self.label_seleciona_posicao.pack(pady=(15, 5))

        self.combo_estatistica.pack(pady=5)
        self.combo_estatistica.current(0)

        self.botao_estatisticas.config(
            text=self.textos.get("botao_estatisticas", "📊 Consultar"),
            command=self.mostrar_estatisticas
        )
        self.botao_estatisticas.pack(pady=(5, 15))

        # 📊 Título da secção Poisson
        self.label_poisson_titulo = ttk.Label(
            self.tab_estatisticas,
            text=self.textos.get("label_poisson_titulo", "Distribuição de Poisson (últimos 100 sorteios):"),
            font=("Segoe UI", 10, "bold")
        )
        self.label_poisson_titulo.pack(pady=(5, 5))

        self.botao_poisson.config(
            text=self.textos.get("botao_poisson", "📊 Números"),
            command=self.mostrar_poisson
        )
        self.botao_poisson.pack(pady=5)

        self.botao_poisson_estrelas.config(
            text=self.textos.get("botao_poisson_estrelas", "🌟 Estrelas"),
            command=self.mostrar_poisson_estrelas
        )
        self.botao_poisson_estrelas.pack(pady=5)

        self.canvas_poisson.pack(pady=(10, 15))

        # 📁 Utilitários
        self.label_utilitarios_titulo = ttk.Label(
            self.tab_utilitarios,
            text=self.textos.get("label_utilitarios_titulo", "Temas e outras opções:"),
            font=("Segoe UI", 10, "bold")
        )
        self.label_utilitarios_titulo.pack(pady=10)

        self.botao_importar.config(
            text="📁 Atualizar histórico de sorteios EuroMillions",
            command=self.atualizar_resultados
        )
        self.botao_importar.pack(pady=10)

        self.botao_exportar.config(text="💾 Exportar previsões obtidas",command=self.exportar_previsoes)
        self.botao_exportar.pack(pady=5)

        self.botao_estado = ttk.Button(
            self.tab_utilitarios,
            text="ℹ️ Ver estado do histórico",
            command=self.mostrar_estado
        )
        self.botao_estado.pack(pady=5)

        self.botao_atualizar = tk.Button(text="🔍 Verificar atualizações",
                                         command=lambda: verificar_atualizacao(self.textos))
        self.botao_atualizar.pack(pady=5)

        self.botao_tema = ttk.Button(
            self.tab_utilitarios,
            text="🌗 Alternar tema",
            command=self.alternar_modo
        )
        self.botao_tema.pack(pady=5)

        # 🚪 Sair
        self.botao_sair = ttk.Button(
            self.tab_sair,
            text="🚪 Sair do programa",
            command=self.fechar_programa
        )
        self.botao_sair.pack(pady=10)

    def mostrar_estatisticas(self):
        posicao_nome_traduzido = self.combo_estatistica.get()
        if not posicao_nome_traduzido:
            alerta = self.textos.get("msg_estatisticas_alerta", "Seleciona uma posição para visualizar estatísticas.")
            messagebox.showinfo("Info", alerta)
            return

        # 🔁 Mapeamento reverso entre nomes traduzidos e originais
        self.posicoes_traduzidas = {}
        valores_posicoes = []

        self.posicoes_traduzidas.clear()
        for chave in self.posicoes.keys():
            if "Estrela" in chave:
                chave_traduzida = chave.replace("Estrela", self.textos.get("label_estrela", "Estrela"))
            else:
                chave_traduzida = chave
            self.posicoes_traduzidas[chave_traduzida] = chave
            valores_posicoes.append(chave_traduzida)

        self.combo_estatistica["values"] = valores_posicoes

        # 🔍 Obter nome original da posição
        posicao_nome_original = self.posicoes_traduzidas.get(posicao_nome_traduzido)
        if not posicao_nome_original:
            messagebox.showinfo("Info", self.textos.get("msg_estatisticas_alerta"))
            return

        coluna = self.posicoes[posicao_nome_original]

        try:
            stats = self.simulador.estatisticas_por_coluna(coluna)

            texto = self.textos.get("msg_estatisticas_titulo", "📊 Estatísticas para {posicao}:").format(
                posicao=posicao_nome_traduzido)
            texto += "\n" + self.textos.get("msg_estatisticas_media", "Média: {media}").format(media=stats["media"])
            texto += "\n\n" + self.textos.get("msg_estatisticas_top10", "Top 10 mais frequentes:") + "\n"

            for num, freq in stats["top_10"].items():
                texto += f"\n  {num}: {freq}x"

            self.texto_historico.insert("end", texto + "\n\n")
            self.texto_historico.see("end")

        except Exception as e:
            titulo = self.textos.get("msg_estatisticas_erro_titulo", "Erro")
            texto_erro = self.textos.get("msg_estatisticas_erro_texto",
                                         "Não foi possível calcular estatísticas:\n{erro}")
            texto_erro = texto_erro.replace("{erro}", str(e))
            messagebox.showerror(titulo, texto_erro)

    def mostrar_poisson(self):
        try:
            df = pd.read_excel("dados/resultados_euromilhoes.xlsx", header=1)
            df.columns = [str(c) for c in df.columns]

            col_numeros = ["1", "2", "3", "4", "5"]
            df_recente = df.tail(100)
            todos_numeros = df_recente[col_numeros].values.flatten()

            contagem = pd.Series(todos_numeros).value_counts().sort_index()
            valores = contagem.index.astype(int)
            observadas = contagem.values

            lambda_val = np.mean(observadas)
            esperada = poisson.pmf(observadas, mu=lambda_val) * sum(observadas)

            for child in self.canvas_poisson.winfo_children():
                child.destroy()

            fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=100)
            cmap = plt.get_cmap("viridis")
            max_index = np.argmax(observadas)

            colors = [
                "tomato" if i == max_index else cmap(i / len(valores))
                for i in range(len(valores))
            ]

            ax.bar(valores, observadas, color=colors,
                   label=self.textos.get("poisson_legenda_observada", "Frequência Observada"))

            for i, v in enumerate(observadas):
                x = float(valores[i])
                y = v + max(observadas) * 0.02
                ax.text(x=x, y=y, s=str(v), ha="center", fontsize=8)

            ax.plot(valores, esperada, "r--", linewidth=2,
                    label=self.textos.get("poisson_legenda_esperada", "Poisson Esperada"))

            ax.set_title(self.textos.get("poisson_titulo_numeros", "Distribuição de Poisson — Últimos 100 sorteios"))
            ax.set_xlabel(self.textos.get("poisson_label_x_numeros", "Número"))
            ax.set_ylabel(self.textos.get("poisson_label_y", "Ocorrências"))
            ax.legend()
            ax.grid(alpha=0.3)
            plt.show()

            texto_resumo = self.textos.get("poisson_resumo_numeros").format(
                media=f"{lambda_val:.2f}",
                numero=valores[max_index],
                frequencia=max(observadas)
            )
            self.texto_historico.insert("end", texto_resumo + "\n")
            self.texto_historico.see("end")

        except Exception as e:
            erro_txt = self.textos.get("poisson_erro_numeros", "Erro ao gerar gráfico de Poisson:\n{erro}")
            messagebox.showerror("Erro", erro_txt.replace("{erro}", str(e)))

    def mostrar_poisson_estrelas(self):
        try:
            df = pd.read_excel("dados/resultados_euromilhoes.xlsx", header=1)
            df.columns = [str(c) for c in df.columns]

            col_estrelas = ["Star 1", "Star 2"]
            df_recente = df.tail(100)
            todas_estrelas = df_recente[col_estrelas].values.flatten()

            contagem = pd.Series(todas_estrelas).value_counts().sort_index()
            valores = contagem.index.astype(int)
            observadas = contagem.values

            lambda_val = np.mean(observadas)
            esperada = poisson.pmf(observadas, mu=lambda_val) * sum(observadas)

            fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=100)
            cmap = plt.get_cmap("plasma")
            max_index = np.argmax(observadas)

            colors = [
                "gold" if i == max_index else cmap(i / len(valores))
                for i in range(len(valores))
            ]

            ax.bar(valores, observadas, color=colors,
                   label=self.textos.get("poisson_legenda_observada", "Frequência Observada"))

            for i, v in enumerate(observadas):
                x = float(valores[i])
                y = float(v) + 0.5  # type: ignore
                ax.text(x, y, str(v), ha="center", fontsize=8)

            ax.plot(valores, esperada, "r--", linewidth=2,
                    label=self.textos.get("poisson_legenda_esperada", "Poisson Esperada"))

            ax.set_title(
                self.textos.get("poisson_titulo_estrelas", "Distribuição de Poisson — Estrelas (últimos 100 sorteios)"))
            ax.set_xlabel(self.textos.get("poisson_label_x_estrelas", "Estrela"))
            ax.set_ylabel(self.textos.get("poisson_label_y", "Ocorrências"))
            ax.legend()
            ax.grid(alpha=0.3)
            plt.show()

            texto = self.textos.get("poisson_resumo_estrelas").format(
                media=f"{lambda_val:.2f}",
                estrela=valores[max_index],
                frequencia=max(observadas)
            )
            self.texto_historico.insert("end", texto + "\n")
            self.texto_historico.see("end")

        except Exception as e:
            erro_txt = self.textos.get("poisson_erro_estrelas", "Erro ao gerar gráfico de Poisson (estrelas):\n{erro}")
            messagebox.showerror("Erro", erro_txt.replace("{erro}", str(e)))

    def prever_sequencia(self):
        previsoes = {}
        usados = set()

        # 🔍 Preparar os pares de estrelas mais frequentes
        df_estrelas = self.simulador.df[self.simulador.col_estrelas].dropna().astype(int)
        pares_estrelas = [tuple(sorted(row)) for row in df_estrelas.values.tolist()]
        pares_frequentes = [par for par, _ in Counter(pares_estrelas).most_common(10)]

        for nome, coluna in self.posicoes.items():
            if coluna not in self.simulador.transicoes:
                self.simulador.gerar_cadeia_markov(coluna)

            trans = self.simulador.transicoes.get(coluna, {})
            if not trans:
                previsoes[nome] = "?"
                continue

            # ✨ Tratar estrelas como par frequente
            if nome == "Estrela 1":
                for e1, e2 in pares_frequentes:
                    if e1 not in usados and e2 not in usados:
                        previsoes["Estrela 1"] = e1
                        previsoes["Estrela 2"] = e2
                        usados.update({e1, e2})
                        break
                continue

            # 🔢 Tratar números principais com Markov
            try:
                origens_fortes = sorted(
                    trans.items(),
                    key=lambda item: sum(item[1].values()),
                    reverse=True
                )[:3]

                previsao = None
                for origem, destinos in origens_fortes:
                    tentativa = self.simulador.prever_por_markov(coluna, origem)
                    if tentativa is not None and tentativa not in usados:
                        previsao = tentativa
                        usados.add(previsao)
                        break

                previsoes[nome] = previsao if previsao is not None else "?"

            except ValueError:
                previsoes[nome] = "?"

        # Extras visuais
        self.mostrar_destinos_provaveis()

    def mostrar_destinos_provaveis(self):
        titulo = self.textos.get("msg_destinos_titulo",
                                 "🔍 Destinos prováveis para cada posição, no jogo (dados atualizados):")
        self.texto_historico.insert("end", titulo + "\n")

        for nome, coluna in self.posicoes.items():
            transicoes = self.simulador.transicoes_percentuais.get(coluna, {})
            for origem in transicoes:
                destinos = transicoes[origem]
                mais_fortes = sorted(destinos.items(), key=lambda x: x[1], reverse=True)[:5]
                destinos_formatados = ", ".join(f"{d} ({p}%)" for d, p in mais_fortes)

                nome_traduzido = nome.replace("Estrela", self.textos.get("label_estrela", "Estrela"))
                linha_template = self.textos.get("msg_destinos_linha", "🔸 {posicao} ({origem}) → {destinos}")
                linha = linha_template.format(posicao=nome_traduzido, origem=origem, destinos=destinos_formatados)

                self.texto_historico.insert("end", linha + "\n")

        self.texto_historico.insert("end", "\n")
        self.texto_historico.see("end")

    @staticmethod
    def obter_chave_oficial():
        try:
            # Lê o ficheiro começando na segunda linha e garante colunas em 'string'
            df = pd.read_excel("dados/resultados_euromilhoes.xlsx", header=1)
            df.columns = [str(c) for c in df.columns]

            # Colunas reais
            col_date = "Date"
            col_numeros = ["1", "2", "3", "4", "5"]
            col_estrelas = ["Star 1", "Star 2"]

            # Verificar colunas
            for col in [col_date] + col_numeros + col_estrelas:
                if col not in df.columns:
                    raise ValueError(f"Coluna '{col}' não encontrada no ficheiro.")

            # Converter datas
            df[col_date] = pd.to_datetime(df[col_date], errors="coerce")
            df_validas = df[df[col_date].notna()]

            # Filtrar apenas sorteios de terça ou sexta
            df_sorteios = df_validas[df_validas[col_date].dt.weekday.isin([1, 4])]
            if df_sorteios.empty:
                raise ValueError("Não há sorteios válidos de terça ou sexta no ficheiro.")

            # Obter o sorteio mais recente
            ultimo = df_sorteios.sort_values(col_date, ascending=False).iloc[0]

            numeros = [int(ultimo[col].item()) for col in col_numeros]
            estrelas = [int(ultimo[col].item()) for col in col_estrelas]
            data_txt = ultimo[col_date].strftime("%d/%m/%Y")

            return numeros, estrelas, data_txt

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter chave oficial:\n{e}")
            return [], [], ""

    def mostrar_chave_real(self):
        numeros, estrelas, data_txt = self.obter_chave_oficial()
        if not numeros or not estrelas:
            return

        texto = f"🎯 Chave oficial sorteada ({data_txt}):\n"
        texto += f"Números: {', '.join(str(n) for n in numeros)}\n"
        texto += f"Estrelas: {', '.join(str(e) for e in estrelas)}"

        self.resultado.config(text=texto)
        self.texto_historico.insert("end", texto + "\n\n")
        self.texto_historico.see("end")

    def comparar_com_chave_oficial(self):
        pergunta = self.textos.get("msg_comparar_pergunta")
        titulo = self.textos.get("msg_comparar_titulo")
        escolha = messagebox.askquestion(titulo, pergunta, icon="question")

        if escolha == "sim":
            self.comparar_com_chave_oficial()
            return
        elif escolha != "não":
            # 📥 Pedir sequência prevista
            num_escolhidos_txt = simpledialog.askstring("5 números", self.textos.get("msg_input_numeros"))
            estrelas_escolhidas_txt = simpledialog.askstring("2 estrelas", self.textos.get("msg_input_estrelas"))

            if not num_escolhidos_txt or not estrelas_escolhidas_txt:
                self.texto_historico.insert("end", self.textos.get("msg_cancelado") + "\n\n")
                return

            try:
                num_escolhidos_txt = [int(n.strip()) for n in num_escolhidos_txt.split(",") if n.strip().isdigit()]
                estrelas_escolhidas_txt = [int(e.strip()) for e in estrelas_escolhidas_txt.split(",") if
                                           e.strip().isdigit()]
                if len(num_escolhidos_txt) != 5 or len(estrelas_escolhidas_txt) != 2:
                    self.texto_historico.insert("end", self.textos.get("msg_erro_previsao") + "\n\n")
                    return
            except TypeError:
                self.texto_historico.insert("end", self.textos.get("msg_erro_processamento_previsao") + "\n\n")
                return

            # 📥 Pedir chave oficial
            num_oficial_txt = simpledialog.askstring("Chave Oficial", self.textos.get("msg_input_oficial_numeros"))
            estrela_oficial_txt = simpledialog.askstring("Chave Oficial", self.textos.get("msg_input_oficial_estrelas"))

            if not num_oficial_txt or not estrela_oficial_txt:
                self.texto_historico.insert("end", self.textos.get("msg_cancelado") + "\n\n")
                return

            try:
                numeros_oficiais = [int(n.strip()) for n in num_oficial_txt.split(",") if n.strip().isdigit()]
                estrelas_oficiais = [int(e.strip()) for e in estrela_oficial_txt.split(",") if e.strip().isdigit()]
                if len(numeros_oficiais) != 5 or len(estrelas_oficiais) != 2:
                    self.texto_historico.insert("end", self.textos.get("msg_erro_oficial") + "\n\n")
                    return
            except TypeError:
                self.texto_historico.insert("end", self.textos.get("msg_erro_processamento_oficial") + "\n\n")
                return

            data_txt = "Resultado"
            total_n = sum(n in numeros_oficiais for n in num_escolhidos_txt)
            total_e = sum(e in estrelas_oficiais for e in estrelas_escolhidas_txt)

            self.texto_historico.insert("end",
                                        self.textos.get("msg_comparacao_titulo", "").format(data=data_txt) + "\n",
                                        "titulo")
            self.texto_historico.insert("end", self.textos.get("msg_chave_manual", "").format(
                numeros=", ".join(map(str, num_escolhidos_txt)),
                estrelas=", ".join(map(str, estrelas_escolhidas_txt))
            ) + "\n")
            self.texto_historico.insert("end", self.textos.get("msg_chave_oficial", "").format(
                numeros=", ".join(map(str, numeros_oficiais)),
                estrelas=", ".join(map(str, estrelas_oficiais))
            ) + "\n")
            self.texto_historico.insert("end", self.textos.get("msg_acertos", "").format(
                total_n=total_n, total_e=total_e
            ) + "\n")

            if all(n in numeros_oficiais for n in num_escolhidos_txt):
                self.texto_historico.insert("end", self.textos.get("msg_quinteto") + "\n", "numeros_certos")

            if all(e in estrelas_oficiais for e in estrelas_escolhidas_txt):
                self.texto_historico.insert("end", self.textos.get("msg_par_estrelas") + "\n", "par_estrela_certo")

            if all(n in numeros_oficiais for n in num_escolhidos_txt) and all(
                    e in estrelas_oficiais for e in estrelas_escolhidas_txt):
                self.texto_historico.insert("end", self.textos.get("msg_jackpot") + "\n",
                                            "numeros_certos, par_estrela_certo")

            self.texto_historico.insert("end", "\n")
            self.texto_historico.see("end")

            texto_resultado = (
                    self.textos.get("msg_chave_oficial", "").format(
                        numeros=", ".join(map(str, numeros_oficiais)),
                        estrelas=", ".join(map(str, estrelas_oficiais))
                    ) + "\n" +
                    self.textos.get("msg_acertos", "").format(total_n=total_n, total_e=total_e)
            )
            self.resultado.config(text=texto_resultado)

    def atualizar_resultados(self):
        try:
            file_id = "1fVvlpxDhtOVJvdjllDCRhiqNCgaTqFCS"
            url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"

            pasta_destino = os.path.join(os.path.expanduser("~"), "EuroMillions")
            os.makedirs(pasta_destino, exist_ok=True)

            caminho_ficheiro = os.path.join(pasta_destino, "resultados_euromilhoes.xlsx")

            response = requests.get(url)
            response.raise_for_status()

            with open(caminho_ficheiro, "wb") as f:
                f.write(response.content)

            # Depuração
            print(self.textos.get("atualizacao_sucesso", "✅ Ficheiro atualizado com sucesso."))

            # Janela pop-up
            messagebox.showinfo(
                title=self.textos.get("atualizacao_titulo", "Atualização"),
                message=self.textos.get("atualizacao_sucesso", "✅ Ficheiro atualizado com sucesso.")
            )

            for coluna in self.posicoes.values():
                self.simulador.gerar_cadeia_markov(coluna)

            messagebox.showinfo(
                title=self.textos.get("atualizacao_titulo", "Atualização"),
                message=self.textos.get("msg_markov_reconstruida",
                                        "✅ A matriz de transição Markov foi atualizada com os novos dados.")
            )

            self.atualizar_poisson()

            messagebox.showinfo(
                title=self.textos.get("atualizacao_titulo", "Atualização"),
                message=self.textos.get("poisson_atualizada",
                                        "📊 Os dados da distribuição de Poisson foram atualizados.")
            )

            return caminho_ficheiro

        except Exception as e:
            erro_txt = self.textos.get("atualizacao_erro", "❌ Erro ao atualizar ficheiro: {erro}")
            print(erro_txt.replace("{erro}", str(e)))
            return None

    @staticmethod
    def calcular_poisson(df, colunas):
        df_recente = df.tail(100)
        valores = df_recente[colunas].values.flatten()
        contagem = pd.Series(valores).value_counts().sort_index()
        return contagem.index.astype(int), contagem.values

    def atualizar_poisson(self):
        try:
            df = pd.read_excel("dados/resultados_euromilhoes.xlsx", header=1)
            df.columns = [str(c) for c in df.columns]

            self.valores_poisson_numeros, self.observadas_poisson_numeros = self.calcular_poisson(df,
                                                                                                  ["1", "2", "3", "4",
                                                                                                   "5"])
            self.valores_poisson_estrelas, self.observadas_poisson_estrelas = self.calcular_poisson(df, ["Star 1",
                                                                                                         "Star 2"])

        except Exception as e:
            print(f"Erro ao atualizar dados de Poisson: {e}")

    @staticmethod
    def obter_estado_ficheiro(caminho):
        estado = {
            "valido": False,
            "erro": "",
            "sorteios": 0,
            "colunas": [],
            "chave": [],
            "estrelas": [],
            "data_ultima_chave": "",
            "ultima_atualizacao": "",
            "caminho": caminho
        }

        try:
            def normalizar(texto):
                return unicodedata.normalize("NFKD", str(texto)).encode("ASCII",
                                                                        "ignore").decode().lower()

            def encontrar_coluna(dataframe, tipo, indice):
                if tipo == "estrela":
                    alternativas = [
                        f"star {indice}",
                        f"star{indice}",
                        f"estrela {indice}",
                        f"estrela{indice}",
                        f"s{indice}",
                        f"e{indice}"
                    ]
                else:
                    alternativas = [
                        f"{indice}",
                        f"n{indice}",
                        f"num {indice}",
                        f"numero {indice}"
                    ]

                for col in dataframe.columns:
                    col_normalizado = normalizar(col)
                    if any(alt == col_normalizado for alt in alternativas):
                        return col

                # Depuração
                print("🔢 Colunas de números:", colunas_numeros)
                print("✨ Colunas de estrelas:", colunas_estrelas)
                print("📄 Primeira linha de dados:", df_ordenado.iloc[0][colunas_numeros + colunas_estrelas].to_dict())

                return None

            def extrair_valor(registro, col):
                if col is None:
                    return 0
                try:
                    dado = registro[col]
                    if pd.isna(dado):
                        return 0
                    return int(str(dado).strip())
                except (KeyError, ValueError, TypeError):
                    return 0

            df = pd.read_excel(caminho, skiprows=1)
            df.columns = df.columns.map(str)  # força todas as colunas a serem 'strings'
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

            # Depuração
            print("\n📋 Tipos de colunas:", [type(col) for col in df.columns])
            print("\n📋 Colunas originais:", df.columns.tolist())

            estado["colunas"] = list(df.columns)
            estado["sorteios"] = len(df)

            # Detecta coluna de data
            coluna_data = next(
                (col for col in df.columns if any(term in col.lower() for term in ["data", "date", "dia", "draw"])),
                None
            )
            print(f"\n🕒 Coluna de data reconhecida: {coluna_data}")   # Depuração
            if not coluna_data and "Arquivo" in df.columns:
                df["Date"] = pd.to_datetime(df["Arquivo"], errors="coerce")
                coluna_data = "Date"

            if not coluna_data:
                raise ValueError(f"❌ Nenhuma coluna de data encontrada. Colunas disponíveis: {df.columns.tolist()}")

            df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
            df = df.dropna(subset=[coluna_data])

            # Identifica colunas de números e estrelas
            colunas_numeros = [encontrar_coluna(df, "numero", i) for i in range(1, 6)]
            colunas_estrelas = [encontrar_coluna(df, "estrela", i) for i in range(1, 3)]
            colunas_numeros = [col for col in colunas_numeros if col]
            colunas_estrelas = [col for col in colunas_estrelas if col]

            # Depuração
            print(f"📁 Ficheiro: {os.path.basename(estado['caminho'])}\n")
            print("🔢 Colunas de números:", colunas_numeros)
            print("✨ Colunas de estrelas:", colunas_estrelas)
            print(f"✅ Estrutura válida: Sim\n")

            if len(colunas_numeros) < 5 or len(colunas_estrelas) < 2:
                raise ValueError("❌ Colunas de números ou estrelas incompletas. Verifica o ficheiro.")

            df_filtrado = df.dropna(subset=colunas_numeros + colunas_estrelas)
            df_filtrado = df_filtrado[(df_filtrado[colunas_numeros + colunas_estrelas] != 0).all(axis=1)]
            df_ordenado = df_filtrado.sort_values(coluna_data, ascending=False)

            for _, linha in df_ordenado.iterrows():
                numeros_validos = all(extrair_valor(linha, col) >= 1 for col in colunas_numeros)
                estrelas_validas = all(extrair_valor(linha, col) >= 1 for col in colunas_estrelas)
                if numeros_validos and estrelas_validas:
                    ultima_linha = linha
                    break
            else:
                raise ValueError("❌ Nenhuma linha válida com números e estrelas encontrada.")

            estado["chave"] = [extrair_valor(ultima_linha, col) for col in colunas_numeros]
            estado["estrelas"] = [extrair_valor(ultima_linha, col) for col in colunas_estrelas]
            estado["data_ultima_chave"] = ultima_linha[coluna_data].strftime("%d-%m-%Y")
            estado["valido"] = True

        except (FileNotFoundError, ValueError, KeyError, TypeError, pd.errors.ParserError):
            estado["erro"] = traceback.format_exc()
            print("⚠️ Erro capturado:\n", estado["erro"])

        if os.path.exists(caminho):
            mod_time = os.path.getmtime(caminho)
            estado["ultima_atualizacao"] = datetime.fromtimestamp(mod_time).strftime("%d-%m-%Y %H:%M")
        else:
            estado["ultima_atualizacao"] = "Ficheiro não encontrado"

        return estado

    def mostrar_estado(self):
        caminho = os.path.join(os.path.expanduser("~"), "EuroMillions", "resultados_euromilhoes.xlsx")
        estado = self.__class__.obter_estado_ficheiro(caminho)

        if estado["valido"]:
            chave = estado["chave"]
            estrelas = estado["estrelas"]
            data = estado["data_ultima_chave"]

            texto = (
                    self.textos.get("estado_valido_atualizacao", "🕒 Última atualização: {data}").format(
                        data=estado["ultima_atualizacao"]) + "\n" +
                    self.textos.get("estado_valido_sorteios", "📊 Sorteios carregados: {quantidade}").format(
                        quantidade=estado["sorteios"]) + "\n\n" +
                    self.textos.get("estado_valido_titulo_chave", "🎯 Última chave sorteada ({data}):").format(
                        data=data) + "\n" +
                    self.textos.get("estado_valido_numeros", "🔢 Números: {numeros}").format(
                        numeros=", ".join(map(str, chave))) + "\n" +
                    self.textos.get("estado_valido_estrelas", "✨ Estrelas: {estrelas}").format(
                        estrelas=", ".join(map(str, estrelas))) + "\n"
            )
        else:
            texto = (
                    self.textos.get("estado_invalido_ficheiro", "📁 Ficheiro: {nome}").format(
                        nome=os.path.basename(estado["caminho"])) + "\n" +
                    self.textos.get("estado_invalido_atualizacao", "🕒 Última atualização: {data}").format(
                        data=estado["ultima_atualizacao"]) + "\n" +
                    self.textos.get("estado_invalido_erro_titulo",
                                    "⚠️ Estrutura inválida ou erro ao ler ficheiro") + "\n" +
                    self.textos.get("estado_invalido_erro_detalhes", "🧾 Detalhes do erro: {erro}").format(
                        erro=estado["erro"])
            )

        self.resultado.config(text=texto)

    def exportar_previsoes(self):
        if not self.historico_previsoes:
            messagebox.showinfo(
                title=self.textos.get("exportar_titulo_dialogo", "Exportar"),
                message=self.textos.get("exportar_alerta_vazia", "Ainda não há previsões para exportar.")
            )
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        nome_sugestao = f"previsoes_v1.4_{timestamp}.xlsx"

        caminho = filedialog.asksaveasfilename(
            initialfile=nome_sugestao,
            defaultextension=".xlsx",
            filetypes=[
                (self.textos.get("label_excel", "Ficheiros Excel"), "*.xlsx"),
                (self.textos.get("label_pdf", "Ficheiros PDF"), "*.pdf")
            ],
            title=self.textos.get("exportar_titulo_dialogo", "Guardar previsões como...")
        )

        if caminho:
            try:
                df = pd.DataFrame({
                    self.textos.get("exportar_excel_coluna_previsao", "Previsão"): self.historico_previsoes,
                    self.textos.get("exportar_excel_coluna_versao", "Versão"): "v1.6",
                    self.textos.get("exportar_excel_coluna_data", "Data"): datetime.datetime.now().strftime("%d-%m-%Y")
                })
                df.to_excel(caminho, index=False)

                def exportar_para_pdf(previsoes, caminho_pdf_1):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                    pdf.set_font("DejaVu", size=12)

                    for idx, previsao in enumerate(previsoes, 1):
                        if isinstance(previsao, dict):
                            linha = (
                                    f"{idx}: " +
                                    self.textos.get("exportar_pdf_numeros",
                                                    "Números → {n1}, {n2}, {n3}, {n4}, {n5}").format(
                                        n1=previsao["N1"], n2=previsao["N2"], n3=previsao["N3"],
                                        n4=previsao["N4"], n5=previsao["N5"]
                                    ) + " | " +
                                    self.textos.get("exportar_pdf_estrelas", "Estrelas → {e1}, {e2}").format(
                                        e1=previsao["Estrela 1"], e2=previsao["Estrela 2"]
                                    )
                            )
                        else:
                            linha = f"{idx}: {previsao}"
                        pdf.cell(200, 10, linha, ln=1, align="L")

                    pdf.output(caminho_pdf_1)

                caminho_pdf = caminho.replace(".xlsx", ".pdf")
                exportar_para_pdf(self.historico_previsoes, caminho_pdf)

                messagebox.showinfo(
                    title=self.textos.get("exportar_titulo_dialogo", "Exportar"),
                    message=self.textos.get("exportar_sucesso", "Previsões exportadas com sucesso em Excel e PDF!")
                )

            except Exception as e:
                erro_txt = self.textos.get("exportar_erro", "Erro ao exportar:\n{erro}")
                messagebox.showerror(
                    title=self.textos.get("exportar_titulo_dialogo", "Exportar"),
                    message=erro_txt.replace("{erro}", str(e))
                )
