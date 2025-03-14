import discord
from discord.ext import commands
import aiohttp
from googletrans import Translator

class SteamGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()

    async def get_exchange_rate(self):
        """TCMB API'den USD/TRY döviz kuru bilgisini alır"""
        url = "https://api.tcmb.gov.tr/evds/api/series/TCMB/DK_TL?date=2025-03-14&format=JSON"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                if data["data"]:
                    return float(data["data"][0]["value"])  # Döviz kuru değeri
                return None

    async def get_game_price(self, game_name):
        """Steam API'den oyunun Türkiye fiyatını, kapak fotoğrafını ve detaylarını çeker"""
        url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&cc=tr&l=tr"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None, "Steam API'ye ulaşılamadı.", None, None, None, None

                data = await response.json()

                if not data["items"]:
                    return None, "Oyun bulunamadı.", None, None, None, None

                game = data["items"][0]  # İlk sonucu al
                game_id = game["id"]  # Steam oyun ID'si
                game_name = game["name"]  # Oyunun tam adı
                game_url = f"https://store.steampowered.com/app/{game_id}"
                game_image = game["tiny_image"]  # Oyunun kapak fotoğrafı

                # Oyun fiyatını almak için yeni istek at
                price_url = f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc=tr&l=tr"
                async with session.get(price_url) as price_response:
                    if price_response.status != 200:
                        return game_name, "Fiyat bilgisi alınamadı.", game_image, None, None, None

                    price_data = await price_response.json()
                    game_data = price_data.get(str(game_id), {}).get("data", {})

                    # Oyun açıklamasını al ve Türkçeye çevir
                    description = game_data.get("short_description", "Açıklama bulunamadı.")
                    description_translated = self.translator.translate(description, src='en', dest='tr').text

                    categories = game_data.get("categories", [])
                    multiplayer = "Coop" if any(cat["description"].lower() in ["multiplayer", "co-op"] for cat in categories) else "Tek oyunculu"

                    if "price_overview" in game_data:
                        final_price = game_data["price_overview"]["final_formatted"]
                        initial_price = game_data["price_overview"].get("initial_formatted", "Bilinmiyor")
                        discount_percent = game_data["price_overview"].get("discount_percent", 0)

                        # Döviz kuru bilgisini al
                        exchange_rate = await self.get_exchange_rate()
                        if exchange_rate:
                            try:
                                price_in_try = float(game_data["price_overview"]["final"]) * exchange_rate
                                price_in_try = round(price_in_try)
                                final_price = f"{final_price} - {price_in_try} TL"
                            except ValueError:
                                pass  # Hatalı veri varsa geç

                        # İndirimli fiyat varsa
                        if discount_percent > 0:
                            discount_message = f"İndirimli Fiyat: **{final_price}**\nOrijinal Fiyat: **{initial_price}**\nİndirim: %{discount_percent}"
                        else:
                            discount_message = f"Fiyat: **{final_price}**"

                        return game_name, discount_message, game_image, multiplayer, description_translated, discount_percent
                    else:
                        return game_name, "Bu oyun şu anda satılmıyor veya fiyat bilgisi yok.", game_image, multiplayer, description_translated, None

    @commands.command()
    async def game(self, ctx, *, game_name: str):
        """Belirtilen oyunun Steam fiyatını ve detaylarını embed mesaj olarak gösterir"""
        await ctx.send("🐱 Kediler araştırıyor... ⏳")

        game_name, price_info, game_image, multiplayer, description, discount_percent = await self.get_game_price(game_name)

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

        # Oyun açıklamasını ve türünü ekle
        embed.add_field(name="Açıklama", value=description, inline=False)
        embed.add_field(name="Tür", value=multiplayer, inline=False)

        # Eğer indirim varsa, footer'ı buna göre değiştirebiliriz.
        if discount_percent > 0:
            embed.set_footer(text="🔥 İndirimli fiyatlar, kaçırmayın! 🏷️")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SteamGame(bot))