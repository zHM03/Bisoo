import discord
from discord.ext import commands

class ChannelControl(commands.Cog):
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


async def setup(bot):
    await bot.add_cog(ChannelControl(bot))
