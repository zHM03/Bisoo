import discord
from discord.ext import commands
import random
import json
import os

KANAL_ID = 1340760164617424938  # Komutun çalışmasını istediğiniz kanalın ID'si

class Joke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_jokes(self):
        """JSON dosyasındaki şakaları yükler"""
        file_path = os.path.join(os.path.dirname(__file__), 'jokes.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @commands.command(name='j')  # Komut adı 'j' olarak belirledik
    async def joke(self, ctx):
        """Rastgele şaka getirir"""

        if ctx.channel.id != KANAL_ID:  # Yanlış kanalda çalıştırılırsa
            kanal = ctx.guild.get_channel(KANAL_ID)
            embed = discord.Embed(
                title="Hrrrr!",
                description=f"Lütfen {kanal.mention}'de buluşalım. Kediler burada mutlu! 😸",
                color=discord.Color.red()
            )
            embed.set_footer(text="Bisonun keyfi 🐾")
            await ctx.send(embed=embed)
            return

        jokes = self.load_jokes()  # Şakaları yükle
        joke = random.choice(jokes)  # Rastgele bir şaka seç
        await ctx.send(joke['joke'])  # Şakayı gönder

async def setup(bot):
    """Botun komutları yüklemesi için setup fonksiyonu"""
    await bot.add_cog(Joke(bot))