# RH Auto

Sistema de apoio à triagem de currículos desenvolvido como projeto acadêmico.

O RH Auto permite cadastrar os requisitos de uma vaga, processar vários currículos em PDF e gerar uma pontuação de compatibilidade para cada candidato. A proposta é ajudar profissionais de recrutamento a organizar um grande volume de candidaturas e identificar os perfis mais próximos dos requisitos informados.

> O sistema é uma ferramenta de apoio. A pontuação não deve ser usada como decisão final de contratação nem substituir a avaliação humana.

## Funcionalidades

- Cadastro das informações e dos requisitos de uma vaga
- Envio de múltiplos currículos em PDF
- Extração do texto dos documentos
- Análise dos currículos com inteligência artificial
- Comparação entre os requisitos da vaga e as informações encontradas
- Geração de score de compatibilidade
- Armazenamento local das análises
- Organização dos candidatos para revisão humana

## Fluxo da aplicação

1. O recrutador informa os requisitos da vaga.
2. Os currículos são enviados em formato PDF.
3. O sistema extrai o conteúdo dos documentos.
4. A inteligência artificial analisa as informações relevantes.
5. Cada currículo recebe um score de compatibilidade.
6. O recrutador revisa os resultados e realiza a avaliação final.

## Tecnologias

- Node.js
- Express
- SQLite, por meio do `better-sqlite3`
- API da OpenAI
- `pdf-parse` para leitura dos currículos
- Multer para upload dos arquivos
- dotenv para variáveis de ambiente
- CORS

## Objetivo do projeto

O objetivo é reduzir o trabalho repetitivo da triagem inicial sem retirar a responsabilidade do profissional de Recursos Humanos. A aplicação organiza informações e apresenta indicadores, mas não decide quem deve ou não ser contratado.

## Uso responsável da IA

Resultados produzidos por inteligência artificial podem conter erros, omissões ou interpretações inadequadas. Por isso:

- o score deve ser tratado apenas como um indicador;
- os currículos precisam ser revisados por uma pessoa;
- critérios discriminatórios não devem ser utilizados;
- dados pessoais devem ser protegidos;
- nenhuma contratação ou eliminação deve ocorrer automaticamente.

## Segurança e privacidade

Currículos contêm dados pessoais. Arquivos enviados, bancos de dados locais e variáveis de ambiente não devem ser versionados no Git. O projeto utiliza um arquivo `.gitignore` para impedir novos envios desses dados.

## Requisitos

- Node.js 18 ou superior
- npm
- Chave de API configurada por variável de ambiente
- Código-fonte da aplicação

## Status

Protótipo acadêmico em organização para demonstração e continuidade do desenvolvimento.

## Autor

Desenvolvido por João Vitor Roventini e colegas como projeto acadêmico.
