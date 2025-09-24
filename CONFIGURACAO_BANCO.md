# Configuração do Banco de Dados

## Problema de Autenticação PostgreSQL

O erro `FATAL: password authentication failed for user "analise-fatura-ia"` indica que a aplicação está tentando se conectar ao PostgreSQL, mas as credenciais estão incorretas ou as variáveis de ambiente não estão definidas.

## Soluções

### 1. Usar SQLite (Recomendado para desenvolvimento local)

A aplicação foi modificada para usar SQLite automaticamente quando as variáveis de ambiente do PostgreSQL não estão definidas. Para usar SQLite:

1. **Não crie um arquivo `.env`** ou deixe as variáveis de banco comentadas
2. A aplicação criará automaticamente um arquivo `analise_fatura.db` local
3. Não é necessário configuração adicional

### 2. Configurar PostgreSQL (Para produção)

Se você quiser usar PostgreSQL, crie um arquivo `.env` na raiz do projeto com:

```env
# Configurações do Banco de Dados PostgreSQL
DB_HOST=85.209.92.145
DB_PORT=5432
DB_NAME=analise_fatura_db
DB_USER=analise-fatura-ia
DB_PASSWORD=sua_senha_correta_aqui

# Configurações da API OpenAI
OPENAI_API_KEY=sua_chave_da_api_openai_aqui
```

**Importante:** Substitua `sua_senha_correta_aqui` pela senha real do banco de dados.

### 3. Verificar Credenciais do PostgreSQL

Se você tem acesso ao servidor PostgreSQL `85.209.92.145`, verifique:

1. Se o usuário `analise-fatura-ia` existe
2. Se a senha está correta
3. Se o usuário tem permissões para acessar o banco `analise_fatura_db`
4. Se o banco de dados existe

## Como a Aplicação Funciona Agora

1. **Primeiro**: Tenta conectar ao PostgreSQL usando as variáveis de ambiente
2. **Se falhar**: Usa SQLite automaticamente como fallback
3. **Logs**: A aplicação mostra qual banco está sendo usado

## Testando a Conexão

Para testar se a conexão está funcionando, execute:

```python
from database import testar_conexao
testar_conexao()
```

## Arquivos Modificados

- `database.py`: Adicionada verificação de variáveis de ambiente
- `env.example`: Atualizado com instruções mais claras
