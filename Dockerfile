# Use uma imagem base oficial do Python.
FROM python:3.11-slim

# Define variáveis de ambiente para garantir que os logs apareçam no terminal do Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho no container
WORKDIR /app

# Copia o arquivo de dependências e instala os pacotes
# Isso aproveita o cache de camadas do Docker. A instalação só será refeita se o requirements.txt mudar.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o diretório de trabalho
COPY . .

# Expõe a porta que o Gunicorn irá usar
EXPOSE 3000

# Comando para iniciar a aplicação com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "app:app", "--reload"]