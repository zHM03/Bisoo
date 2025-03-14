import discord
import requests
from discord.ext import commands

class GameInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.steam_api_key = "0C9F01F93B0D19BB2F241A38A7F5668F"  # Buraya Steam API anahtarınızı girin

    @commands.command()
    async def game(self, ctx, *, game_name: str):
        # Steam arama API'si
        search_url = f"http://api.steampowered.com/ISteamApps/GetAppList/v2/"
        try:
            # Steam API'den oyunların listesine erişiyoruz
            response = requests.get(search_url)
            data = response.json()
            
            # Oyun adıyla eşleşen ID'yi bulalım
            game_id = None
            for game in data['applist']['apps']:
                if game_name.lower() in game['name'].lower():  # Oyun adı küçük harfe çevrilmiş
                    game_id = game['appid']
                    break
            
            if not game_id:
                await ctx.send("Bu oyun bulunamadı!")
                return
            
            # Oyun bilgilerini almak için detayları çekiyoruz
            game_details_url = f"http://store.steampowered.com/api/appdetails?appids={game_id}"
            game_details = requests.get(game_details_url).json()

            if not game_details[str(game_id)]['success']:
                await ctx.send("Oyun bilgileri alınırken bir hata oluştu.")
                return
            
            game_data = game_details[str(game_id)]['data']
            
            # Embed mesajını oluşturuyoruz
            game_info_embed = discord.Embed(
                title=game_data['name'],
                description=game_data['short_description'],
                color=discord.Color.blue()
            )

            # Tür ve fiyat bilgilerini ekliyoruz
            genres = ", ".join(genre['description'] for genre in game_data['genres']) if 'genres' in game_data else "Bilinmiyor"
            price = "Bilinmiyor"
            if 'price_overview' in game_data:
                price = game_data['price_overview']['final_formatted']
            
            game_info_embed.add_field(name="Tür", value=genres, inline=False)
            game_info_embed.add_field(name="Fiyat", value=price, inline=False)

            # Oyuncu sayısı bilgisi için player count'ı kontrol edebiliriz
            player_count = "Bilinmiyor"
            if 'players' in game_data:
                player_count = game_data['players']
            
            game_info_embed.add_field(name="Kaç Kişilik", value=player_count, inline=False)

            # Embed mesajını gönderiyoruz
            await ctx.send(embed=game_info_embed)
        
        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {e}")

async def setup(bot):
    await bot.add_cog(GameInfoCog(bot))