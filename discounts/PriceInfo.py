import discord
from discord.ext import commands
import aiohttp

class SteamGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_game_price(self, game_name):
        """Steam API'den oyunun Türkiye fiyatını çeker"""
        url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&cc=tr&l=tr"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return "Steam API'ye ulaşılamadı."

                data = await response.json()

                if not data["items"]:
                    return "Oyun bulunamadı."

                game = data["items"][0]  # İlk sonucu al
                game_id = game["id"]  # Steam oyun ID'si
                game_url = f"https://store.steampowered.com/app/{game_id}"

                # Oyun fiyatını almak için yeni istek at
                price_url = f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc=tr&l=tr"
                async with session.get(price_url) as price_response:
                    if price_response.status != 200:
                        return "Fiyat bilgisi alınamadı."

                    price_data = await price_response.json()
                    game_data = price_data.get(str(game_id), {}).get("data", {})

                    if "price_overview" in game_data:
                        price = game_data["price_overview"]["final_formatted"]
                        return f"**{game_name}** fiyatı: {price} TL\n[Steam Sayfası]({game_url})"
                    else:
                        return f"**{game_name}** şu anda satılmıyor veya fiyat bilgisi yok.\n[Steam Sayfası]({game_url})"

    @commands.command()
    async def game(self, ctx, *, game_name: str):
        """Belirtilen oyunun Steam fiyatını getirir (Türkiye fiyatı)"""
        await ctx.send("Oyun fiyatı aranıyor... ⏳")
        price_info = await self.get_game_price(game_name)
        await ctx.send(price_info)

async def setup(bot):
    await bot.add_cog(SteamGame(bot))