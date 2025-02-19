import discord
from discord.ext import commands
import random
import json
import os

class Joke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_jokes(self):
        """JSON dosyasındaki şakaları yükle"""
        file_path = os.path.join(os.path.dirname(__file__), 'jokes.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @commands.command(name='j')  # Komut adı 'j' olarak belirledik
    async def joke(self, ctx):
        """Rastgele şaka getirir"""
        jokes = self.load_jokes()  # Şakaları yükle
        joke = random.choice(jokes)  # Rastgele bir şaka seç
        await ctx.send(joke['joke'])  # Şakayı gönder

async def setup(bot):
    """Botun komutları yüklemesi için setup fonksiyonu"""
    await bot.add_cog(Joke(bot))
