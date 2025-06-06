import discord
from discord.ext import commands, tasks
import requests
import asyncio
from dotenv import load_dotenv
import os
import datetime

# .env dosyasını yükle
load_dotenv()

# API anahtarını .env dosyasından al
API_KEY = os.getenv('CRYPTOCOMPARE_API_KEY')
BASE_URL = "https://min-api.cryptocompare.com/data/price"

# Kanal ID'leri
LOG_CHANNEL_ID = 1339957995542544435  # Keep-alive mesajlarının atılacağı kanal
PRICE_CHANNEL_ID = 1340760164617424938  # BTC fiyatının atılacağı kanal

# En popüler 10 coin
TOP_COINS = ["BTC", "ETH", "SOL","LTC", "RENDER", "ONDO", "FET", "GRT"]

def log_message(message):
    """Log mesajını tarih, saat ile birlikte formatlayarak döndür"""
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)  # Türkiye saati
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] {message}"

async def log_error(bot, message):
    """Log kanalına hata mesajı gönder"""
    formatted_message = log_message(message)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"⚠ **Hata:** {formatted_message}")

def get_crypto_price(coin):
    """API'den tek bir coin'in fiyatını alır"""
    url = f"{BASE_URL}?fsym={coin.upper()}&tsyms=USD,TRY"
    headers = {'Authorization': f'Apikey {API_KEY}'}
    response = requests.get(url, headers=headers)
    data = response.json()

    # Log için API yanıtını döndürelim
    print(f"API Yanıtı ({coin}): {data}")

    if 'USD' in data and 'TRY' in data:
        return data['USD'], data['TRY']
    return None, None

def format_price(price):
    """Sayısal değeri daha okunabilir hale getirir"""
    return "{:,.2f}".format(price).replace(",", ".")

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_daily_price.start()
        self.keep_alive.start()

    def cog_unload(self):
        self.send_daily_price.cancel()
        self.keep_alive.cancel()

    @commands.command()
    async def crypto(self, ctx, coin: str = None):
        """Coin fiyatlarını gösterir. Eğer coin belirtilmezse en popüler 10 coini gösterir."""
        if ctx.channel.id != PRICE_CHANNEL_ID:
            embed = discord.Embed(
                title="Hrrrr!",
                description=f"Lütfen <#{PRICE_CHANNEL_ID}> kanalında buluşalım. Kediler burada mutlu! 😸",
                color=discord.Color.red()
            )
            embed.set_footer(text="Bisonun keyfi 🐾")
            await ctx.send(embed=embed)
            return

        if coin:
            # Kullanıcı belirli bir coin istemiş
            coin = coin.upper()
            price_usd, price_try = get_crypto_price(coin)
            if price_usd and price_try:
                formatted_usd = format_price(price_usd)
                formatted_try = format_price(price_try)
                embed = discord.Embed(
                    title=f"🐾 {coin} Fiyatı 🐱",
                    description=f"**${formatted_usd}** /**₺{formatted_try}**\n\n*Bu fiyatlar patili borsa analizi içermez*",
                    color=discord.Color.yellow()
                )
                embed.set_footer(text="Mır mır! Kriptolar hep değişir, dikkatli ol! (YTD).")
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ **{coin} için fiyat verisi bulunamadı.** Mırmır, tekrar dene!")

        else:
            # Kullanıcı genel coin fiyatlarını istiyor
            embed = discord.Embed(
                title="🐱 Bakalım mama parasını nerden çıkaracağız! 🐾",
                description="Bu fiyatlar patili borsa analizi içermez!",
                color=discord.Color.yellow()
            )
            for coin in TOP_COINS:
                price_usd, price_try = get_crypto_price(coin)
                if price_usd and price_try:
                    formatted_usd = format_price(price_usd)
                    formatted_try = format_price(price_try)
                    embed.add_field(
                        name=f"🐾 {coin}",
                        value=f"**${formatted_usd}**\n**₺{formatted_try}**",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=f"🐾 {coin}",
                        value="❌ **Fiyat alınamadı.**",
                        inline=True
                    )
            embed.set_footer(text="Mır mır! Kriptolar hep değişir, dikkatli ol! (YTD).")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Crypto(bot))
