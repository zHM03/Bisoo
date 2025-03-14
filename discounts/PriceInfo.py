import discord
from discord.ext import commands
import aiohttp

class SteamGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_usd_to_try_rate(self):
        """Alternatif döviz kuru API'sinden USD/TRY kurunu alır"""
        url = "https://api.exchangerate-api.com/v4/latest/USD"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None  # API'ye ulaşılamadı

                data = await response.json()
                return data["rates"].get("TRY")  # Türkiye kuru

    async def get_game_price(self, game_name):
        """Steam API'den oyunun ABD dolar fiyatını ve kapak fotoğrafını çeker"""
        url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&cc=us&l=us"

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
                game_description = game.get("short_description", "Açıklama bulunamadı.")  # Oyun açıklaması

                # Oyun fiyatını almak için yeni istek at
                price_url = f"https://store.steampowered.com/api/appdetails?appids={game_id}&cc=us&l=tr"
                async with session.get(price_url) as price_response:
                    if price_response.status != 200:
                        return game_name, "Fiyat bilgisi alınamadı.", game_image, game_url, game_description, None

                    price_data = await price_response.json()
                    game_data = price_data.get(str(game_id), {}).get("data", {})

                    if "price_overview" in game_data:
                        price_usd = float(game_data["price_overview"]["final"]) / 100  # Steam fiyatları cent olarak döndürüyor
                        # Oyun türünü almak için
                        genres = [genre["description"] for genre in game_data.get("genres", [])]
                        genres_info = ', '.join(genres) if genres else "Bilinmiyor"

                        return game_name, price_usd, game_image, game_url, game_description, genres_info
                    else:
                        return game_name, None, game_image, game_url, game_description, None

    @commands.command()
    async def game(self, ctx, *, game_name: str):
        """Belirtilen oyunun Steam fiyatını embed mesaj olarak gösterir"""
        await ctx.send("🐱 **Kediler araştırıyor...** ⏳")

        game_name, price_usd, game_image, game_url, game_description, genres_info = await self.get_game_price(game_name)

        if game_name is None:
            await ctx.send(price_usd)  # price_usd burada hata mesajı içeriyor
            return

        usd_to_try = await self.get_usd_to_try_rate()
        if usd_to_try is None:
            await ctx.send("💰 Döviz kuru alınamadı, fiyat TL'ye çevrilemiyor.")
            return

        if price_usd is None:
            price_info = "Bu oyun şu anda satılmıyor veya fiyat bilgisi yok."
        else:
            price_try = price_usd * usd_to_try
            price_info = f"ABD fiyatı: **{price_usd:.2f}$**\nTürk Lirası fiyatı: **{price_try:.2f}₺**"

        # Embed mesaj oluştur
        embed = discord.Embed(
            title=f"🎮 {game_name}",
            description=f"**{price_info}**\n\n🐾 *Kediler bu oyunu oynar mı bilmiyoruz ama fiyatı bu!* 🐾",
            color=discord.Color.orange(),
            url=game_url
        )
        embed.set_thumbnail(url=game_image)
        embed.add_field(name="Açıklama", value=game_description, inline=False)
        embed.add_field(name="Türler", value=genres_info if genres_info else "Bilinmiyor", inline=False)

        embed.set_footer(text="😺 Oyun fiyatlarını kontrol etmek kediler için de önemli!")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SteamGame(bot))