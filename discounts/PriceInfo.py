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
                game_url = f"https://store.steampowered.com/app/{game_id}"  # Oyunun Steam sayfasının linki

                # Fiyat ve detay bilgileri için ek API isteği
                details_url = f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc=tr&l=tr"
                async with session.get(details_url) as details_response:
                    if details_response.status != 200:
                        return game["name"], "Fiyat bilgisi alınamadı.", game_image, "Bilinmiyor", "Açıklama yok.", game_url

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
                        price_info = game_data["price_overview"]
                        price_in_cents = price_info["final"]  # **Cent cinsinden**
                        original_price_in_cents = price_info["initial"]  # **Orijinal fiyat**
                        discount_percent = price_info["discount_percent"]  # **İndirim yüzdesi**

                        usd_price = price_in_cents / 100  # **Gerçek dolara çevir**
                        original_usd_price = original_price_in_cents / 100  # **Orijinal fiyatı dolara çevir**
                        formatted_usd_price = f"${usd_price:.2f}"
                        formatted_original_price = f"${original_usd_price:.2f}"

                        # Döviz kuru al ve TL'ye çevir
                        exchange_rate = await self.get_exchange_rate()
                        if exchange_rate:
                            price_in_try = round(usd_price * exchange_rate)  # **TL karşılığını hesapla**
                            original_price_in_try = round(original_usd_price * exchange_rate)  # **Orijinal fiyat TL**
                            price = f"{formatted_usd_price} (~{price_in_try} TL)"

                            if discount_percent > 0:
                                price = f"Şu an indirimde! **{formatted_usd_price} (~{price_in_try} TL)**\n" \
                                        f"Önceki fiyat: ~~{formatted_original_price} (~{original_price_in_try} TL~~)"
                        else:
                            price = formatted_usd_price
                    else:
                        price = "Bu oyun şu anda satılmıyor."

                    return game["name"], price, game_image, game_type, translated_desc, game_url

    @commands.command()
    async def game(self, ctx, *, game_name: str):
        """Oyunun Steam fiyatı ve detaylarını embed içinde gösterir."""
        
        name, price, image, game_type, description, game_url = await self.get_game_info(game_name)

        if name is None:
            await ctx.send(price)
            return

        # Embed mesajı oluştur
        embed = discord.Embed(
            title=f"🐾 {name} 🐾",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=image)

        # Sıralama: Açıklama → Tür → Fiyat
        embed.add_field(name="Bakalım bu oyun neymiş", value=description, inline=False)
        embed.add_field(name="Tür", value=game_type, inline=False)
        embed.add_field(name="Fiyat", value=price, inline=False)

        # Fiyatların altında Steam linkini yazıyoruz
        embed.description += f"\n[Steam Sayfası]({game_url})"  # Steam sayfasına yönlendiren linki ekliyoruz

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SteamGame(bot))