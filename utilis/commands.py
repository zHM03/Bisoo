import discord
from discord.ext import commands    

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        """Yardım komutunu sağlar (Kedi Temalı)"""
        embed = discord.Embed(
            title="🐱 Bisooo yardıma ulaştı! 🐾", 
            description="Miyav! Beni çağırdığını duydum! İşte sana tüylerimi kabartarak hazırladığım komutlar!", 
            color=discord.Color.orange()
        )

        # 🎵 Müzik Komutları
        embed.add_field(
            name="🎵 Mırnav Melodileri",
            value=(
                "▶️ **!p** `<şarkı adı / YouTube linki>` → Tırnaklarımla plağı çeviriyorum\n"
                "⏸️ **!s** → Şşş... Biraz uyku vakti\n"
                "⏯️ **!r** → Miyav! Parti devam etsin\n"
                "⏹️ **!l** → Mırlamadan uzaklaşıyorum\n"
            ),
            inline=False
        )

        # 😺 Eğlenceli Komutlar
        embed.add_field(
            name="😸 Eğlenceli Komutlar",
            value=(
                "😹 **!j** → Biraz kahkaha iyidir! Miyav-miyav bir şaka geliyor\n"
                "🙀 **!kedy** → Pati dostlarımı ifşa ediyorum!\n"
            ),
            inline=False
        )

        # 🐾 Patisyonel Komutlar
        embed.add_field(
            name="🐾 Patisyonel Komutlar",
            value=(
                "🌤 **!h** `<şehir>` → Hava nasıl, biliyor musun? Ben de bilmiyorum! Ama öğrenebiliriz...\n"
                "💰 **!crypto** `<coin>` → Coin fiyatını gösteririm (Mama parası lazim!)\n"
            ),
            inline=False
        )

        # Thumbnail ve Footer ekleyelim
        embed.set_thumbnail(url="https://i.imgur.com/90rVRLz.jpeg")  # Küçük kedi görseli
        embed.set_footer(text="Tüylerimi kabarttım, her zaman yardıma hazırım! Miyav seslenmen yeter! 🐾")

        await ctx.send(embed=embed)

    @commands.command(name="d")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Belirtilen sayıda mesajı siler"""
        if amount < 1:
            await ctx.send("En az 1 mesaj silmelisin!", delete_after=5)
            return

        deleted = await ctx.channel.purge(limit=amount + 1)  # Komut mesajını da siler
        await ctx.send(f"🧹 {len(deleted) - 1} mesaj silindi!", delete_after=5)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Yanlış komut kullanıldığında yardım mesajını atar"""
        if isinstance(error, commands.CommandNotFound):
            # Yanlış komut kullanıldığında yardım komutunu tetikler
            await self.help(ctx)

async def setup(bot):
    await bot.add_cog(Commands(bot))