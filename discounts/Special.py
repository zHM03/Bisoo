import discord
from discord.ext import commands
import aiohttp

class SpecialDeals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_steam_specials(self):
        url = "https://store.steampowered.com/api/featuredcategories"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                specials = data.get("specials", {}).get("items", [])

                result = []
                for game in specials[:5]:  # İlk 5 indirimli oyunu al
                    name = game.get("name", "Bilinmiyor")
                    appid = game.get("id", "")
                    old_price = game.get("original_price", 0) / 100
                    new_price = game.get("final_price", 0) / 100
                    url = f"https://store.steampowered.com/app/{appid}"

                    if old_price == 0 or new_price == 0:
                        continue  # Hatalı fiyat verilerini atla

                    # Oyun detaylarını çek (storesearch API ile)
                    details = await self.fetch_game_details(name)

                    result.append({
                        "name": name,
                        "old_price": f"{old_price:.2f} TL",
                        "new_price": f"{new_price:.2f} TL",
                        "url": url,
                        "description": details
                    })

                return result

    async def fetch_game_details(self, game_name):
        """Steam StoreSearch API ile oyun açıklaması alır"""
        search_url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&cc=tr&l=tr"

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                if response.status != 200:
                    return "Açıklama bulunamadı."
                
                data = await response.json()
                if "items" in data and len(data["items"]) > 0:
                    return data["items"][0].get("short_description", "Açıklama yok.")
                return "Açıklama bulunamadı."

    @commands.command(name="special")
    async def special(self, ctx):
        """Steam'deki indirimli oyunları listeler"""
        games = await self.fetch_steam_specials()

        if not games:
            await ctx.send("Şu an Steam indirimli oyunlarını çekemedim.")
            return

        embed = discord.Embed(title="Steam İndirimli Oyunlar", color=discord.Color.blue())

        for game in games:
            embed.add_field(
                name=game["name"],
                value=f"~~{game['old_price']}~~ → **{game['new_price']}**\n{game['description']}\n[Steam Sayfası]({game['url']})",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SpecialDeals(bot))