import discord
from discord.ext import commands
import os
import sys
from dotenv import load_dotenv

# Klasörleri içe aktarmak için yolları ekleyelim
directories = ['fun', 'music', 'other', 'utilis', 'discounts']
for directory in directories:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), directory)))

# Modülleri içe aktar
from fun import *
from music import *
from other import *
from utilis import *
from discounts import *

# .env dosyasındaki değişkenleri yükle
load_dotenv()

# Discord botunun yetkilerini belirle
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

# Botu oluştur
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print('Bisooo göreve hazır!')

    extensions = [
        'commands',  # Genel komutlar
        'steamtracker',
        'weather',  # Hava durumu komutu
        'crypto',  # Kripto para bilgisi
        'joke',  # Şaka komutları
        'gif',  # GIF komutları
        'music_player',  # Müzik modülü
        'music_commands',
        'tempsdelete'  # Geçici dosya temizleme
    ]

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ {ext} başarıyla yüklendi!")
        except Exception as e:
            print(f"❌ {ext} yüklenirken hata oluştu: {e}")

# Discord bot tokenini al
TOKEN = os.getenv('DISCORD_TOKEN')

# Botu çalıştır
bot.run(TOKEN)