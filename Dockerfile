# Python 3.9 tabanlı bir imaj kullanıyoruz
FROM python:3.9

# Sistemde gerekli bağımlılıkları kuruyoruz
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6

# Çalışma dizinini belirliyoruz
WORKDIR /app

# requirements.txt dosyasını kopyalıyoruz
COPY requirements.txt .

# Bağımlılıkları kuruyoruz
RUN pip install -r requirements.txt

# Proje dosyalarını kopyalıyoruz
COPY . .

# Uygulama başlatma komutu
CMD ["python", "app.py"]
