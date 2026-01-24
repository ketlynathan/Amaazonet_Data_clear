FROM python:3.12.8-slim

# Diretório de trabalho
WORKDIR /app

# Variáveis de ambiente Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Dependências do sistema
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas requirements para cache
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copiar todo o código
COPY . .

# Criar usuário não-root
RUN useradd -m appuser
USER appuser

# Expor porta Streamlit
EXPOSE 8501

# Healthcheck do container
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando de entrada (igual ao que você roda localmente)
ENTRYPOINT ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
