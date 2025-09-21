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

- Python 3.7+ (para desenvolvimento local)
- Docker e Docker Compose (para produção)
- Bibliotecas Python (veja `requirements.txt`)
- PostgreSQL

## Instalação

### Opção 1: Docker (Recomendado para Produção)

O projeto está configurado para rodar no Portainer usando Docker Compose.

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. Configure as variáveis de ambiente:
   Copie o arquivo `env.example` para `.env` e configure as variáveis:
   ```bash
   cp env.example .env
   ```

   Edite o arquivo `.env` com suas configurações:
   ```env
   # Configurações do Banco de Dados PostgreSQL
   DB_HOST=postgres
   DB_PORT=5432
   DB_NAME=analise_fatura_db
   DB_USER=analise_fatura_user
   DB_PASSWORD=sua_senha_super_segura_aqui

   # Configurações da API OpenAI
   OPENAI_API_KEY=sua_chave_da_api_openai_aqui
   ```

3. Deploy no Portainer:
   - Acesse seu Portainer
   - Vá para "Stacks" no menu lateral
   - Clique em "Add stack"
   - Cole o conteúdo do arquivo `docker-compose.yml`
   - Configure as variáveis de ambiente no Portainer ou use o arquivo `.env`
   - Deploy a stack

4. Acesse a aplicação em: `https://analise-fatura.seudominio.com`

   **Nota**: Se você quiser usar um domínio diferente, edite a linha 28 do `docker-compose.yml`:
   ```yaml
   - "traefik.http.routers.analise-fatura.rule=Host(`seu-dominio.com`)"
   ```

### Opção 2: Desenvolvimento Local

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

4. Configure o banco de dados:
   - Crie um banco de dados PostgreSQL para o projeto
   - Execute as migrações: `alembic upgrade head`

5. Inicie a aplicação:
   ```
   streamlit run app.py
   ```

6. Abra seu navegador e acesse `http://localhost:8501`

## Estrutura do Projeto

### Arquivos da Aplicação
- `app.py`: Arquivo principal da aplicação Streamlit
- `database.py`: Funções para interação com o banco de dados PostgreSQL
- `models.py`: Modelos de dados do banco de dados
- `ai_utils.py`: Funções relacionadas à IA e processamento de linguagem natural
- `data_processing.py`: Funções para processamento de dados e importação de faturas
- `auth.py`: Funções para autenticação de usuários
- `alembic/`: Diretório contendo as migrações do banco de dados
- `tela_*.py`: Arquivos contendo as diferentes telas da aplicação
- `requirements.txt`: Arquivo contendo as dependências do projeto

### Arquivos Docker
- `Dockerfile`: Configuração da imagem Docker para a aplicação Streamlit
- `docker-compose.yml`: Orquestração dos serviços (app, PostgreSQL)
- `env.example`: Arquivo de exemplo com as variáveis de ambiente necessárias
- `init-scripts/01-init-db.sh`: Script para inicializar o banco de dados

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

## Troubleshooting

### Docker/Portainer

#### Verificar Logs
```bash
# Logs da aplicação
docker logs analise-fatura-nubank

# Logs do PostgreSQL
docker logs analise-fatura-postgres
```

#### Verificar Status dos Serviços
```bash
docker ps
```

#### Acessar o Banco de Dados
```bash
docker exec -it analise-fatura-postgres psql -U analise_fatura_user -d analise_fatura_db
```

### Backup e Restore

#### Backup do PostgreSQL
```bash
docker exec analise-fatura-postgres pg_dump -U analise_fatura_user analise_fatura_db > backup.sql
```

#### Restore do PostgreSQL
```bash
docker exec -i analise-fatura-postgres psql -U analise_fatura_user -d analise_fatura_db < backup.sql
```

### Problemas Comuns

1. **Erro de conexão com banco de dados**: Verifique se as variáveis de ambiente estão configuradas corretamente
2. **Aplicação não carrega**: Verifique se o Traefik está configurado corretamente e se o subdomínio está apontando para o servidor
3. **Erro de migração**: Execute manualmente `alembic upgrade head` dentro do container da aplicação

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter pull requests ou abrir issues para sugerir melhorias ou reportar bugs.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.