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
        await bot.load_extension('commands') # Diğer komutlar
        await bot.load_extension('steamtracker')
        await bot.load_extension('weather')  # Hava durumu komutu
        await bot.load_extension('crypto') # Crypto bilgisi
        await bot.load_extension('joke')  # Şakacı 
        await bot.load_extension('gif') 
        try:
        await bot.load_extension('music_player')    # Müzik modülü
        except exception as e:
            print(f"music player yüklerken hata oluştu {e}")
        await bot.load_extension('music_commands')
        await bot.load_extension('tempsdelete')
        print("Tüm extensionlar başarıyla yüklendi!")
    except Exception as e:
        print(f"Extension yüklenirken hata oluştu: {e}")

TOKEN = os.getenv('DISCORD_TOKEN')

bot.run(TOKEN)
