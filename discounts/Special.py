import discord
from discord.ext import commands
import aiohttp

class SpecialDeals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="special")
    async def special(self, ctx):
        """Steam'deki indirimli oyunları listeler"""
        url = "https://store.steampowered.com/api/featuredcategories"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await ctx.send("Steam verilerine ulaşılamadı.")
                    return
                
                data = await response.json()
                specials = data.get("specials", {}).get("items", [])

                if not specials:
                    await ctx.send("Şu an Steam'de indirimli oyun bulunamadı.")
                    return

                embed = discord.Embed(title="Steam İndirimli Oyunlar", color=discord.Color.blue())

                for game in specials[:10]:  # İlk 5 oyunu gösteriyoruz
                    name = game["name"]
                    old_price = game.get("original_price", 0) / 100
                    new_price = game.get("final_price", 0) / 100
                    url = f"https://store.steampowered.com/app/{game['id']}"

                    embed.add_field(
                        name=name,
                        value=f"~~{old_price} TL~~ → **{new_price} TL**\n[Steam Sayfası]({url})",
                        inline=False
                    )

                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SpecialDeals(bot))