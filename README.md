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
- PostgreSQL

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   Crie um arquivo `.env` na raiz do projeto e adicione suas configurações:
   ```
   OPENAI_API_KEY=chave da api openai
   DB_HOST=host do seu banco de dados
   DB_PORT=porta do seu banco de dados
   DB_NAME=nome do seu banco de dados
   DB_USER=usuario do seu banco de dados
   DB_PASSWORD=senha do seu banco de dados
   ```

## Configuração do Banco de Dados

O projeto usa PostgreSQL como banco de dados e Alembic para gerenciamento de migrações.

1. Crie um banco de dados PostgreSQL para o projeto.

2. Verifique a configuração do banco de dados em `alembic.ini`.

3. Execute as migrações:
   ```
   alembic upgrade head
   ```

## Uso

1. Inicie a aplicação Streamlit:
   ```
   streamlit run app.py
   ```

2. Abra seu navegador e acesse `http://localhost:8501`

## Estrutura do Projeto

- `app.py`: Arquivo principal da aplicação Streamlit
- `database.py`: Funções para interação com o banco de dados PostgreSQL
- `models.py`: Modelos de dados do banco de dados
- `ai_utils.py`: Funções relacionadas à IA e processamento de linguagem natural
- `data_processing.py`: Funções para processamento de dados e importação de faturas
- `auth.py`: Funções para autenticação de usuários
- `alembic/`: Diretório contendo as migrações do banco de dados
- `tela_*.py`: Arquivos contendo as diferentes telas da aplicação
- `requirements.txt`: Arquivo contendo as dependências do projeto

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