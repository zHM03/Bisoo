import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Steam API anahtarını almak
STEAM_API_KEY = os.getenv('STEAM_API_KEY')

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Steam ID'yi kullanıcı adından almak için fonksiyon
    def get_steam_id_from_vanity_url(self, vanity_url):
        url = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={STEAM_API_KEY}&vanityurl={vanity_url}"
        response = requests.get(url)
        data = response.json()
        
        if data['response']['success'] == 1:
            return data['response']['steamid']
        else:
            return None  # Geçersiz kullanıcı adı

    # Kullanıcı bilgilerini çekmek için fonksiyon
    def get_steam_user_info(self, steam_id):
        url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={steam_id}"
        response = requests.get(url)
        data = response.json()

        if data['response']['players']:
            player = data['response']['players'][0]
            return player
        else:
            return None

    # Kullanıcının sahip olduğu oyun sayısını almak için fonksiyon
    def get_owned_games_count(self, steam_id):
        url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={STEAM_API_KEY}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true"
        response = requests.get(url)
        data = response.json()
        
        if 'response' in data and 'games' in data['response']:
            return len(data['response']['games'])
        return 0

    # Kullanıcının en çok oynadığı 3 oyunu almak için fonksiyon
    def get_top_played_games(self, steam_id):
        url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={STEAM_API_KEY}&steamid={steam_id}&include_played_free_games=true&include_appinfo=true"
        response = requests.get(url)
        data = response.json()

        if 'response' in data and 'games' in data['response']:
            games = sorted(data['response']['games'], key=lambda x: x.get('playtime_forever', 0), reverse=True)
            top_games = [(game['name'], game['playtime_forever'] // 60) for game in games[:3]]  # En çok oynanan 3 oyun
            return top_games
        return []

    # Kullanıcı profil bilgilerini ve seviyesini çekmek için !profile komutu
    @commands.command()
    async def profile(self, ctx, *, username: str):
        # Kullanıcı adı ile Steam ID'yi alıyoruz
        steam_id = self.get_steam_id_from_vanity_url(username)
        
        if not steam_id:
            await ctx.send(f"{username} adında geçerli bir Steam profili bulamadım.")
            return
        
        # Steam ID ile kullanıcı bilgilerini alıyoruz
        user_info = self.get_steam_user_info(steam_id)
        
        if user_info:
            # Kullanıcının Steam seviyesini alıyoruz
            steam_level = self.get_steam_level(steam_id)

            # Kullanıcının sahip olduğu oyun sayısını alıyoruz
            owned_games_count = self.get_owned_games_count(steam_id)

            # Kullanıcının en çok oynadığı oyunları alıyoruz
            top_games = self.get_top_played_games(steam_id)

            # Embed mesajını oluşturuyoruz
            embed = discord.Embed(
                title=f"{user_info['personaname']}'in Steam Profili", 
                color=discord.Color(0x00BFFF)  # Başlık için renk
            )
            embed.set_thumbnail(url=user_info['avatarfull'])  # Profil fotoğrafını ekliyoruz
            embed.set_image(url=user_info.get('background', ''))  # Arka plan görselini ekliyoruz (varsa)
            embed.add_field(name="Kullanıcı Adı", value=user_info['personaname'], inline=False)
            embed.add_field(name="Steam Seviyesi", value=str(steam_level), inline=False)
            embed.add_field(name="Sahip Olduğu Oyun Sayısı", value=str(owned_games_count), inline=False)
            embed.add_field(name="Profil Linki", value=f"[Steam Profili](https://steamcommunity.com/profiles/{steam_id})", inline=False)

            # En çok oynadığı oyunları ekliyoruz
            if top_games:
                embed.add_field(name="En Çok Oynadığı Oyunlar", value='\n'.join([f"{game[0]}: {game[1]} saat" for game in top_games]), inline=False)

            # Embed mesajını gönderiyoruz
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{username} için Steam bilgilerini alamadım.")

    # Kullanıcı seviyesini almak için fonksiyon
    def get_steam_level(self, steam_id):
        url = f"http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={STEAM_API_KEY}&steamid={steam_id}"
        response = requests.get(url)
        data = response.json()

        if 'response' in data and 'player_level' in data['response']:
            return data['response']['player_level']
        return None

# Botun cog'u ekleyip yüklemek için
async def setup(bot):
    await bot.add_cog(ProfileCog(bot))