import discord
from discord.ext import commands
import requests

class PriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="price")
    async def get_game_price(self, ctx, *, game_name: str):
        # CheapShark API URL'si
        url = f"https://api.cheapshark.com/api/1.0/games?title={game_name}"
        
        # API'ye istek gönder
        response = requests.get(url)
        if response.status_code != 200:
            await ctx.send(f"CheapShark API'den veri alınırken bir hata oluştu: {response.status_code}")
            return
        
        data = response.json()
        
        if not data:
            await ctx.send(f"{game_name} adlı oyun bulunamadı!")
            return
        
        # Fiyat bilgilerini al
        game_info = data[0]  # İlk sonuç
        deal = game_info['deal']
        price = float(deal['price'])
        savings = float(deal['savings'])
        retail_price = float(deal['retailPrice'])
        
        # Embed mesajı oluştur
        embed = discord.Embed(title=f"{game_name} Fiyat Bilgisi", color=discord.Color.green())
        embed.add_field(name="İndirimli Fiyat", value=f"${price}", inline=False)
        embed.add_field(name="Orijinal Fiyat", value=f"${retail_price}", inline=False)
        embed.add_field(name="İndirim Oranı", value=f"{savings}%", inline=False)
        
        # Embed mesajı gönder
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PriceCog(bot))