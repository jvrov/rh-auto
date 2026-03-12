# AI Contract Risk Analyzer — Dashboard Dash

Dashboard profissional para análise de risco contratual com IA.

## Tecnologias

- Python, Dash, Dash Bootstrap Components, Plotly
- pdfplumber (extração de texto), OpenAI (análise)
- SQLite (histórico em `contracts_history`)

## Como rodar

Na pasta **idi_project** (raiz do projeto):

```bash
# Ativar ambiente e instalar dependências do dashboard
pip install -r dash_app/requirements.txt

# Definir chave da OpenAI
export OPENAI_API_KEY="sua-chave"

# Subir o dashboard
python run.py
```

Ou, a partir de **dash_app**:

```bash
cd idi_project/dash_app
PYTHONPATH=.. python app.py
```

Acesse: **http://127.0.0.1:8050**

## Estrutura

- `app.py` — Inicializa o servidor Dash
- `layout.py` — Interface (sidebar, cards, gráficos, seções)
- `callbacks.py` — Upload, histórico, comparação
- `analyzer.py` — Chama a IA e devolve resultado no formato do dashboard
- `pdf_reader.py` — Extração de texto do PDF
- `database.py` — SQLite, tabela `contracts_history`
- `charts.py` — Gráfico radar, barras, radar comparativo

## Funcionalidades

1. **Upload** — Enviar PDF → extração → análise IA → exibição
2. **Cards** — Score, nível, nº cláusulas perigosas, nº multas (cores por risco)
3. **Radar** — Risco financeiro, jurídico, operacional (0–10)
4. **Barras** — Quantidade por categoria
5. **Seções** — Multas, retenções, responsabilidades (contratada/contratante), cláusulas (texto + motivo), sugestões
6. **Histórico** — Dropdown para rever contratos analisados
7. **Comparação** — Selecionar dois contratos e ver radar comparativo
