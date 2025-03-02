import discord
from discord.ext import commands
import requests

class GameInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gameinfo(self, ctx, *, game_name: str):
        # CheapShark API üzerinden oyun araması
        CHEAPSHARK_API_URL = 'https://www.cheapshark.com/api/1.0'
        search_url = f"{CHEAPSHARK_API_URL}/search?title={game_name}&limit=5"
        search_response = requests.get(search_url)
        search_data = search_response.json()

        if not search_data:
            await ctx.send("Oyun bulunamadı.")
            return

        # Oyun bilgilerini ve fiyatları almak
        game_info = search_data[0]
        game_title = game_info['title']
        steam_id = game_info['steamAppID']
        price = float(game_info['price'])

        # Steam fiyatlarını almak
        steam_url = f"{CHEAPSHARK_API_URL}/discounts?steamAppID={steam_id}"
        steam_response = requests.get(steam_url)
        steam_data = steam_response.json()

        if not steam_data:
            await ctx.send("Fiyat bilgisi alınamadı.")
            return

        # TL fiyatı için döviz kuru API kullanabiliriz (ExchangeRate-API)
        exchange_response = requests.get('https://v6.exchangerate-api.com/v6/6db4ab17f8e14befe2a62b94/latest/USD')
        exchange_data = exchange_response.json()
        usd_to_try = exchange_data['conversion_rates']['TRY']
        price_try = price * usd_to_try

        # Embed mesajı oluşturma
        embed = discord.Embed(
            title=f"**{game_title}** Oyun Fiyat Bilgileri",
            description="Fiyatlar ve platformlar:",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url="https://example.com/cat_image.png")  # Kedi temalı görsel
        embed.set_footer(text="Bilgiler CheapShark API kullanılarak sağlanmıştır.")

        # Fiyat bilgilerini embed'e ekle
        embed.add_field(name="Steam Fiyatı", value=f"${price:.2f} / ₺{price_try:.2f}", inline=False)

        # En ucuz platformu ekleyin
        cheapest_platform = steam_data[0]['storeID']
        embed.add_field(name="En Ucuz Platform", value=cheapest_platform, inline=False)

        # Embed mesajını gönder
        await ctx.send(embed=embed)

# Cog'u bot'a ekleme
async def setup(bot):
    await bot.add_cog(GameInfo(bot))