# 🚀 Guia de Deploy

## 📁 Arquivos Separados

### `docker-compose.yml` (Produção)
- **Uso**: Deploy no Portainer
- **Características**: 
  - Usa `image: fabioguidotti/analise-fatura-nubank:latest` (Docker Hub)
  - Configurações de `deploy` para Docker Swarm
  - Sem volume `./uploads` (não suportado no Swarm)

### `docker-compose.dev.yml` (Desenvolvimento)
- **Uso**: Desenvolvimento local
- **Comando**: `docker-compose -f docker-compose.dev.yml up`
- **Características**: 
  - Usa `build: .` para build automático
  - Inclui volume `./uploads` para desenvolvimento
  - Configurações de `container_name` e `restart`

## 🔧 Processo de Deploy

### 1. Desenvolvimento Local
```bash
docker-compose -f docker-compose.dev.yml up
```

### 2. Build da Imagem
```bash
# Windows
build-and-push.bat

# Linux/Mac
docker build -t analise-fatura-nubank:latest .
```

### 3. Push para Registry (se necessário)
```bash
docker push analise-fatura-nubank:latest
```

### 4. Deploy no Portainer
1. Vá em **Stacks** → **Add stack**
2. Escolha **Repository**
3. Configure:
   - **Repository URL**: `https://github.com/seu-usuario/analise-fatura-nubank-ia`
   - **Compose path**: `docker-compose.yml`
   - **Branch**: `main` (ou sua branch principal)
4. Configure as variáveis de ambiente:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   DB_HOST=seu_host_do_banco
   DB_PORT=5432
   DB_NAME=nome_do_banco
   DB_USER=usuario_do_banco
   DB_PASSWORD=senha_do_banco
   ```
5. **Deploy**

## 🔄 Workflow Recomendado

1. **Desenvolvimento**: `docker-compose -f docker-compose.dev.yml up`
2. **Teste**: Teste localmente
3. **Build**: `build-and-push.bat`
4. **Push**: `git push origin main`
5. **Deploy**: Portainer usa a imagem pré-construída

## ⚠️ Importante

- A imagem `analise-fatura-nubank:latest` deve existir no servidor
- As variáveis de ambiente devem estar configuradas no Portainer
- A rede `traefik-central_traefik-public` deve existir
