📦 EuroMillions Master Wizard — Changelog v1.3
Data de lançamento: 15/07/2025
Versão: v1.3

🔧 Novidades e Melhorias:

🪄 Interação inteligente com previsão
- Adicionado sistema de escolha: o utilizador pode comparar a chave oficial com:
- A sequência prevista gerada pelo modelo (Markov)
- Uma sequência jogada manualmente inserida no momento

🧮 Comparação segura com chave oficial
- Inserção manual da chave oficial via Tkinter simpledialog
- Correções na contagem de acertos (números e estrelas), incluindo deteção do par completo de estrelas

🧠 Consolidação da previsão
- A função prever_sequencia() foi refatorada para garantir consistência:
- Os números e estrelas previstas são únicas e sincronizadas
- A previsão usa pares de estrelas mais frequentes e transições Markov robustas

📊 Análise estatística de previsões
- Cada número e estrela prevista é classificado como:
- 🔴 Quente — acima da média histórica
- 🟡 Morno — frequência média
- 🔵 Frio — abaixo da média
- Visualização direta na área de histórico

🛡️ Tratamento de exceções e cancelamentos
- Cancelar caixas de entrada (simpledialog) já não causa erros — sistema responde com mensagens claras e sem interrupções

🧼 Outros ajustes e melhorias
- Melhor gestão do botão “Mostrar acertos” com lógica integrada
- Preparação para futuras comparações em lote e exportações
- Correções de interface e inserção de mensagens contextuais
