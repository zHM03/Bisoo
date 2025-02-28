import discord
from discord.ext import commands
import requests

EPIC_API_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

class EpicGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_free_games(self):
        """Epic Games Store'daki ücretsiz oyunları çeker"""
        response = requests.get(EPIC_API_URL)
        if response.status_code != 200:
            return "Epic Games verisi alınamadı."

        data = response.json()
        games = data["data"]["Catalog"]["searchStore"]["elements"]

        free_games = []
        for game in games:
            title = game["title"]
            url = f"https://store.epicgames.com/p/{game['productSlug']}"
            free_games.append(f"🎮 **{title}**\n🔗 [İndir]({url})")

        return "\n\n".join(free_games) if free_games else "Şu anda ücretsiz oyun yok."

    @commands.command(name="freegames")
    async def free_games(self, ctx):
        """!freegames komutu çalıştırıldığında Epic Games oyunlarını gösterir"""
        games = self.get_free_games()
        await ctx.send(games)

async def setup(bot):
    await bot.add_cog(EpicGames(bot))
