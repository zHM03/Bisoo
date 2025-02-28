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
            return None

        data = response.json()
        games = data["data"]["Catalog"]["searchStore"]["elements"]

        free_games = []
        for game in games:
            title = game["title"]
            url = f"https://store.epicgames.com/p/{game.get('productSlug', '')}"
            image = game["keyImages"][0]["url"] if "keyImages" in game and game["keyImages"] else None

            free_games.append({"title": title, "url": url, "image": image})

        return free_games if free_games else None

    @commands.command(name="freegames")
    async def free_games(self, ctx):
        """!freegames komutu çalıştırıldığında Epic Games oyunlarını belirtilen kanala embed olarak yollar"""
        channel = self.bot.get_channel(1341428278879326298)
        if not channel:
            await ctx.send("Belirtilen kanal bulunamadı.")
            return
        
        games = self.get_free_games()
        if not games:
            await channel.send("Şu anda ücretsiz oyun yok.")
            return

        for game in games:
            embed = discord.Embed(title=game["title"], url=game["url"], color=discord.Color.blue())
            embed.set_image(url=game["image"]) if game["image"] else None
            embed.set_footer(text="Epic Games Store - Ücretsiz Oyunlar")

            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EpicGames(bot))
