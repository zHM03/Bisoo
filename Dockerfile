FROM python:3.9-slim

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
