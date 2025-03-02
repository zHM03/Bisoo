import discord
from discord.ext import commands
import requests

class GameInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gameinfo(self, ctx, *, game_name: str):
        try:
            # CheapShark API üzerinden oyun araması
            CHEAPSHARK_API_URL = 'https://www.cheapshark.com/api/1.0'
            search_url = f"{CHEAPSHARK_API_URL}/search?title={game_name}&limit=5"
            search_response = requests.get(search_url)

            # Yanıtı kontrol et
            print(search_response.text)  # Yanıtın içeriğini görmek için ekliyoruz.

            search_data = search_response.json()

            if not search_data:
                await ctx.send("Hmm, bu oyun hakkında bilgi bulamadım. 🙀")
                return

            # Oyun bilgilerini ve fiyatları almak
            game_info = search_data[0]
            game_title = game_info['title']
            steam_id = game_info['steamAppID']
            price = float(game_info['price'])

            # Steam fiyatlarını almak
            steam_url = f"{CHEAPSHARK_API_URL}/discounts?steamAppID={steam_id}"
            steam_response = requests.get(steam_url)

            # Yanıtı kontrol et
            print(steam_response.text)  # Yanıtın içeriğini görmek için ekliyoruz.

            steam_data = steam_response.json()

            if not steam_data:
                await ctx.send("Oyun fiyatı hakkında bilgi alamadım. 😾")
                return

            # Oyun resmi almak için Steam API'sinden kullanabiliriz
            game_image_url = f"https://cdn.akamai.steamstatic.com/steam/apps/{steam_id}/header.jpg"  # Steam oyun resmi

            # Embed mesajı oluşturma
            embed = discord.Embed(
                title=f"Meow! **{game_title}** oyununu buldum! 🐾",
                description="Hadi bakalım, işte oyunla ilgili bilgiler! 😸",
                color=discord.Color.purple()
            )
            embed.set_image(url=game_image_url)  # Oyun resmini ekliyoruz
            embed.set_footer(text="Kedi Robot'tan sevgilerle! 😽")

            # Fiyat bilgilerini embed'e ekle
            embed.add_field(name="Steam Fiyatı", value=f"${price:.2f}", inline=False)

            # En ucuz platformu ekleyin
            cheapest_platform = steam_data[0]['storeID']
            embed.add_field(name="En Ucuz Platform", value=f"{cheapest_platform} purrfect!", inline=False)

            # Embed mesajını gönder
            await ctx.send(embed=embed)

        except Exception as e:
            # Hata mesajını belirli bir kanala gönder
            channel = self.bot.get_channel(1339957995542544435)  # Hata mesajlarını göndereceğiniz kanal ID'si
            error_message = f"Hata: {str(e)}"
            await channel.send(error_message)
            await ctx.send("Bir şeyler ters gitti, yetkililere bildirildi. 😿")

# Cog'u bot'a async olarak eklemek
async def setup(bot):
    await bot.add_cog(GameInfo(bot))