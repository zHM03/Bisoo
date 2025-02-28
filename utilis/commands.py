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
            title="Bisooo'nun Yetenekleri", 
            description="Bisooo ile neler yapabilirsiniz:", 
            color=discord.Color.orange()  # Embed için kedici bir renk
        )
    
        help_message = (
            "**!p:** *<Şarkı ismi veya YouTube linki> Mırlayarak şarkınızı çalarım*\n"
            "**!s:** *Mırlamayı durdururum, sessiz olurum*\n"
            "**!r:** *Mırlamaya devam ederim*\n"
            "**!l:** *Yanınızdan ayrılırım, patilerimle veda ederim :(*\n"
            "----------------------------------------------------\n"
            "**Oyun Takip Etme Komutları:**\n"
            "**!addgame:** *<Oyun adı veya steam linki> Listeye eklerim ve indirime girince size miyavlarım*\n"
            "**!listgames:** *Takip ettiğim oyunları liste olarak çıkarırım*\n"
            "**!removegame:** *<Oyun adı> Oyun listemden silinir*\n"
            "----------------------------------------------------\n"
            "**Diğer Komutlar:**\n"
            "**!h:** *<Şehir> Merak ettiğiniz şehrin hava durumunu tüylerimle okurum*\n"
            "**!j:** *Komik şakalar yaparım*\n"
            "**!kedy:** *Arkadaşlarımın yaramazlıklarını ifşalarım*\n"
            "**!crypto:** *<coin> coin'in fiyatını patilerimle gösteririm*\n"
        )
        
        # Yardım mesajını embed'in içerisine ekliyoruz
        embed.add_field(name="Müzik Komutları:", value=help_message, inline=False)
    
        # Embed'e footer ekliyoruz
        embed.set_footer(text="Şimdilik bu kadarrr🐱")
        
        # Yardım mesajını embed olarak gönder
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Commands(bot))
