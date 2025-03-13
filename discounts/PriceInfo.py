import discord
from discord.ext import commands
import requests

class ITADCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='deals')
    async def get_deals(self, ctx):
        """ITAD API'sinden en iyi teklifleri getirir."""
        api_key = "37d8ca093b6022f360d8e48ce69932797bc3c4e2"
        url = "https://api.isthereanydeal.com/v01/deals/list/"
        params = {
            "key": api_key,
            "sort": "price",  # Fiyat sıralaması
            "limit": 5        # İlk 5 teklif
        }

        # API isteği gönder
        response = requests.get(url, params=params)

        # Log kanal ID'si
        log_channel_id = 1273378150901874718
        log_channel = self.bot.get_channel(log_channel_id)

        # Kanal var mı kontrol et
        if log_channel is None:
            print("Log kanalı bulunamadı!")
            await ctx.send("Log kanalı bulunamadı.")
            return

        # Yanıt kontrolü
        if response.status_code == 200:
            data = response.json()
            deals = data.get('data', {}).get('list', [])
            if deals:
                message = "İşte en iyi 5 teklif:\n"
                for deal in deals:
                    name = deal.get('title', 'Bilinmiyor')
                    price = deal.get('price', 'Bilinmiyor')
                    message += f"{name}: {price}\n"
                await ctx.send(message)
                # Loglara yazma
                await log_channel.send(f"API başarıyla çalıştı ve teklifler alındı:\n{message}")
            else:
                await ctx.send("Teklif bulunamadı.")
                # Loglara yazma
                await log_channel.send("Teklif bulunamadı.")
        else:
            await ctx.send(f"API isteği başarısız. Durum kodu: {response.status_code}")
            # Loglara yazma
            await log_channel.send(f"API isteği başarısız. Durum kodu: {response.status_code}")

async def setup(bot):
    await bot.add_cog(ITADCog(bot))