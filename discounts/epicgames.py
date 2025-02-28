import discord
from discord.ext import commands, tasks
import requests
from googletrans import Translator  # Google Translate API kullanacağız

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
            description = game.get("description", "Açıklama bulunamadı.")  # Açıklama varsa al
            if description == "Açıklama bulunamadı.":
                description = "Bu oyun hakkında herhangi bir açıklama sağlanmamış."  # Türkçe açıklama ekleyelim

            # Google Translate kullanarak açıklamayı Türkçeye çeviriyoruz
            translator = Translator()
            translated_description = translator.translate(description, src='en', dest='tr').text

            free_games.append({
                "title": title,
                "url": url,
                "image": image,
                "description": translated_description,  # Çevrilen açıklama
            })

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
                title="🐱Miyaaaav! Bakın ne buldummm!!",
                description=f"**[{game['title']}]({game['url']})** Bedava mama! En sevdiğimm 😻🐾",
                color=discord.Color.orange()
            )
            embed.add_field(name="🎮 Mama Açıklaması:", value=game["description"], inline=False)
            embed.set_image(url=game["image"]) if game["image"] else None
            embed.set_footer(text="Epic Games Store - Bedava Oyunlar", icon_url="https://i.imgur.com/OJt0r5Z.png")

            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EpicGames(bot))
