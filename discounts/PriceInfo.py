import discord
from discord.ext import commands
import aiohttp

class SteamGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_game_price(self, game_name):
        """Steam API'den oyunun Türkiye fiyatını ve kapak fotoğrafını çeker"""
        url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&cc=tr&l=tr"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None, "Steam API'ye ulaşılamadı.", None

                data = await response.json()

                if not data["items"]:
                    return None, "Oyun bulunamadı.", None

                game = data["items"][0]  # İlk sonucu al
                game_id = game["id"]  # Steam oyun ID'si
                game_name = game["name"]  # Oyunun tam adı
                game_url = f"https://store.steampowered.com/app/{game_id}"
                game_image = game["tiny_image"]  # Oyunun kapak fotoğrafı

                # Oyun fiyatını almak için yeni istek at
                price_url = f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc=tr&l=tr"
                async with session.get(price_url) as price_response:
                    if price_response.status != 200:
                        return game_name, "Fiyat bilgisi alınamadı.", game_image

                    price_data = await price_response.json()
                    game_data = price_data.get(str(game_id), {}).get("data", {})

                    if "price_overview" in game_data:
                        price = game_data["price_overview"]["final_formatted"]
                        return game_name, f"Fiyatı: **{price} TL**", game_image
                    else:
                        return game_name, "Bu oyun şu anda satılmıyor veya fiyat bilgisi yok.", game_image

    @commands.command()
    async def game(self, ctx, *, game_name: str):
        """Belirtilen oyunun Steam fiyatını embed mesaj olarak gösterir"""
        await ctx.send("🐱 **Kediler araştırıyor...** ⏳")

        game_name, price_info, game_image = await self.get_game_price(game_name)

        if game_name is None:
            await ctx.send(price_info)
            return

        # Embed mesaj oluştur
        embed = discord.Embed(
            title=f"🎮 {game_name}",
            description=f"**{price_info}**\n\n🐾 *Kediler bu oyunu oynar mı bilmiyoruz ama fiyatı bu!* 🐾",
            color=discord.Color.orange(),
        )
        embed.set_thumbnail(url=game_image)
        embed.set_footer(text="😺 Oyun fiyatlarını kontrol etmek kediler için de önemli!")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SteamGame(bot))