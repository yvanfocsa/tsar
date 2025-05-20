# 1) Base Python
FROM python:3.11-slim

# 2) Installer Nmap et ses dépendances système
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      nmap \
      nikto \
 && rm -rf /var/lib/apt/lists/*

# 3) Créer le répertoire de travail
WORKDIR /app

# 4) Copier les fichiers Python + requirements
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt

COPY . .

# 5) Exposer le port Streamlit
EXPOSE 8501

# 6) Lancer Streamlit
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
