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

    # !profile komutunu tanımlıyoruz
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
            # Embed mesajını oluşturuyoruz
            embed = discord.Embed(title=f"{user_info['personaname']}'in Steam Profili", color=discord.Color.blue())
            embed.set_thumbnail(url=user_info['avatarfull'])
            embed.add_field(name="Kullanıcı Adı", value=user_info['personaname'], inline=False)
            embed.add_field(name="Profil Linki", value=f"[Steam Profili](https://steamcommunity.com/profiles/{steam_id})", inline=False)
            embed.add_field(name="Son Görülme", value=user_info['lastlogoff'], inline=False)
            embed.add_field(name="Profil Durumu", value=user_info['profileurl'], inline=False)

            # Embed mesajını gönderiyoruz
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{username} için Steam bilgilerini alamadım.")

# Botun cog'u ekleyip yüklemek için
async def setup(bot):
    await bot.add_cog(ProfileCog(bot))