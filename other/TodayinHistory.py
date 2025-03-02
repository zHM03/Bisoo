import discord
from discord.ext import commands
import datetime
import requests

class TodayInHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="today")  # Komut ismini daha kısa yaptık
    async def today_in_history(self, ctx):
        # Bugünün tarihi
        today = datetime.datetime.now().strftime('%m-%d')

        # Tarihteki olayları çekmek için API kullanabiliriz (örneğin: Wikipedia API)
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{today}"
        response = requests.get(url)
        data = response.json()

        # Eğer veri bulunmuşsa
        if 'events' in data:
            events = data['events']
            if events:
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
        else:
            await ctx.send("Veri çekilemedi, lütfen tekrar deneyin.")

async def setup(bot):
    await bot.add_cog(TodayInHistory(bot))  # async setup kullanıldı