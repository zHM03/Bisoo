import discord
from discord.ext import commands

class VoiceControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []

    @commands.command()
    async def q(self, ctx):
        """Mevcut şarkı kuyruğunu gösterir."""
        await self.send_queue_embed(ctx)

    async def send_queue_embed(self, ctx):
        """Mevcut sırayı embed olarak gösterir."""
        if not self.song_queue:
            await ctx.send("🎵 Şu an çalma listesinde şarkı yok.")
            return

        embed = discord.Embed(title="🎶 Miyaaaav 🎶", color=discord.Color.orange())
        for i, (url, title) in enumerate(self.song_queue, 1):
            embed.add_field(name=f"{i}. {title}", value=url, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def s(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client:  
            if voice_client.is_playing():
                voice_client.pause()
                await ctx.send("⏸️ Şarkı duraklatıldı.")
            else:
                await ctx.send("❌ Şu anda çalan bir müzik yok.")
        else:
            await ctx.send("❌ Bot şu anda bir ses kanalında değil.")

    @commands.command()
    async def n(self, ctx):
        """Sonraki şarkıya geçer."""
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if voice_client and voice_client.is_playing():
            voice_client.stop()  # Mevcut şarkıyı durdur
            await self.after_play(ctx)  # Sonraki şarkıyı çalmaya başla
        else:
            await ctx.send("🎶 Şu an hiçbir şarkı çalmıyor.")


    @commands.command()
    async def r(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()

    @commands.command()
    async def l(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client:
            await voice_client.disconnect()

async def setup(bot):
    await bot.add_cog(VoiceControl(bot))
