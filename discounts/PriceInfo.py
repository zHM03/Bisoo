import discord
from discord.ext import commands
import requests

class GameInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = "37d8ca093b6022f360d8e48ce69932797bc3c4e2"
        self.debug_channel_id = 1339957995542544435  # Hataları göndereceği kanal

    @commands.command()
    async def gameinfo(self, ctx, *, game_name: str):
        try:
            debug_channel = self.bot.get_channel(self.debug_channel_id)

            # Oyunun "plain" ID'sini al
            search_url = f"https://api.isthereanydeal.com/v02/game/plain/?key={self.api_key}&title={game_name}"
            search_response = requests.get(search_url).json()

            await debug_channel.send(f"API Yanıtı (Search): ```{search_response}```")

            if "data" not in search_response or not search_response["data"]:
                await ctx.send("Hmm, bu oyun hakkında bilgi bulamadım. 🙀")
                return

            game_plain = search_response["data"]

            # Oyun fiyatlarını al
            prices_url = f"https://api.isthereanydeal.com/v01/game/prices/?key={self.api_key}&plains={game_plain}"
            prices_response = requests.get(prices_url).json()

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
            info_url = f"https://api.isthereanydeal.com/v01/game/info/?key={self.api_key}&plains={game_plain}"
            info_response = requests.get(info_url).json()

            await debug_channel.send(f"API Yanıtı (Info): ```{info_response}```")

            game_image = info_response["data"].get(game_plain, {}).get("image", None)

            # Embed mesajı oluştur
            embed = discord.Embed(
                title=f"Meow! **{game_name}** oyununu buldum! 🐾",
                description="Hadi bakalım, işte oyunla ilgili bilgiler! 😸",
                color=discord.Color.purple()
            )

            if game_image:
                embed.set_image(url=game_image)

            embed.add_field(name="💰 En Ucuz Fiyat", value=f"{cheapest_price} {cheapest_currency} ({cheapest_store})", inline=False)
            embed.set_footer(text="Kedi Robot'tan sevgilerle! 😽")

            await ctx.send(embed=embed)

        except Exception as e:
            error_message = f"Hata: {str(e)}"
            await debug_channel.send(error_message)
            await ctx.send("Bir şeyler ters gitti, yetkililere bildirildi. 😿")

# Cog'u bot'a ekleme
async def setup(bot):
    await bot.add_cog(GameInfo(bot))