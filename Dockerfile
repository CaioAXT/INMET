# Usar uma imagem base do Python
FROM python:3.13.1
 
# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
 
# Definir o diretório de trabalho
WORKDIR /
 
# Copiar os arquivos necessários para o contêiner
COPY . /app
 
# Instalar bibliotecas Python
RUN pip install --no-cache-dir -r requirements.txt
 
# Expor a porta caso seja necessário
EXPOSE 8080
 
# Definir o comando padrão para executar o bot
CMD ["python", "app.py"]

 