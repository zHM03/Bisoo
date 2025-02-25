# Hafif bir Python 3.9 tabanlı imaj kullan
FROM python:3.9-slim

# Çalışma dizinini ayarla
WORKDIR /app

# FFmpeg'i yükle
RUN apt update && apt install -y ffmpeg

# En güncel yt-dlp sürümünü yükle
RUN pip install --no-cache-dir --upgrade yt-dlp

# Gereksinimleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Botu başlat
CMD ["python", "main.py"]