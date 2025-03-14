import discord
from discord.ext import commands
import requests
import urllib.parse

class GamePriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gameprice")
    async def get_game_price(self, ctx, *, game_title: str):
        """Belirtilen oyun için en iyi fiyatı gösterir"""
        
        # API anahtarınızı buraya ekleyin
        api_key = "37d8ca093b6022f360d8e48ce69932797bc3c4e2"
        # Oyun başlığını URL'ye düzgün şekilde entegre et
        game_title_encoded = urllib.parse.quote(game_title)  # Başlıkta boşlukları ve özel karakterleri encode et
        url = f"https://api.isthereanydeal.com/lookup/game/title/{game_title_encoded}/?key={api_key}"

        # API isteği gönderme
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            prices = data.get('data', {}).get('prices', [])
            
            if prices:
                # En düşük fiyatı bul
                best_price = min(prices, key=lambda x: x['price'])
                best_store = best_price.get('shop', 'Bilinmiyor')
                best_price_value = best_price.get('price', 'Bilinmiyor')
                best_link = best_price.get('link', 'Bilinmiyor')
                
                # En iyi fiyatı Discord kanalında göster
                await ctx.send(f"**{game_title}** için en iyi fiyat: {best_price_value} - {best_store}\nLink: {best_link}")
            else:
                await ctx.send("Fiyat bilgisi bulunamadı.")
        else:
            await ctx.send(f"Hata: {response.status_code}, API'ye bağlanılamadı.")

# Botu başlatma
async def setup(bot):
    await bot.add_cog(GamePriceCog(bot))
