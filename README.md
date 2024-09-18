# Gestão Financeira Pessoal - Fatura do Cartão Nubank

Este projeto é uma aplicação Streamlit para gerenciar e analisar faturas do cartão de crédito Nubank. Ele permite importar faturas em PDF, visualizar transações, realizar análises detalhadas e interagir com uma IA para obter insights sobre seus gastos.

## Funcionalidades

- Importação de faturas do Nubank em formato PDF
- Visualização e gerenciamento de transações
- Análises gráficas detalhadas dos gastos
- Gerenciamento de categorias de gastos
- Interação com IA para obter insights financeiros personalizados
- Sistema de migração de banco de dados com Alembic

## Requisitos

- Python 3.7+
- Bibliotecas Python (veja `requirements.txt`)

## Instalação

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Configure as variáveis de ambiente:
   Crie um arquivo `secrets.toml` na pasta `.streamlit` do projeto e adicione sua chave da API OpenAI:
   ```toml
   OPENAI_API_KEY = "sua_chave_api_aqui"
   ```

## Configuração do Banco de Dados

O projeto usa SQLite como banco de dados e Alembic para gerenciamento de migrações.

Verifique a configuração do banco de dados em `alembic.ini`:

## Uso

1. Inicie a aplicação Streamlit:
   ```
   streamlit run app.py
   ```

2. Abra seu navegador e acesse `http://localhost:8501`

## Estrutura do Projeto

- `app.py`: Arquivo principal da aplicação Streamlit
- `database.py`: Funções para interação com o banco de dados SQLite
- `ai_utils.py`: Funções relacionadas à IA e processamento de linguagem natural usando OpenAI
- `data_processing.py`: Funções para processamento de dados e importação de faturas PDF
- `visualizations.py`: Funções para criar visualizações e gráficos interativos com Plotly
- `alembic/`: Diretório contendo as migrações do banco de dados
  - `env.py`: Configuração do ambiente Alembic
  - `versions/`: Scripts de migração do banco de dados
- `.streamlit/`: Diretório contendo configurações do Streamlit
  - `secrets.toml`: Arquivo para armazenar segredos e chaves de API

## Funcionalidades Detalhadas

1. **Importação de Faturas**: 
   - Suporta múltiplos arquivos PDF
   - Extração inteligente de transações usando IA

2. **Visualização e Gerenciamento de Dados**:
   - Tabela interativa com opções de ordenação
   - Funcionalidades de exclusão de transações individuais ou em lote

3. **Análises**:
   - Resumo financeiro
   - Gráficos de evolução de gastos (semanal e mensal)
   - Distribuição de gastos por categoria
   - Top 10 maiores gastos
   - Padrões de gastos (frequência e dia da semana)

4. **Gerenciamento de Categorias**:
   - Interface para adicionar, editar e excluir categorias

5. **Interação com IA**:
   - Chat interativo para análises personalizadas e insights financeiros

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter pull requests ou abrir issues para sugerir melhorias ou reportar bugs.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.