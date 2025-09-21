# 🚀 Guia de Deploy

## 📁 Arquivo Único

### `docker-compose.yml`
- **Uso**: Desenvolvimento local E produção no Portainer
- **Comando local**: `docker-compose up`
- **Deploy Portainer**: Via interface web
- **Características**: 
  - Build automático com `build.context` e `build.dockerfile`
  - Configurações híbridas (funciona em ambos os ambientes)
  - Volume `./uploads` para desenvolvimento local

## 🔧 Processo de Deploy

### 1. Desenvolvimento Local
```bash
docker-compose up
```

### 2. Deploy no Portainer (Build Automático)
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

## ✨ Vantagens do Build Automático

- 🔄 **Deploy automático**: A cada push no GitHub
- 🏗️ **Build automático**: Portainer faz o build da imagem
- 📦 **Sem registry**: Não precisa de Docker Hub ou registry privado
- 🚀 **Deploy rápido**: Apenas configure uma vez

## 🔄 Workflow Recomendado

1. **Desenvolvimento**: `docker-compose up` (local)
2. **Commit e Push**: `git push origin main`
3. **Deploy automático**: Portainer detecta mudanças e faz rebuild
4. **Monitoramento**: Acompanhe logs no Portainer

## ⚠️ Importante

- As variáveis de ambiente devem estar configuradas no Portainer
- A rede `traefik-central_traefik-public` deve existir
- O Portainer precisa ter acesso ao repositório GitHub
