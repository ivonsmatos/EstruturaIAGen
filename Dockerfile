# Dockerfile otimizado para containerização do projeto
FROM python:3.10-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Atualizar o comando para iniciar o Flask
CMD ["python", "web_interface/app.py"]