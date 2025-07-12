import pandas as pd
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import ttk, messagebox, filedialog
from simulador import EuroMillionsMasterWizard
from scipy.stats import poisson

class InterfaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EuroMillions Master Wizard v1.1")
        self.root.geometry("540x520")

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

        # Título
        self.label_titulo = ttk.Label(
            self.root,
            text="🔢 EuroMillions Master Wizard v1.1",
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

        self.tabs.add(self.tab_previsoes, text="🔮 Previsões")
        self.tabs.add(self.tab_acertos, text="✅ Acertos")
        self.tabs.add(self.tab_estatisticas, text="📊 Estatísticas")
        self.tabs.add(self.tab_utilitarios, text="📁 Utilitários")

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
        # Canvas para mostrar gráfico
        self.canvas_poisson = tk.Canvas(self.tab_estatisticas, width=720, height=440)  # ✅ canvas puro
        # Importar/exportar
        self.botao_importar = ttk.Button(self.tab_utilitarios)
        self.botao_exportar = ttk.Button(self.tab_utilitarios)

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

    def criar_widgets(self):
        # 🔮 Previsão sequencial completa

        ttk.Label(
            self.tab_previsoes,
            text="Prever chave completa com Cadeia de Markov:",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=10)

        self.botao_multi_prever.config(
            text="🔮 Prever sequência completa",
            command=self.prever_sequencia
        )
        self.botao_multi_prever.pack(pady=5)

        # ✅ Comparação de acertos

        ttk.Label(
            self.tab_acertos,
            text="Comparar previsão com chave oficial:",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=10)

        self.botao_comparar.config(
            text="🧮 Mostrar acertos",
            command=self.comparar_com_chave_oficial
        )
        self.botao_comparar.pack(pady=5)

        # 📊 Estatísticas — Posição
        ttk.Label(
            self.tab_estatisticas,
            text="Seleciona a posição:",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(15, 5))

        self.combo_estatistica.pack(pady=5)
        self.combo_estatistica.current(0)

        self.botao_estatisticas.config(
            text="📊 Consultar",
            command=self.mostrar_estatisticas
        )
        self.botao_estatisticas.pack(pady=(5, 15))

        # 📊 Título da secção Poisson
        ttk.Label(
            self.tab_estatisticas,
            text="Distribuição de Poisson (últimos 100 sorteios):",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(5, 5))

        self.botao_poisson.config(
            text="📊 Números",
            command=self.mostrar_poisson
        )
        self.botao_poisson.pack(pady=5)

        self.botao_poisson_estrelas.config(
            text="🌟 Estrelas",
            command=self.mostrar_poisson_estrelas
        )
        self.botao_poisson_estrelas.pack(pady=5)

        # 📈 Canvas para exibir gráfico (caso uses TkAgg ou substitua por plt.show())
        self.canvas_poisson.pack(pady=(10, 15))

        # 📁 Utilitários

        ttk.Label(
            self.tab_utilitarios,
            text="Opções adicionais:",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=10)

        self.botao_importar.config(text="📁 Importar ficheiro Excel",command=self.importar_ficheiro)
        self.botao_importar.pack(pady=10)

        self.botao_exportar.config(text="💾 Exportar previsões",command=self.exportar_previsoes)
        self.botao_exportar.pack(pady=5)

    def mostrar_estatisticas(self):
        posicao_nome = self.combo_estatistica.get()
        if not posicao_nome:
            messagebox.showinfo("Info", "Seleciona uma posição para visualizar estatísticas.")
            return

        coluna = self.posicoes[posicao_nome]

        try:
            stats = self.simulador.estatisticas_por_coluna(coluna)
            texto = f"📊 Estatísticas para {posicao_nome}:\n"
            texto += f"Média: {stats['media']}\n"
            texto += "Top 10 mais frequentes:\n"
            for num, freq in stats["top_10"].items():
                texto += f"  {num}: {freq}x\n"

            self.texto_historico.insert("end", texto + "\n\n")
            self.texto_historico.see("end")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível calcular estatísticas:\n{e}")

    def mostrar_poisson(self):
        try:
            # Lê o ficheiro
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

            # Limpar Canvas anterior
            for child in self.canvas_poisson.winfo_children():
                child.destroy()

            # Criar gráfico ampliado
            fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=100)
            cmap = plt.get_cmap("viridis")

            # Índice da barra mais frequente
            max_index = np.argmax(observadas)

            # Paleta de cores com destaque em 'tomato' para o mais frequente
            colors = [
                "tomato" if i == max_index else cmap(i / len(valores))
                for i in range(len(valores))
            ]

            # Gráfico de barras observadas
            ax.bar(valores, observadas, color=colors, label="Frequência Observada")

            # 👉 Rótulo numérico em cada barra
            for i, v in enumerate(observadas):
                ax.text(valores[i], v + 0.5, str(v), ha="center", fontsize=8)

            # Curva esperada de Poisson
            ax.plot(valores, esperada, "r--", linewidth=2, label="Poisson Esperada")

            # Estilo visual
            ax.set_title("Distribuição de Poisson — Últimos 100 sorteios")
            ax.set_xlabel("Número")
            ax.set_ylabel("Ocorrências")
            ax.legend()
            ax.grid(alpha=0.3)
            plt.show()  # 👉 Abre o gráfico numa janela separada

            # Mostrar resumo textual no histórico
            texto_resumo = f"📈 Média esperada por número: {lambda_val:.2f}\n"
            texto_resumo += f"🔍 Número mais frequente: {valores[np.argmax(observadas)]} ({max(observadas)}x)\n"
            self.texto_historico.insert("end", texto_resumo + "\n")
            self.texto_historico.see("end")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar gráfico de Poisson:\n{e}")

    def mostrar_poisson_estrelas(self):
        try:
            # Lê o ficheiro
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

            # Criar gráfico
            fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=100)
            cmap = plt.get_cmap("plasma")
            max_index = np.argmax(observadas)

            colors = [
                "gold" if i == max_index else cmap(i / len(valores))
                for i in range(len(valores))
            ]

            ax.bar(valores, observadas, color=colors, label="Frequência Observada")

            for i, v in enumerate(observadas):
                ax.text(valores[i], v + 0.5, str(v), ha="center", fontsize=8)

            ax.plot(valores, esperada, "r--", linewidth=2, label="Poisson Esperada")

            ax.set_title("Distribuição de Poisson — Estrelas (últimos 100 sorteios)")
            ax.set_xlabel("Estrela")
            ax.set_ylabel("Ocorrências")
            ax.legend()
            ax.grid(alpha=0.3)

            # Mostrar em janela separada
            plt.show()

            # Texto informativo no histórico
            texto = f"🌟 Média esperada por estrela: {lambda_val:.2f}\n"
            texto += f"✨ Estrela mais frequente: {valores[max_index]} ({max(observadas)}x)\n"
            self.texto_historico.insert("end", texto + "\n")
            self.texto_historico.see("end")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar gráfico de Poisson (estrelas):\n{e}")

    def prever_sequencia(self):
        previsoes = {}

        for nome, coluna in self.posicoes.items():
            # Garante que há transições geradas
            if coluna not in self.simulador.transicoes:
                self.simulador.gerar_cadeia_markov(coluna)

            trans = self.simulador.transicoes.get(coluna, {})
            if not trans:
                previsoes[nome] = "?"
                continue

            try:
                origem = max(trans.items(), key=lambda item: sum(item[1].values()))[0]
                previsao = self.simulador.prever_por_markov(coluna, origem)
                previsoes[nome] = previsao if previsao is not None else "?"
            except ValueError:
                previsoes[nome] = "?"

        # 🔮 Renderiza o texto final
        numeros = ", ".join(str(previsoes.get(f"N{i}", "?")) for i in range(1, 6))
        estrelas = ", ".join([
            str(previsoes.get("Estrela 1", "?")),
            str(previsoes.get("Estrela 2", "?"))
        ])

        texto = (
            f"🔮 Sequência prevista com Markov ordem 1:\n"
            f"Números: {numeros}\nEstrelas: {estrelas}"
        )
        self.texto_historico.insert("end", texto + "\n\n")
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

            numeros = [int(ultimo[col]) for col in col_numeros]
            estrelas = [int(ultimo[col]) for col in col_estrelas]
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
        previsao_completa = {}
        for nome, coluna in self.posicoes.items():
            if coluna not in self.simulador.transicoes:
                self.simulador.gerar_cadeia_markov(coluna)

            trans = self.simulador.transicoes.get(coluna, {})
            if not trans:
                previsao_completa[nome] = "?"
                continue

            try:
                origem = max(trans, key=lambda k: sum(trans[k].values()))
                previsao = self.simulador.prever_por_markov(coluna, origem)
                previsao_completa[nome] = previsao if previsao is not None else "?"
            except ValueError:
                previsao_completa[nome] = "?"

        # Obter chave oficial dinâmica
        numeros_oficiais, estrelas_oficiais, data_txt = self.obter_chave_oficial()
        if not numeros_oficiais or not estrelas_oficiais:
            return

        # Separar previsão
        numeros_previstos = [
            previsao_completa.get("N1"),
            previsao_completa.get("N2"),
            previsao_completa.get("N3"),
            previsao_completa.get("N4"),
            previsao_completa.get("N5")
        ]
        estrelas_previstas = [
            previsao_completa.get("Estrela 1"),
            previsao_completa.get("Estrela 2")
        ]

        total_n = sum(n in numeros_oficiais for n in numeros_previstos)
        total_e = sum(e in estrelas_oficiais for e in estrelas_previstas)

        # Inserir no histórico com etiquetas visuais
        self.texto_historico.insert("end", f"🧮 Comparação com chave oficial ({data_txt}):\n", "titulo")
        self.texto_historico.insert("end", "🔮 Previsão: ")

        for num in numeros_previstos:
            if num in numeros_oficiais:
                self.texto_historico.insert("end", f"{num} ", "numero_certo")
            else:
                self.texto_historico.insert("end", f"{num} ")

        self.texto_historico.insert("end", "+ ")

        for estrela in estrelas_previstas:
            if estrela in estrelas_oficiais:
                self.texto_historico.insert("end", f"{estrela} ", "estrela_certa")
            else:
                self.texto_historico.insert("end", f"{estrela} ")

        self.texto_historico.insert("end",
                                    f"\n🎯 Chave oficial: {', '.join(str(n) for n in numeros_oficiais)} + {', '.join(str(e) for e in estrelas_oficiais)}\n")
        self.texto_historico.insert("end", f"✅ Acertos: {total_n} números, {total_e} estrelas\n\n")
        self.texto_historico.see("end")

        # Resultado também no label
        texto_resultado = f"🔮 Previsão: {', '.join(str(n) for n in numeros_previstos)} + {', '.join(str(e) for e in estrelas_previstas)}\n"
        texto_resultado += f"🎯 Chave oficial: {', '.join(str(n) for n in numeros_oficiais)} + {', '.join(str(e) for e in estrelas_oficiais)}\n"
        texto_resultado += f"✅ Acertos: {total_n} números, {total_e} estrelas"

        self.resultado.config(text=texto_resultado)

    def importar_ficheiro(self):
        caminho = filedialog.askopenfilename(
            title="Seleciona o ficheiro Excel",
            filetypes=[("Ficheiros Excel", "*.xlsx *.xls")]
        )
        if caminho:
            try:
                self.simulador = EuroMillionsMasterWizard(caminho)
                self.resultado.config(text="✅ Ficheiro carregado com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar ficheiro:\n{e}")

    def exportar_previsoes(self):
        if not self.historico_previsoes:
            messagebox.showinfo("Info", "Ainda não há previsões para exportar.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Ficheiros Excel", "*.xlsx")],
            title="Guardar previsões como..."
        )
        if caminho:
            try:
                df = pd.DataFrame({"Previsões": self.historico_previsoes})
                df.to_excel(caminho, index=False)
                messagebox.showinfo("Sucesso", "Previsões exportadas com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar:\n{e}")