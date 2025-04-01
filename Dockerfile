FROM python:3.13.1
 
# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
 
# Definir o diretório de trabalho
WORKDIR /app
 
# Copiar os arquivos para o contêiner
COPY . .
 
# Instalar bibliotecas Python
RUN pip install --no-cache-dir -r requirements.txt
 
# Expor a porta usada pelo app (ajuste se não for 8080)
EXPOSE 8080
 
# Comando padrão
CMD ["python", "app.py"]