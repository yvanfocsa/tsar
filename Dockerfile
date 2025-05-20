# 1. Base Python
FROM python:3.11-slim

# 2. Dépendances système (nmap, etc.)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      nmap \
      nikto \
      git \
      curl \
 && rm -rf /var/lib/apt/lists/*

# 3. Copie de tout le projet
WORKDIR /app
COPY . .

# 4. Dépendances Python
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt

# 5. Exposition du port et lancement
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "streamlit_app.py",
            "--server.port=8501", "--server.address=0.0.0.0"]
