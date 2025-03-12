import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import os
import sys

directories = ['fun', 'music', 'other', 'utilis', 'discounts']
for directory in directories:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), directory)))
from fun import *
from music import *
from other import *
from utilis import *
from discounts import *

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print('Bisooo göreve hazır')
    try:
        #discounts
        await bot.load_extension('EpicGames') #epicgamesten bedava oyun alma
        await bot.load_extension('EmbedCheck')#discount kanalındaki tekrarlanan mesajları siler
        await bot.load_extension('PriceInfo')
        await bot.load_extension('SteamProfile')
        #fun
        await bot.load_extension('Joke')#json dosyasından şaka alır
        await bot.load_extension('GIF') #apiden kedi gif atıyor
        await bot.load_extension('Wallpaper')
        await bot.load_extension('Cark')
        #music
        await bot.load_extension('MusicPlayer')    # Müzik modülü
        await bot.load_extension('MusicCommands')   #p,l komutları hariç diğer komutlar
        await bot.load_extension('MusicUtils')      #kanaldaki mesajları siler
        await bot.load_extension('TempsDelete')     #bot kanalda olmayınca eski şarkıları siler
        #other
        await bot.load_extension('Weather')  # Hava  durumu komutu
        await bot.load_extension('TodayinHistory')
        await bot.load_extension('Crypto') # Crypto bilgisi
        await bot.load_extension('Poem')
        #utilis
        await bot.load_extension('commands') # yanlış komut kullanılınca ve help komutu

        print("Tüm extensionlar başarıyla yüklendi!")
    except Exception as e:
        print(f"Extension yüklenirken hata oluştu: {e}")

TOKEN = os.getenv('DISCORD_TOKEN')

bot.run(TOKEN)
