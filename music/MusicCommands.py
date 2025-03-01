import discord
from discord.ext import commands

class VoiceControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channel_id = 1276852302388400200  # Buraya sadece izin verilen kanalın ID'sini yazın

    async def check_channel(self, ctx):
        """Komutların sadece belirli bir kanalda çalışmasını sağlar"""
        allowed_channel = self.bot.get_channel(self.allowed_channel_id)
        if ctx.channel.id != self.allowed_channel_id:
            allowed_channel_mention = allowed_channel.mention  # Kanal etiketini al
            embed = discord.Embed(
                title="😾 Hrrrr 😾",
                description=f"Sinirlendirmeyin beni buraya gelin lütfen! {allowed_channel_mention}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return False
        return True

    @commands.command()
    async def s(self, ctx):
        """Müzik duraklatma komutu"""
        if not await self.check_channel(ctx):
            return  # Eğer komut geçerli bir kanalda değilse, işlem yapılmaz

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
        """Sıradaki şarkıya geç komutu"""
        if not await self.check_channel(ctx):
            return  # Eğer komut geçerli bir kanalda değilse, işlem yapılmaz

        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice_client or not voice_client.is_playing():
            await ctx.message.add_reaction("❌")  # Şu an çalan müzik yoksa
            return

        voice_client.stop()  # Mevcut şarkıyı durdur
        await ctx.message.add_reaction("⏭️")  # İleri sarma emojisi

    @commands.command()
    async def r(self, ctx):
        """Müziği devam ettir komutu"""
        if not await self.check_channel(ctx):
            return  # Eğer komut geçerli bir kanalda değilse, işlem yapılmaz

        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.message.add_reaction("▶️")  # Devam ettirme emojisi


async def setup(bot):
    await bot.add_cog(VoiceControl(bot))
