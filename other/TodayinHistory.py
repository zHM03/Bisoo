import discord
from discord.ext import commands
import datetime
import requests

class TodayInHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="today")
    async def today_in_history(self, ctx):
        # Bugünün tarihi
        today = datetime.datetime.now().strftime('%m/%d')  # mm/dd formatında
        month, day = today.split('/')

        # API URL'si - Doğru endpoint
        url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/{month}/{day}"

        # API çağrısını yapalım
        response = requests.get(
            url, 
            headers={"User-Agent": "bisooo/1.0 (h2kh03@gmail.com)"}
        )

        # API yanıtını log kanalına yazalım
        log_channel_id = 1339957995542544435  # Hedef kanal ID'si
        log_channel = self.bot.get_channel(log_channel_id)

        # API yanıtını log kanalına yazalım
        if log_channel:
            await log_channel.send(f"API Yanıtı: {response.status_code}")
            await log_channel.send(f"API Yanıtı İçeriği: {response.text}")

        if response.status_code != 200:
            await ctx.send(f"API ile iletişim kurulamıyor. Hata kodu: {response.status_code}")
            return

        # Yanıtı JSON formatında alalım
        try:
            data = response.json()

            # Eğer veri bulunmuşsa
            if 'events' in data and data['events']:
                events = data['events']
                event_titles = [event['text'] for event in events[:5]]  # İlk 5 olayı al

                # Kedi temalı başlıklar ve içeriklerle embed mesajı
                embed = discord.Embed(
                    title="Miyav! Bugün Tarihte Ne Oldu?",
                    description="İşte bugün tarihte gerçekleşen bazı olaylar!",
                    color=discord.Color.purple()
                )

                for i, title in enumerate(event_titles, 1):
                    embed.add_field(name=f'🐾 Olay {i}:', value=title, inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send("Bugün tarihteki olaylar bulunamadı.")
        except Exception as e:
            print(f"Hata: {e}")
            await ctx.send("API yanıtı işlenemedi, lütfen tekrar deneyin.")

async def setup(bot):
    await bot.add_cog(TodayInHistory(bot))