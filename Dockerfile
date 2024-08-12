# Use uma imagem base do Python
FROM python:3.9-slim

# Defina o diretório de trabalho na imagem
WORKDIR /app

# Copie o arquivo de requisitos e instale as dependências
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código da aplicação para o diretório de trabalho
COPY . .


# Exponha a porta que o Gunicorn usará
EXPOSE 8000

# Comando para iniciar a aplicação usando Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
