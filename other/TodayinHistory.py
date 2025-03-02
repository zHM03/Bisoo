import discord
from discord.ext import commands
import requests
import datetime
from googletrans import Translator

class TodayHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()  # Çevirici nesnesi

    @commands.command(name="today")
    async def today_in_history(self, ctx):
        try:
            # Bugünün tarihi (ay/gün formatında)
            today = datetime.datetime.now().strftime('%m/%d')
            month, day = today.split('/')

            # API'ye istek gönder
            url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/{month}/{day}"
            response = requests.get(url, headers={"User-Agent": "bisooo/1.0 (h2kh03@gmail.com)"})
            
            if response.status_code == 200:
                data = response.json()

                # Olayları kontrol et ve gönder
                if 'events' in data and data['events']:
                    events = data['events']
                    event_titles = [event['text'] for event in events[:5]]  # İlk 5 olay
                    
                    # Verileri Türkçe'ye çevir
                    event_titles_translated = [self.translator.translate(title, src='en', dest='tr').text for title in event_titles]

                    embed = discord.Embed(
                        title="Miyav! Bugün Tarihte Ne Oldu?",
                        description="İşte bugün tarihte gerçekleşen bazı olaylar!",
                        color=discord.Color.purple()
                    )
                    for i, title in enumerate(event_titles_translated, 1):
                        embed.add_field(name=f'🐾 Olay {i}:', value=title, inline=False)

                    await ctx.send(embed=embed)  # Embed ile mesajı gönder
                else:
                    await ctx.send("Bugün tarihteki olaylar bulunamadı.")
            else:
                await ctx.send(f"API ile iletişim kurulamıyor. Hata kodu: {response.status_code}")
        
        except Exception as e:
            print(f"Hata: {e}")
            await ctx.send("Bir hata oluştu, lütfen tekrar deneyin.")

# Cog'u bot'a eklemek için gerekli fonksiyon
async def setup(bot):
    await bot.add_cog(TodayHistory(bot))