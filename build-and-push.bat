@echo off
echo 🔨 Fazendo build da imagem Docker...
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" build -t analise-fatura-nubank:latest .

echo 🏷️ Fazendo tag da imagem...
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" tag analise-fatura-nubank:latest fabioguidotti/analise-fatura-nubank:latest

echo 📦 Fazendo push da imagem para o Docker Hub...
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" push fabioguidotti/analise-fatura-nubank:latest

echo ✅ Build e push concluídos!
echo 🚀 Use o arquivo docker-compose.yml no Portainer
echo 💡 Para desenvolvimento local: docker-compose -f docker-compose.dev.yml up
echo 🌐 Imagem disponível em: https://hub.docker.com/r/fabioguidotti/analise-fatura-nubank
