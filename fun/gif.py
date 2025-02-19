import discord
from discord.ext import commands
import requests
import random
from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

class Giphy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sent_gifs = []  # Gönderilen GIF'lerin ID'lerini saklayacak liste

    def get_random_gif(self, data):
        """Verilen Giphy API verisinden rastgele bir GIF seçer, daha önce gönderilmemişse seçer."""
        available_gifs = [gif for gif in data['data'] if gif['id'] not in self.sent_gifs]
        
        if available_gifs:
            return random.choice(available_gifs)
        else:
            return random.choice(data['data'])  # Eğer tüm GIF'ler gönderildiyse, her şeyi kabul ederiz.

    @commands.command(name='kedy')  # Komut adı 'gif' olarak belirledik
    async def gif(self, ctx):
        """Rastgele kedi GIF'i gönderir"""
        
        GIPHY_API_KEY = os.getenv('GIPHY_API_KEY')  # .env dosyasından API anahtarını al
        GIPHY_API_URL = 'https://api.giphy.com/v1/gifs/search'
        
        query = 'cat'  # Kedi GIF'leri arıyoruz
        params = {
            'api_key': GIPHY_API_KEY,
            'q': query,
            'limit': 2000  # Birden fazla sonuç alıyoruz, örneğin 10 sonuç
        }
        
        # Giphy API'den gelen veriyi çekiyoruz
        response = requests.get(GIPHY_API_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['data']:  # Eğer sonuç varsa
                random_gif = self.get_random_gif(data)  # Yeni bir GIF seç
                gif_url = random_gif['url']
                
                # Seçilen GIF'in ID'sini kaydediyoruz
                self.sent_gifs.append(random_gif['id'])
                
                await ctx.send(gif_url)  # GIF URL'sini gönder
            else:
                await ctx.send("Üzgünüm, kedi GIF'i bulunamadı.")
        else:
            await ctx.send("GIF alınamadı, bir hata oluştu.")

# Cog'u yükleme
async def setup(bot):
    await bot.add_cog(Giphy(bot))
