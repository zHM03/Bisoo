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
        """Yardım komutunu sağlar (Kedi Temalı)"""
        embed = discord.Embed(
            title="🐱 Bisooo'nun Yetenekleri! 🐾", 
            description="Biso ile neler yapabilirsiniz?", 
            color=discord.Color.orange()
        )
    
        help_message = (
            "😺 **Müzik Komutları:**\n"
            "🐾 **!p:** *<Şarkı ismi veya YouTube linki> Mırnav melodinizi çalarım*\n"
            "🐾 **!s:** *Biraz kestirmek mi istiyorsunuz?*\n"
            "🐾 **!r:** *Parti devam ediyor!*\n"
            "🐾 **!l:** *Yanınızdan ayrılırım... 😿*\n"
            "----------------------------------------------------\n"
            "🐱 **Diğer Miyav Komutlar:**\n"
            "🌤 **!h:** *<Şehir> Merak ettiğiniz şehrin hava durumunu tüylerimle hissederim*\n"
            "🤣 **!j:** *Patilerimle gülmeye hazır olun!*\n"
            "😼 **!kedy:** *Arkadaşlarımı ifşalarım (Ama sakın beni ele vermeyin!)*\n"
            "💰 **!crypto:** *<coin> coin'in fiyatını gösterebilirim (Mama parası lazım!)*\n"
            "----------------------------------------------------\n"
            "🐾 ***Miyav! Şimdilik bu kadarrr...***"
        )
        
        embed.description = help_message
        
        # Kedi temalı küçük bir resim ekleyelim
        embed.set_thumbnail(url="https://imgur.com/a/FsG1xAJ")  # Doğru kedi görseli linki
        embed.set_footer(text="Biso her zaman burada! 😺")
    
        # **Burada eksik olan satır!**
        await ctx.send(embed=embed)  # Bu satır fonksiyonun dışına çıkmıştı, içine aldım.




    @commands.command(name="d")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Belirtilen sayıda mesajı siler"""
        if amount < 1:
            await ctx.send("En az 1 mesaj silmelisin!", delete_after=5)
            return

        deleted = await ctx.channel.purge(limit=amount + 1)  # Komut mesajını da siler
        await ctx.send(f"🧹 {len(deleted) - 1} mesaj silindi!", delete_after=5)

async def setup(bot):
    await bot.add_cog(Commands(bot))
