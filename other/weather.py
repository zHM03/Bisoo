import discord
import requests
import os
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # API anahtarını .env'den al
BASE_URL = "http://api.weatherapi.com/v1/current.json"  # Yeni API URL'si

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name="h")
    async def get_weather(self, ctx, *, city: str):
        """Belirtilen şehir için hava durumu bilgisini getirir."""
        try:
            params = {
                "key": WEATHER_API_KEY,  # API Anahtarı
                "q": city,  # Şehir adı
                "lang": "tr"  # Türkçe açıklamalar için
            }
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            print("API Yanıtı:", data)  # Terminalde API yanıtını kontrol et

            if "error" in data:
                hata_mesajı = data["error"]["message"]
                await ctx.send(f"❌ Şehir bulunamadı! Hata: {hata_mesajı}")
                return

            şehir = data["location"]["name"]
            ülke = data["location"]["country"]
            sıcaklık = data["current"]["temp_c"]
            açıklama = data["current"]["condition"]["text"]
            nem = data["current"]["humidity"]
            rüzgar = data["current"]["wind_kph"]

            embed = discord.Embed(
                title=f"🌍 {şehir}, {ülke} için hava durumu",
                color=discord.Color.blue()
            )
            embed.add_field(name="🌡️ Sıcaklık", value=f"{sıcaklık}°C", inline=True)
            embed.add_field(name="💧 Nem", value=f"%{nem}", inline=True)
            embed.add_field(name="💨 Rüzgar Hızı", value=f"{rüzgar} km/h", inline=True)
            embed.add_field(name="🌫️ Durum", value=açıklama.capitalize(), inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            await self.bot.music.log_error(f"⚠️ Weather extensionda bir hata oluştu: {e}")

async def setup(bot):
    await bot.add_cog(Weather(bot))
