import discord
from discord.ext import commands

class VoiceControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def s(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client:
            if voice_client.is_playing():
                voice_client.pause()
                await ctx.message.add_reaction("⏸️")  # Duraklatma tepki emojisi
            else:
                await ctx.message.add_reaction("❌")  # Şu an çalan müzik yoksa
        else:
            await ctx.message.add_reaction("❌")  # Bot ses kanalında değilse

    @commands.command(name="n")
    async def next(self, ctx):
        """Sıradaki şarkıya geç"""
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice_client or not voice_client.is_playing():
            await ctx.message.add_reaction("❌")  # Şu an çalan müzik yoksa
            return

        voice_client.stop()  # Mevcut şarkıyı durdur
        await ctx.message.add_reaction("⏭️")  # İleri sarma emojisi

    @commands.command()
    async def r(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.message.add_reaction("▶️")  # Devam ettirme emojisi

async def setup(bot):
    await bot.add_cog(VoiceControl(bot))
