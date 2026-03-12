# rh-auto · Industrial Deal Intelligence (IDI)

Sistema de análise de contratos industriais com IA (OpenAI) — **dashboard Dash**.

## Requisitos

- Python 3.10+
- Chave da API OpenAI

## Instalação

```bash
cd idi_project
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# ou: .venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install -r dash_app/requirements.txt
```

## Configuração

Antes de rodar, defina a chave da OpenAI **no terminal**:

```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

Depois execute o app no **mesmo** terminal. (A chave não fica em nenhum arquivo do projeto.)

## Executar

```bash
python run.py
```
(ou `.venv/bin/python run.py` se não ativou o venv)

Acesse: **http://127.0.0.1:8050**

## Uso

1. No dashboard, use **Selecionar PDF** na barra lateral para enviar um contrato.
2. O sistema extrai o texto, analisa com OpenAI e calcula o score de risco (0–10).
3. São exibidos: cards de métricas, gráfico radar (financeiro/jurídico/operacional), gráfico de barras, multas, retenções, responsabilidades, cláusulas perigosas e sugestões. É possível consultar o histórico e comparar dois contratos.

## Estrutura

- `run.py` – **entrada principal** (inicia o dashboard na porta 8050)
- `dash_app/` – dashboard (layout, callbacks, gráficos, histórico)
- `app/` – lógica compartilhada (análise com IA, PDF, score híbrido)
- `config.py` – configurações
- `run_flask.py` – interface Flask antiga (porta 5000), opcional
