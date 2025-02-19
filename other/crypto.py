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
API_KEY = os.getenv('CRYPTOCOMPARE_API_KEY')  # .env dosyasındaki anahtarı burada kullanıyoruz
BASE_URL = "https://min-api.cryptocompare.com/data/price"

def log_message(self, message):
    """Log mesajını tarih, saat ile birlikte formatlayarak döndür"""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] {message}"

async def log_error(self, message):
    """Log kanalına hata mesajı gönder"""
    formatted_message = self.log_message(message)
    for guild in self.bot.guilds:
        log_channel = await self.get_log_channel(guild)
        if log_channel:
            await log_channel.send(f"**Log:** {formatted_message}")

async def get_log_channel(self, guild):
    """Log kanalını döndüren fonksiyon"""
    log_channel = discord.utils.get(guild.text_channels, name="biso-log")
    return log_channel

def get_crypto_price(coin_symbol):
    url = f"{BASE_URL}?fsym={coin_symbol.upper()}&tsyms=USD,TRY"  # Hem USD hem de TRY fiyatını alıyoruz
    headers = {
        'Authorization': f'Apikey {API_KEY}'
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    # API'den gelen yanıtın doğruluğunu kontrol et
    print(f"API Yanıtı: {data}")

    if 'USD' in data and 'TRY' in data:
        return data['USD'], data['TRY']
    return None, None

def format_price(price):
    """Sayısal değeri daha okunabilir hale getiren format fonksiyonu"""
    return "{:,.2f}".format(price).replace(",", ".")

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_daily_price.start()  # Her gün saat 00:00'da mesaj gönderecek

    def cog_unload(self):
        self.send_daily_price.cancel()

    @tasks.loop(hours=24, reconnect=True)  # Saatlik olarak yeniden başlatmaya gerek yok, 24 saatlik loop ile 00:00'da çalışacak
    async def send_daily_price(self):
        now = datetime.datetime.now()
        # Eğer saat 00:00 ise, fiyatı gönder
        if now.hour == 0 and now.minute == 0:
            channel = self.bot.get_channel(1340760164617424938)  # Burada CHANNEL_ID ile kanal ID'sini yazmalısın
            price_usd, price_try = get_crypto_price("BTC")
            if price_usd and price_try:
                # Sayıları formatlayarak göndereceğiz
                formatted_usd = format_price(price_usd)
                formatted_try = format_price(price_try)
                await channel.send(f"24 saatlik BTC fiyatı: ${formatted_usd} / ₺{formatted_try}... (YTD)")
            else:
                await self.bot.music.log_error("BTC fiyatı alınamadı.")
        await asyncio.sleep(60)  # Her dakika kontrol edip 00:00'ı bekler

    @commands.command()
    async def crypto(self, ctx, coin: str):
        """Belirli bir coin'in fiyatını yazacak komut"""
        # Coin sembolünü küçük harfe çeviriyoruz
        coin_symbol = coin.lower()
        price_usd, price_try = get_crypto_price(coin_symbol)
        if price_usd and price_try:
            # Sayıları formatlayarak göndereceğiz
            formatted_usd = format_price(price_usd)
            formatted_try = format_price(price_try)
            await ctx.send(f"{coin.upper()} fiyatı: ${formatted_usd} / ₺{formatted_try}... (YTD)")
        else:
            await ctx.send(f"{coin.upper()} için fiyat verisi bulunamadı.")

async def setup(bot):
    await bot.add_cog(Crypto(bot))
