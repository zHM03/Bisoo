import discord
from discord.ext import commands
import aiohttp
from googletrans import Translator

class SteamGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()

    async def get_exchange_rate(self):
        """Döviz kuru bilgisini getirir (USD -> TRY)."""
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                return data["rates"].get("TRY", None)

    async def get_game_info(self, game_name):
        """Steam API'den oyun bilgilerini çeker ve işler."""
        search_url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&cc=tr&l=tr"
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                if response.status != 200:
                    return None, "Steam API'ye ulaşılamadı."

                data = await response.json()
                if not data["items"]:
                    return None, "Oyun bulunamadı."

                game = data["items"][0]
                game_id = game["id"]
                game_image = game["tiny_image"]

                # Fiyat ve detay bilgileri için ek API isteği
                details_url = f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc=tr&l=tr"
                async with session.get(details_url) as details_response:
                    if details_response.status != 200:
                        return game["name"], "Fiyat bilgisi alınamadı.", game_image, "Bilinmiyor", "Açıklama yok."

                    details_data = await details_response.json()
                    game_data = details_data.get(str(game_id), {}).get("data", {})

                    # Açıklamayı çevir
                    description = game_data.get("short_description", "Açıklama bulunamadı.")
                    translated_desc = self.translator.translate(description, src='en', dest='tr').text

                    # Tür bilgisi
                    categories = game_data.get("categories", [])
                    game_type = "Co-op" if any(cat["description"].lower() in ["multiplayer", "co-op"] for cat in categories) else "Tek oyunculu"

                    # Fiyat bilgisi
                    if "price_overview" in game_data:
                        price = game_data["price_overview"]["final_formatted"]
                        exchange_rate = await self.get_exchange_rate()
                        if exchange_rate:
                            try:
                                price_in_try = round(float(game_data["price_overview"]["final"]) * exchange_rate)
                                price = f"{price} - {price_in_try} TL"
                            except ValueError:
                                pass  # Hatalı veri varsa geç

                    else:
                        price = "Bu oyun şu anda satılmıyor."

                    return game["name"], price, game_image, game_type, translated_desc

    @commands.command()
    async def game(self, ctx, *, game_name: str):
        """Oyunun Steam fiyatı ve detaylarını embed içinde gösterir."""
        await ctx.send("🐱 Kediler araştırıyor... ⏳")

        name, price, image, game_type, description = await self.get_game_info(game_name)

        if name is None:
            await ctx.send(price)
            return

        # Embed mesajı oluştur
        embed = discord.Embed(
            title=f"🎮 {name}",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=image)

        # Sıralama: Açıklama → Tür → Fiyat
        embed.add_field(name="📝 Açıklama", value=description, inline=False)
        embed.add_field(name="🎭 Tür", value=game_type, inline=False)
        embed.add_field(name="💰 Fiyat", value=price, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SteamGame(bot))