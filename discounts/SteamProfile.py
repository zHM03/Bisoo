import discord
from discord.ext import commands
import requests
import json

class PriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="price")
    async def get_game_price(self, ctx, *, game_name: str):
        # Steam API URL'si
        steam_api_url = f"https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        
        # Steam'de oyun adı ile ilgili bilgiyi al
        response = requests.get(steam_api_url)
        data = response.json()

        # Oyunun App ID'sini bul
        game_app_id = None
        for game in data['applist']['apps']:
            if game_name.lower() in game['name'].lower():
                game_app_id = game['appid']
                break

        if not game_app_id:
            await ctx.send(f"{game_name} adlı oyun bulunamadı!")
            return

        # Oyunun fiyat bilgilerini al
        price_url = f"https://api.steampowered.com/ISteamEconomy/GetAssetPrices/v1?appid={game_app_id}"
        price_response = requests.get(price_url)
        price_data = price_response.json()

        if "price" not in price_data or "discount" not in price_data:
            await ctx.send(f"{game_name} için fiyat bilgisi alınamadı.")
            return
        
        # En son indirim ve fiyat bilgilerini al
        discount_price = price_data['discount']['final_price']
        original_price = price_data['price']['original_price']
        discount_start_time = price_data['discount']['start_time']
        discount_end_time = price_data['discount']['end_time']

        # Embed mesajı oluştur
        embed = discord.Embed(title=f"{game_name} Fiyat Bilgisi", color=discord.Color.green())
        embed.add_field(name="İndirim Fiyatı", value=f"${discount_price / 100:.2f}", inline=False)
        embed.add_field(name="Orijinal Fiyat", value=f"${original_price / 100:.2f}", inline=False)
        embed.add_field(name="İndirim Başlangıcı", value=f"<t:{discount_start_time}:F>", inline=False)
        embed.add_field(name="İndirim Bitişi", value=f"<t:{discount_end_time}:F>", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PriceCog(bot))