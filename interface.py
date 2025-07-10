from tkinter import ttk, messagebox, filedialog
from simulador import EuroMillionsMasterWizard
import pandas as pd

class InterfaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EuroMillions Master Wizard")
        self.root.geometry("520x500")

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

        self.label_titulo = ttk.Label(self.root)
        self.label = ttk.Label(self.root)
        self.entrada = ttk.Entry(self.root)
        self.combo_posicao = ttk.Combobox(self.root, values=list(self.posicoes.keys()), state="readonly")
        self.botao_prever = ttk.Button(self.root)
        self.botao_chave = ttk.Button(self.root)
        self.botao_estatisticas = ttk.Button(self.root)
        self.botao_importar = ttk.Button(self.root)
        self.botao_exportar = ttk.Button(self.root)
        self.resultado = ttk.Label(self.root)

        self.criar_widgets()

    def criar_widgets(self):
        self.label_titulo.config(text="🔢 EuroMillions Master Wizard", font=("Segoe UI", 16, "bold"))
        self.label_titulo.pack(pady=10)

        self.label.config(text="Número atual:")
        self.label.pack(pady=5)

        self.entrada.pack()

        ttk.Label(self.root, text="Escolhe a posição:").pack(pady=5)
        self.combo_posicao.current(0)
        self.combo_posicao.pack()

        self.botao_prever.config(text="Prever próximo", command=self.prever)
        self.botao_prever.pack(pady=10)

        self.botao_chave.config(text="Gerar chave completa", command=self.gerar_chave)
        self.botao_chave.pack(pady=5)

        self.botao_estatisticas.config(text="📊 Ver estatísticas", command=self.mostrar_estatisticas)
        self.botao_estatisticas.pack(pady=5)

        self.botao_importar.config(text="📁 Importar ficheiro Excel", command=self.importar_ficheiro)
        self.botao_importar.pack(pady=5)

        self.botao_exportar.config(text="💾 Exportar previsões", command=self.exportar_previsoes)
        self.botao_exportar.pack(pady=5)

        self.resultado.config(text="", font=("Segoe UI", 11))
        self.resultado.pack(pady=20)

    def mostrar_estatisticas(self):
        posicao_nome = self.combo_posicao.get()
        coluna = self.posicoes[posicao_nome]

        try:
            stats = self.simulador.estatisticas_por_coluna(coluna)
            texto = f"📊 Estatísticas para {posicao_nome}:\n"
            texto += f"Média: {stats['media']}\n"
            texto += "Top 10 mais frequentes:\n"
            for num, freq in stats["top_10"].items():
                texto += f"  {num}: {freq}x\n"

            self.resultado.config(text=texto)
            self.historico_previsoes.append(texto)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível calcular estatísticas:\n{e}")

    def prever(self):
        try:
            valor = int(self.entrada.get())
            posicao_nome = self.combo_posicao.get()
            coluna = self.posicoes[posicao_nome]

            if coluna not in self.simulador.transicoes:
                self.simulador.gerar_cadeia_markov(coluna)

            origem, previsao = self.prever_com_alternativa(coluna, valor)
            if previsao:
                texto = f"🔮 Mais provável após {origem} ({posicao_nome}): {previsao}"
                self.resultado.config(text=texto)
                self.historico_previsoes.append(texto)
            else:
                self.resultado.config(text="Nenhuma transição disponível.")
        except ValueError:
            messagebox.showerror("Erro", "Insere um número válido.")

    def prever_com_alternativa(self, coluna, valor_atual):
        trans = self.simulador.transicoes.get(coluna, {})
        if valor_atual in trans:
            return valor_atual, self.simulador.prever_por_markov(coluna, valor_atual)

        candidatos = sorted(trans.keys(), reverse=True)
        for candidato in candidatos:
            if isinstance(candidato, int) and candidato < valor_atual:
                return candidato, self.simulador.prever_por_markov(coluna, candidato)

        return None, None

    def gerar_chave(self):
        numeros, estrelas = self.simulador.gerar_chave_por_markov()
        texto = f"🔐 Chave prevista:\nNúmeros: {numeros}\nEstrelas: {estrelas}"
        self.resultado.config(text=texto)
        self.historico_previsoes.append(texto)

    def importar_ficheiro(self):
        caminho = filedialog.askopenfilename(
            title="Seleciona o ficheiro Excel",
            filetypes=[("Ficheiros Excel", "*.xlsx *.xls")]
        )
        if caminho:
            try:
                self.simulador = EuroMillionsMasterWizard("dados/resultados_euromilhoes.xlsx")
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