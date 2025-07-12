import pandas as pd
from collections import defaultdict

class EuroMillionsMasterWizard:
    def __init__(self, caminho_excel):
        self.df = pd.read_excel(caminho_excel, skiprows=1)
        self.col_numeros = [1, 2, 3, 4, 5]
        self.col_estrelas = ["Star 1", "Star 2"]
        self.transicoes = {}  # Armazena transições por coluna

    # 🧠 Gera a cadeia de Markov para uma coluna (posição)
    def gerar_cadeia_markov(self, coluna):
        transicoes = defaultdict(lambda: defaultdict(int))
        valores = self.df[coluna].dropna().astype(int).tolist()

        for i in range(len(valores) - 1):
            atual = valores[i]
            seguinte = valores[i + 1]
            transicoes[atual][seguinte] += 1

        transicoes_percentuais = {}
        for origem, destinos in transicoes.items():
            total = sum(destinos.values())
            transicoes_percentuais[origem] = {
                destino: round((freq / total) * 100, 2)
                for destino, freq in destinos.items()
            }

        self.transicoes[coluna] = transicoes_percentuais

    # 🔮 Prever o valor provável após um número
    def prever_por_markov(self, coluna, valor_atual):
        trans = self.transicoes.get(coluna, {})
        if valor_atual not in trans:
            return None
        return max(trans[valor_atual], key=trans[valor_atual].get)

    # 🎯 Filtrar transições para manter apenas certos valores como destino
    def filtrar_transicoes_por_valor(self, coluna, valores_desejados):
        transicoes_originais = self.transicoes.get(coluna, {})
        filtradas = {}
        for origem, destinos in transicoes_originais.items():
            candidatos = {
                destino: prob for destino, prob in destinos.items()
                if destino in valores_desejados
            }
            if candidatos:
                filtradas[origem] = candidatos
        return filtradas

    # 📊 Mostrar colunas disponíveis no DataFrame
    def mostrar_colunas(self):
        print("📋 Colunas disponíveis:", self.df.columns.tolist())

    # 🧪 Obter todos os valores únicos de uma coluna
    def valores_unicos(self, coluna):
        return sorted(self.df[coluna].dropna().astype(int).unique().tolist())

    def estatisticas_por_coluna(self, coluna):
        serie = self.df[coluna].dropna().astype(int)
        frequencias = serie.value_counts().sort_index()
        media = round(serie.mean(), 2)
        top = frequencias.sort_values(ascending=False).head(10)

        return {
            "frequencias": frequencias.to_dict(),
            "media": media,
            "top_10": top.to_dict()
        }