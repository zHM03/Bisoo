FROM python:3.9-slim

# Gerekli sistem bağımlılıklarını yükleyelim
RUN apt-get update && apt-get install -y ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*  # Gereksiz dosyaları temizle

# Çalışma dizini oluştur
WORKDIR /app

# En güncel yt-dlp sürümünü yükle
RUN pip install --no-cache-dir --upgrade yt-dlp

# Gereksinimleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

CMD ["python", "main.py"]
