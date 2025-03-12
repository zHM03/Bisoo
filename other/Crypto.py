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

async def get_log_channel(guild):
    """Log kanalını döndüren fonksiyon"""
    return discord.utils.get(guild.text_channels, name="biso-log")

def get_crypto_price(coin_symbol):
    """API'den kripto para fiyatlarını alır"""
    url = f"{BASE_URL}?fsym={coin_symbol.upper()}&tsyms=USD,TRY"
    headers = {'Authorization': f'Apikey {API_KEY}'}
    response = requests.get(url, headers=headers)
    data = response.json()

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

    @tasks.loop(minutes=1)
    async def send_daily_price(self):
        """Her gün 00:00'da BTC fiyatını gönderir"""
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)  # Türkiye saati
        if now.hour == 0 and now.minute == 0:
            channel = self.bot.get_channel(PRICE_CHANNEL_ID)
            if channel:
                price_usd, price_try = get_crypto_price("BTC")
                if price_usd and price_try:
                    formatted_usd = format_price(price_usd)
                    formatted_try = format_price(price_try)
                    await channel.send(f"📢 **24 Saatlik BTC Fiyatı:**\n💲 ${formatted_usd} / ₺{formatted_try} (YTD)")
                else:
                    await log_error(self.bot, "BTC fiyatı alınamadı.")

    @tasks.loop(minutes=10)
    async def keep_alive(self):
        """Bot'un Railway tarafından kapatılmasını önler"""
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send("✅ **Bot hala çalışıyor...**")

    @commands.command()
    async def crypto(self, ctx, coin: str):
        """Belirtilen coin'in anlık fiyatını getirir"""
        coin_symbol = coin.lower()
        price_usd, price_try = get_crypto_price(coin_symbol)
        if price_usd and price_try:
            formatted_usd = format_price(price_usd)
            formatted_try = format_price(price_try)
            await ctx.send(f"📊 **{coin.upper()} Fiyatı:**\n💲 ${formatted_usd} / ₺{formatted_try} (YTD)")
        else:
            await ctx.send(f"❌ **{coin.upper()} için fiyat verisi bulunamadı.**")

async def setup(bot):
    await bot.add_cog(Crypto(bot))