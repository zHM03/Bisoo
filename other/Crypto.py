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
TOP_COINS = ["BTC", "ETH", "BNB", "XRP", "DOGE", "ADA", "SOL", "MATIC", "DOT", "LTC"]

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

def get_crypto_price(coins):
    """API'den kripto para fiyatlarını alır"""
    coin_symbols = ",".join(coins)
    url = f"{BASE_URL}/multi?fsyms={coin_symbols}&tsyms=USD,TRY"
    headers = {'Authorization': f'Apikey {API_KEY}'}
    response = requests.get(url, headers=headers)
    data = response.json()

    prices = {}
    for coin in coins:
        if coin in data and 'USD' in data[coin] and 'TRY' in data[coin]:
            prices[coin] = (data[coin]['USD'], data[coin]['TRY'])
    return prices

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

    @tasks.loop(minutes=1)
    async def send_daily_price(self):
        """Her gün 00:00'da BTC fiyatını gönderir"""
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)  # Türkiye saati
        if now.hour == 0 and now.minute == 0:
            channel = self.bot.get_channel(PRICE_CHANNEL_ID)
            if channel:
                prices = get_crypto_price(["BTC"])
                if "BTC" in prices:
                    price_usd, price_try = prices["BTC"]
                    formatted_usd = format_price(price_usd)
                    formatted_try = format_price(price_try)
                    embed = discord.Embed(
                        title="🐱 24 Saatlik BTC Fiyatı 🐾",
                        description=f"💲 **${formatted_usd}** / 🐟 **₺{formatted_try}**\n\n*Bu fiyatlar sadece bilgi amaçlıdır. YTD!*",
                        color=discord.Color.gold()
                    )
                    embed.set_footer(text="Meow meow, kripto dünyası seni bekliyor!")
                    await channel.send(embed=embed)
                else:
                    await log_error(self.bot, "BTC fiyatı alınamadı.")

    @tasks.loop(minutes=10)
    async def keep_alive(self):
        """Bot'un Railway tarafından kapatılmasını önler"""
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send("✅ **Bot hala çalışıyor...**")

    @commands.command()
    async def crypto(self, ctx, coin: str = None):
        """Coin fiyatlarını gösterir. Eğer coin belirtilmezse en popüler 10 coini gösterir."""
        if coin:
            # Kullanıcı belirli bir coin istemiş
            coin = coin.upper()
            prices = get_crypto_price([coin])
            if coin in prices:
                price_usd, price_try = prices[coin]
                formatted_usd = format_price(price_usd)
                formatted_try = format_price(price_try)
                embed = discord.Embed(
                    title=f"🐾 {coin} Fiyatı Meow! 🐱",
                    description=f"💲 **${formatted_usd}** / 🐟 **₺{formatted_try}**\n\n*Mır mır! Kriptolar hep değişir, dikkatli ol!*",
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Bu fiyatlar patili borsa analizi içermez.")
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ **{coin} için fiyat verisi bulunamadı.** Mırmır, tekrar dene!")

        else:
            # Kullanıcı genel coin fiyatlarını istiyor
            prices = get_crypto_price(TOP_COINS)
            embed = discord.Embed(
                title="🐱 En Popüler 10 Coin Meow! 🐾",
                description="İşte en ünlü 10 kripto paranın fiyatları!",
                color=discord.Color.purple()
            )
            for coin, (price_usd, price_try) in prices.items():
                formatted_usd = format_price(price_usd)
                formatted_try = format_price(price_try)
                embed.add_field(
                    name=f"🐾 {coin}",
                    value=f"💲 **${formatted_usd}**\n🐟 **₺{formatted_try}**",
                    inline=True
                )
            embed.set_footer(text="Meow meow! Kripto dünyasında dikkatli ol!")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Crypto(bot))