import discord
from discord.ext import commands
import requests

class GameInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gameinfo(self, ctx, *, game_name: str):
        try:
            API_KEY = "37d8ca093b6022f360d8e48ce69932797bc3c4e2"
            SEARCH_URL = f"https://api.isthereanydeal.com/v02/game/plain/?key={API_KEY}&title={game_name}"
            
            # Oyunun "plain" ID'sini al
            search_response = requests.get(SEARCH_URL).json()
            
            # API yanıtını hata kanalına gönder
            debug_channel = self.bot.get_channel(1339957995542544435)
            await debug_channel.send(f"API Yanıtı (Search): ```{search_response}```")
            
            if "data" not in search_response or not search_response["data"]:
                await ctx.send("Hmm, bu oyun hakkında bilgi bulamadım. 🙀")
                return
            
            game_plain = search_response["data"]
            
            # Oyun fiyatlarını al
            PRICES_URL = f"https://api.isthereanydeal.com/v01/game/prices/?key={API_KEY}&plains={game_plain}"
            prices_response = requests.get(PRICES_URL).json()
            
            await debug_channel.send(f"API Yanıtı (Prices): ```{prices_response}```")
            
            if "data" not in prices_response or game_plain not in prices_response["data"]:
                await ctx.send("Oyun fiyatı hakkında bilgi alamadım. 😾")
                return
            
            price_data = prices_response["data"][game_plain]["list"]
            
            # En ucuz fiyatı bul
            cheapest = min(price_data, key=lambda x: x["price"])
            cheapest_store = cheapest["shop"]["name"]
            cheapest_price = cheapest["price"]
            cheapest_currency = cheapest["currency"]

            # Oyun resmini al
            INFO_URL = f"https://api.isthereanydeal.com/v01/game/info/?key={API_KEY}&plains={game_plain}"
            info_response = requests.get(INFO_URL).json()
            
            await debug_channel.send(f"API Yanıtı (Info): ```{info_response}```")