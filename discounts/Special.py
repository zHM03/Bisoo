import discord
from discord.ext import commands
import aiohttp

class SpecialDeals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_exchange_rate(self):
        """USD/TRY kuru almak için ExchangeRate-API'den veriyi çeker."""
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                try:
                    usd_try = float(data["rates"]["TRY"])
                    return usd_try
                except (KeyError, ValueError):
                    return None

    async def fetch_steam_specials(self, usd_try):
        """Steam'den indirimli oyunları alır ve TL fiyatlarını hesaplar."""
        url = f"https://store.steampowered.com/api/featuredcategories"
        games = []

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                specials = data.get("specials", {}).get("items", [])

                for i, game in enumerate(specials[:10]):  # Yalnızca ilk 10 oyunu alıyoruz
                    name = game.get("name", "Bilinmiyor")
                    appid = game.get("id", "")
                    old_price = game.get("original_price", 0) / 100  # Cent -> Dolar
                    new_price = game.get("final_price", 0) / 100  # Cent -> Dolar
                    url = f"https://store.steampowered.com/app/{appid}"

                    if old_price == 0 or new_price == 0:
                        continue  # Hatalı fiyat verilerini atla

                    # TL'ye çevirme
                    old_price_try = old_price * usd_try
                    new_price_try = new_price * usd_try

                    games.append({
                        "name": name,
                        "old_price": f"${old_price:.2f} ({old_price_try:.2f} TL)",
                        "new_price": f"${new_price:.2f} ({new_price_try:.2f} TL)",
                        "url": url
                    })

        return games

    @commands.command(name="special")
    async def special(self, ctx):
        """Steam'deki indirimli oyunları listeler ve TL fiyatlarını hesaplar"""
        usd_try = await self.fetch_exchange_rate()
        if not usd_try:
            await ctx.send("USD/TRY kuru alınamadı, fiyatları sadece dolar olarak göstereceğim.")
            usd_try = 1  # Eğer kur alınamazsa TL çevirisi yapılmasın

        games = await self.fetch_steam_specials(usd_try)

        if not games:
            await ctx.send("Şu an Steam indirimli oyunlarını çekemedim.")
            return

        embed = discord.Embed(
            title="🐾 Bisooo İndirimli Mama Buldu! 🐾",
            description="İndirimdeki mamaları kaçırma! 🏷️",
            color=discord.Color.orange()  # Kedi temalı yeşil renk
        )

        for game in games:
            embed.add_field(
                name=f"🐾 {game['name']} 🐾",
                value=f"Eski Fiyat: ~~{game['old_price']}~~\nYeni Fiyat: **{game['new_price']}**\n"
                      f"[Steam Sayfası]({game['url']})",
                inline=False
            )

        embed.set_footer(text="İndirim yakalarken, bir kedinin fareyi yakaladığı kadar hızlı olmalısın 😼!")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SpecialDeals(bot))