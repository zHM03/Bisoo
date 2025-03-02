import discord
from discord.ext import commands
import requests
from googletrans import Translator

# Şiirleri almak için PoetryDB API'sini kullanıyoruz
def get_random_poem():
    url = "https://poetrydb.org/random"  # PoetryDB API rastgele şiir endpoint
    response = requests.get(url)
    poem_data = response.json()  # JSON formatında şiir verisini alıyoruz

    # Şiir başlığını ve satırlarını almak
    lines = poem_data[0]['lines']
    poem_text = "\n".join(lines)  # Şiir satırlarını birleştiriyoruz
    return poem_text

# Şiiri Türkçeye çevirmek için Google Translate kullanıyoruz
def translate_poem(poem_text):
    translator = Translator()
    translated = translator.translate(poem_text, src='en', dest='tr')
    return translated.text

# Discord bot sınıfı
class PoemBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def siir(self, ctx):
        # PoetryDB API'den rastgele şiir alıyoruz
        poem = get_random_poem()

        # Şiiri Google Translate ile Türkçeye çeviriyoruz
        translated_poem = translate_poem(poem)

        # Embed mesajı oluşturuyoruz
        embed = discord.Embed(title="Türkçe Şiir", description="İngilizce şiirin Türkçe çevirisi", color=discord.Color.blue())
        embed.add_field(name="Türkçe Şiir", value=translated_poem, inline=False)

        # Embed mesajını gönderiyoruz
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PoemBot(bot))