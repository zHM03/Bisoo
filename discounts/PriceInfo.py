import discord
from discord.ext import commands
import aiohttp
import xml.etree.ElementTree as ET

TCMB_API_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"  # Günlük döviz kuru XML verisi

class SteamGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_usd_to_try(self):
        """TCMB API'den USD → TL kurunu çeker"""
        async with aiohttp.ClientSession() as session:
            async with session.get(TCMB_API_URL) as response:
                if response.status != 200:
                    return None  # API'ye ulaşılamadı

                xml_data = await response.text()
                root = ET.fromstring(xml_data)

                # USD'nin alış kurunu çekiyoruz
                for currency in root.findall("Currency"):
                    if currency.get("CurrencyCode") == "USD":
                        usd_to_try = currency.find("ForexBuying").text
                        return float(usd_to_try)  # USD → TL dönüşüm oranı

                return None  # USD kuru bulunamadı

    async def get_game_price(self, game_name):
        """Steam API'den oyunun fiyatını çeker ve TL'ye çevirir"""
        url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&cc=us&l=en"

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
                price_url = f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc=us&l=en"
                async with session.get(price_url) as price_response:
                    if price_response.status != 200:
                        return game_name, "Fiyat bilgisi alınamadı.", game_image

                    price_data = await price_response.json()
                    game_data = price_data.get(str(game_id), {}).get("data", {})

                    if "price_overview" in game_data:
                        price_usd = float(game_data["price_overview"]["final"]) / 100  # Steam fiyatları cent cinsinden döndürüyor
                        usd_to_try = await self.get_usd_to_try()  # TCMB'den döviz kuru al
                        if usd_to_try is None:
                            return game_name, f"Fiyatı: **{price_usd} USD** (Döviz bilgisi alınamadı)", game_image

                        price_try = round(price_usd * usd_to_try, 2)  # TL'ye çevir ve 2 basamaklı göster
                        return game_name, f"Fiyatı: **{price_try} TL** (~{price_usd} USD)", game_image
                    else:
                        return game_name, "Bu oyun şu anda satılmıyor veya fiyat bilgisi yok.", game_image

    @commands.command()
    async def game(self, ctx, *, game_name: str):
        """Belirtilen oyunun Steam fiyatını TL'ye çevirerek embed mesaj olarak gösterir"""
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