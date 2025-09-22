@echo off
echo 🔨 Fazendo build da imagem Docker...
docker build -t analise-fatura-nubank:latest .

echo 📦 Fazendo push da imagem para o registry...
echo ⚠️  Certifique-se de que a imagem foi enviada para o registry antes de fazer o deploy no Portainer

echo ✅ Build concluído!
echo 📋 Para fazer push manual: docker push analise-fatura-nubank:latest
echo 🚀 Use o arquivo docker-compose.yml no Portainer
echo 💡 Para desenvolvimento local: docker-compose -f docker-compose.dev.yml up
