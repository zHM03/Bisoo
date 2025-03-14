import discord
from discord.ext import commands
import aiohttp

class SteamGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_game_price(self, game_name):
        """Steam API'den oyunun Türkiye fiyatını, kapak fotoğrafını ve detaylarını çeker"""
        steam_url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&cc=tr&l=tr"
        epic_url = f"https://www.epicgames.com/store/api/storesearch?term={game_name}"

        async with aiohttp.ClientSession() as session:
            # Steam verisini al
            async with session.get(steam_url) as response:
                if response.status != 200:
                    return None, "Steam API'ye ulaşılamadı.", None, None, None

                steam_data = await response.json()
                if not steam_data["items"]:
                    return None, "Oyun Steam'de bulunamadı.", None, None, None

                steam_game = steam_data["items"][0]  # İlk sonucu al
                steam_game_id = steam_game["id"]
                steam_game_name = steam_game["name"]
                steam_game_image = steam_game["tiny_image"]

                # Steam fiyatını almak için yeni istek at
                steam_price_url = f"https://store.steampowered.com/api/appdetails?appids={steam_game_id}&cc=tr&l=tr"
                async with session.get(steam_price_url) as price_response:
                    if price_response.status != 200:
                        return steam_game_name, "Fiyat bilgisi alınamadı.", steam_game_image, None, None

                    steam_price_data = await price_response.json()
                    steam_game_data = steam_price_data.get(str(steam_game_id), {}).get("data", {})
                    if "price_overview" in steam_game_data:
                        steam_final_price = steam_game_data["price_overview"]["final_formatted"]
                        steam_initial_price = steam_game_data["price_overview"].get("initial_formatted", "Bilinmiyor")
                        steam_discount_percent = steam_game_data["price_overview"].get("discount_percent", 0)

                        if steam_discount_percent > 0:
                            steam_discount_message = f"İndirimli Fiyat: **{steam_final_price} TL**\nOrijinal Fiyat: **{steam_initial_price} TL**\nİndirim: %{steam_discount_percent}"
                        else:
                            steam_discount_message = f"Fiyat: **{steam_final_price} TL**"
                    else:
                        steam_discount_message = "Bu oyun şu anda satılmıyor veya fiyat bilgisi yok."

            # Epic Games verisini al
            async with session.get(epic_url) as response:
                if response.status != 200:
                    return steam_game_name, "Epic Games Store API'ye ulaşılamadı.", steam_game_image, None, None

                epic_data = await response.json()
                if not epic_data.get('data'):
                    return steam_game_name, "Oyun Epic Games Store'da bulunamadı.", steam_game_image, None, None

                epic_game = epic_data['data'][0]  # İlk sonucu al
                epic_game_name = epic_game["title"]
                epic_game_image = epic_game["keyImages"][0]["url"]
                epic_game_price = epic_game["price"]["totalPrice"]["formattedPrice"]
                epic_discount_percent = epic_game["price"]["discountPercent"]

                if epic_discount_percent > 0:
                    epic_discount_message = f"İndirimli Fiyat: **{epic_game_price}**\nİndirim: %{epic_discount_percent}"
                else:
                    epic_discount_message = f"Fiyat: **{epic_game_price}**"

        return steam_game_name, steam_discount_message, steam_game_image, epic_discount_message, epic_game_image

    @commands.command()
    async def game(self, ctx, *, game_name: str):
        """Belirtilen oyunun Steam ve Epic Games fiyatlarını embed mesaj olarak gösterir"""
        await ctx.send("🐱 **Kediler araştırıyor...** ⏳")

        steam_name, steam_price_info, steam_image, epic_price_info, epic_image = await self.get_game_price(game_name)

        if steam_name is None:
            await ctx.send(steam_price_info)
            return

        # Embed mesaj oluştur
        embed = discord.Embed(
            title=f"🎮 {steam_name}",
            description=f"**Steam Fiyatı:** {steam_price_info}\n**Epic Games Fiyatı:** {epic_price_info}\n\n🐾 *Kediler bu oyunu oynar mı bilmiyoruz ama fiyatı bu!* 🐾",
            color=discord.Color.orange(),
        )
        embed.set_thumbnail(url=steam_image)

        # Epic Games için ayrı bir resim ekleyelim
        embed.add_field(name="Epic Games", value=epic_price_info, inline=False)
        embed.set_footer(text="😺 Oyun fiyatlarını kontrol etmek kediler için de önemli!")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SteamGame(bot))