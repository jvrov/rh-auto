# rh-auto · Industrial Deal Intelligence (IDI)

Sistema de análise de contratos industriais com IA.

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
```

## Configuração

Defina a chave da API OpenAI:

```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

## Executar

```bash
python run.py
```

Acesse: http://127.0.0.1:5000

## Uso

1. Na página inicial, escolha um contrato em PDF e clique em **Analisar contrato**.
2. O sistema extrai o texto, analisa com IA e calcula o score de risco (0–10).
3. Na página de resultado são exibidos: multas, retenções, responsabilidades, cláusulas perigosas e sugestões de negociação.

## Estrutura

- `app/` – lógica da aplicação (rotas, PDF, análise, score, modelos)
- `templates/` – páginas HTML
- `uploads/` – PDFs enviados
- `config.py` – configurações
- `run.py` – entrada da aplicação
