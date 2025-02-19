import discord
from discord.ext import commands    

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Hrr böyle komut yok, '!help' yazabilirsiniz!")

    @commands.command()
    async def help(self, ctx):
        """Yardım komutunu sağlar"""
        embed = discord.Embed(
            title="Biso'nun yetenekleri", 
            description="Biso ile neler yapabilirsiniz:", 
            color=discord.Color.orange()  # Embed için mavi renk
        )

        help_message = (
            "**!p:** *<Şarkı ismi, YouTube veya Spotify linki> şarkınızı çalarım*\n"
            "**!s:** *Şarkınızı durdururum*\n"
            "**!r:** *Şarkınızı devam ettiririm*\n"
            "**!l:** *Yanınızdan ayrılırım :(*\n"
            "----------------------------------------------------\n"
            "**Oyun Takip Etme Komutları:**\n"
            "**!addgame:** *<Oyun adı veya steam linki> listeye eklerim ve indirime girdğinde size miyavlarım*\n"
            "**!listgames:** *Takip listesindeki oyunları gösteririm*\n"
            "**!removegame:** *<Oyun adı>Listeden kaldırırım\n"
            "----------------------------------------------------\n"
            "**Diğer Komutlar:**\n"
            "**!h:** *<Şehir> Merak ettiğiniz şehrin hava durumunu söylerim*\n"
            "**!j:** *Komik şakalar yaparım*\n"
            "**!kedy:** *Arkadaşlarımı ifşalarım*\n"
            "**!crypto:** *<coin> coin'in fiyatını gösterebilirim*\n"
            "----------------------------------------------------\n"
            "***Şimdilik bu kadarrr***"
        )
        
        # Yardım mesajını embed'in içerisine ekliyoruz
        embed.add_field(name="Müzik Komutları:", value=help_message, inline=False)
        
        # Yardım mesajını embed olarak gönder
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Commands(bot))