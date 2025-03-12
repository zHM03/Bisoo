import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

class SteamDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "https://steamdb.info/app/"

    @commands.command(name="price")
    async def fetch_price(self, ctx, *, game_name: str):
        """SteamDB'den oyunun fiyat bilgisini ve indirim geçmişini alır."""
        game_id = await self.get_steam_game_id(game_name)
        if not game_id:
            return await ctx.send(f"Oyun '{game_name}' SteamDB üzerinde bulunamadı.")

        url = f"{self.base_url}{game_id}/"
        response = requests.get(url)
        if response.status_code != 200:
            return await ctx.send("SteamDB verisi alınamadı. Lütfen daha sonra tekrar deneyin.")

        soup = BeautifulSoup(response.text, "html.parser")

        # Güncel fiyat bilgisi
        current_price_tag = soup.find("div", class_="price")
        if current_price_tag:
            current_price = current_price_tag.get_text(strip=True)
        else:
            current_price = "Bilinmiyor"

        # İndirim geçmişi bilgisi
        discount_history_tag = soup.find("table", class_="table table-striped")
        discount_history = "İndirim geçmişi bulunamadı."

        if discount_history_tag:
            rows = discount_history_tag.find_all("tr")
            # İndirimlerin bulunduğu tabloyu işleyelim
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    discount_history = f"Son indirim: {cols[0].get_text(strip=True)}, Fiyat: {cols[1].get_text(strip=True)}"
                    break  # İlk indirim bilgisi yeterli

        embed = discord.Embed(
            title=f"{game_name} - Fiyat ve İndirim Bilgisi",
            url=f"https://steamdb.info/app/{game_id}/",
            color=discord.Color.blue()
        )
        embed.add_field(name="Güncel Fiyat", value=current_price, inline=False)
        embed.add_field(name="Son İndirim Geçmişi", value=discount_history, inline=False)

        await ctx.send(embed=embed)

    async def get_steam_game_id(self, game_name):
        """Oyun adından SteamDB ID'sini alır"""
        search_url = "https://steamdb.info/search/"
        params = {"q": game_name}
        
        response = requests.get(search_url, params=params)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        game_link = soup.find("a", class_="app")
        
        if game_link:
            game_id = game_link["href"].split("/")[2]
            return game_id
        
        return None

async def setup(bot):
    await bot.add_cog(SteamDB(bot))