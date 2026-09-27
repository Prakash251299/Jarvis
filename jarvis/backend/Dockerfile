FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Piper TTS
RUN wget -q https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz \
    -O /tmp/piper.tar.gz && \
    tar -xzf /tmp/piper.tar.gz -C /usr/local/bin --strip-components=1 && \
    rm /tmp/piper.tar.gz || true

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
