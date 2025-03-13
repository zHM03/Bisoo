import discord
from discord.ext import commands
import requests

class GamePriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = "37d8ca093b6022f360d8e48ce69932797bc3c4e2"
        self.url = "https://api.example.com/game-price"  # API URL'sini burada değiştirebilirsiniz

    @commands.command()
    async def gamefiyat(self, ctx, *, game_name: str):
        """Oyun adı ile fiyat sorgulama"""
        
        params = {
            'api_key': self.api_key,
            'game_name': game_name
        }

        response = requests.get(self.url, params=params)

        if response.status_code == 200:
            data = response.json()
            if 'price' in data:
                await ctx.send(f"{game_name} oyununun fiyatı: {data['price']}")
            else:
                await ctx.send(f"{game_name} oyunu için fiyat bulunamadı.")
        else:
            await ctx.send(f"API hatası: {response.status_code}")

# Cog'u botumuza ekliyoruz
async def setup(bot):
    await bot.add_cog(GamePriceCog(bot))