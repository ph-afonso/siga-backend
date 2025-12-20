# Usa uma imagem oficial leve do Python
FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Garante que os logs sejam exibidos imediatamente no terminal
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para compilar pacotes Python (ex: psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements e instala as dependências do Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia o restante do projeto
COPY . .

# Comando padrão para rodar o servidor de desenvolvimento
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]