FROM python:3.9-slim

# Sistem bağımlılıklarını yükleyelim
RUN apt-get update && apt-get install -y ffmpeg

# Çalışma dizini oluştur
WORKDIR /app

# Gereksinimleri yükle
COPY requirements.txt .
RUN pip install -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

CMD ["python", "main.py"]
