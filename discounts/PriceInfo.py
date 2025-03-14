import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

class EpicGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_game_price(self, game_name):
        """Epic Games Store'dan oyunun fiyatını alır"""
        url = f"https://www.epicgames.com/store/tr/p/{game_name}"
        
        response = requests.get(url)
        
        if response.status_code != 200:
            return None, "Epic Games Store'a ulaşılamadı."
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Fiyat bilgisini almak
        price_tag = soup.find('span', {'class': 'css-v4l7v8'})  # Fiyat sınıfı
        if not price_tag:
            return None, "Fiyat bilgisi alınamadı veya oyun bulunamadı."
        
        price = price_tag.get_text(strip=True)
        
        return game_name, f"**{price}**", None

    @commands.command()
    async def epicgame(self, ctx, *, game_name: str):
        """Belirtilen oyunun Epic Games fiyatını embed mesaj olarak gösterir"""
        await ctx.send("🐱 **Kediler araştırıyor...** ⏳")

        game_name, price_info, game_image = self.get_game_price(game_name)

        if game_name is None:
            await ctx.send(price_info)
            return

        # Embed mesaj oluştur
        embed = discord.Embed(
            title=f"🎮 {game_name}",
            description=f"**Fiyatı:** {price_info}\n\n🐾 *Kediler bu oyunu oynar mı bilmiyoruz ama fiyatı bu!* 🐾",
            color=discord.Color.orange(),
        )
        embed.set_footer(text="😺 Oyun fiyatlarını kontrol etmek kediler için de önemli!")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EpicGame(bot))