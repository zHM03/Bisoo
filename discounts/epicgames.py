import discord
from discord.ext import commands, tasks
import requests

EPIC_API_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

class EpicGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.latest_games = set()  # Daha önce paylaşılan oyunları takip eder
        self.check_free_games.start()  # Bot açıldığında otomatik kontrol başlar

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

    @tasks.loop(hours=1)  # Her saat başı kontrol eder
    async def check_free_games(self):
        """Epic Games ücretsiz oyunlarını belirli aralıklarla kontrol eder"""
        channel = self.bot.get_channel(1341428278879326298)
        if not channel:
            print("Belirtilen kanal bulunamadı.")
            return

        games = self.get_free_games()
        if not games:
            return  # Eğer yeni oyun yoksa, bir şey gönderme

        for game in games:
            if game["title"] in self.latest_games:
                continue  # Eğer oyun daha önce paylaşılmışsa, tekrar paylaşma

            self.latest_games.add(game["title"])  # Yeni oyunları kaydet

            # Kedi temalı embed mesajı
            embed = discord.Embed(
                title="🐱 Miyaaaav! Bakın ne buldummm! 🐱",  # Başlık artık sadece düz metin
                description=f"**[{game['title']}]({game['url']})** Beleş mama! 😻🐾",
                color=discord.Color.orange()
            )
            embed.set_image(url=game["image"]) if game["image"] else None
            embed.set_footer(text="Bisooo ile beleşçilik", icon_url="https://i.imgur.com/OJt0r5Z.png")

            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EpicGames(bot))
