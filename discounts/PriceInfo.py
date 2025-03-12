import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class PriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.steam_api_key = os.getenv("STEAM_API_KEY")  # .env dosyasındaki Steam API anahtarını al
        self.log_channel_id = 1339957995542544435  # Log mesajlarının gönderileceği kanal ID'si

    async def send_log_message(self, message: str):
        """Log mesajlarını belirli bir kanala gönderir."""
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            # 4000 karakterden fazla ise, mesajı kes
            if len(message) > 4000:
                message = message[:4000]  # 4000 karakteri aşan kısmı kes
            await channel.send(message)
        else:
            print("Log kanalı bulunamadı!")

    @commands.command(name="price")
    async def get_game_price(self, ctx, *, game_name: str):
        # Steam API URL'si (AppList ile oyunları listele)
        steam_api_url = f"http://api.steampowered.com/ISteamApps/GetAppList/v2/"

        # Steam API'den oyun listesi al
        try:
            response = requests.get(steam_api_url)
            if response.status_code != 200:
                await ctx.send(f"Steam API'den veri alınırken bir hata oluştu: {response.status_code}")
                await self.send_log_message(f"Steam API'den veri alınırken hata oluştu: {response.status_code}")
                return

            data = response.json()

            # Oyunun App ID'sini bul
            game_app_id = None
            await self.send_log_message(f"{game_name} oyunu aranmaya başlandı...")
            for game in data['applist']['apps']:
                if game_name.lower() in game['name'].lower():
                    game_app_id = game['appid']
                    await self.send_log_message(f"Oyun bulundu! App ID: {game_app_id}")
                    break

            if not game_app_id:
                await ctx.send(f"{game_name} adlı oyun bulunamadı!")
                await self.send_log_message(f"{game_name} adlı oyun bulunamadı.")
                return

        except Exception as e:
            await ctx.send(f"Steam API'ye bağlanırken bir hata oluştu: {e}")
            await self.send_log_message(f"Steam API bağlanırken hata: {e}")
            return

        # Oyun için fiyat bilgisi almak yerine Steam Store üzerinden fiyat bilgisi al
        store_url = f"https://store.steampowered.com/api/appdetails?appids={game_app_id}"

        await self.send_log_message(f"Steam Store API'ye istek atılıyor: {store_url}")

        try:
            store_response = requests.get(store_url)
            if store_response.status_code != 200:
                await ctx.send(f"Fiyat verileri alınırken bir hata oluştu: {store_response.status_code}")
                await self.send_log_message(f"Fiyat verileri alınırken hata oluştu: {store_response.status_code}")
                return

            store_data = store_response.json()

            # API yanıtını logla
            await self.send_log_message(f"Steam Store API yanıtı: {store_data}")

            if not store_data.get(str(game_app_id), {}).get("success", False):
                await ctx.send(f"{game_name} için fiyat bilgisi alınamadı.")
                await self.send_log_message(f"{game_name} için fiyat bilgisi alınamadı.")
                return

            game_details = store_data[str(game_app_id)]["data"]
            discount_price = game_details.get("price_overview", {}).get("final", None)
            original_price = game_details.get("price_overview", {}).get("initial", None)
            discount_start_time = game_details.get("price_overview", {}).get("discount_percent", 0) > 0

            if discount_price and original_price:
                # Embed mesajı oluştur
                embed = discord.Embed(title=f"{game_name} Fiyat Bilgisi", color=discord.Color.green())
                embed.add_field(name="İndirim Fiyatı", value=f"${discount_price / 100:.2f}", inline=False)
                embed.add_field(name="Orijinal Fiyat", value=f"${original_price / 100:.2f}", inline=False)
                embed.add_field(name="İndirim Durumu", value="İndirimli", inline=False)

                await ctx.send(embed=embed)
                
                # Fiyat bilgisini logla
                await self.send_log_message(f"{game_name} Fiyatı: İndirimli Fiyat: ${discount_price / 100:.2f}, Orijinal Fiyat: ${original_price / 100:.2f}")
            else:
                await ctx.send(f"{game_name} için geçerli bir fiyat bilgisi bulunamadı.")
                await self.send_log_message(f"{game_name} için geçerli bir fiyat bilgisi bulunamadı.")

        except Exception as e:
            await ctx.send(f"Fiyat verilerine bağlanırken bir hata oluştu: {e}")
            await self.send_log_message(f"Fiyat verilerine bağlanırken hata: {e}")
            return

async def setup(bot):
    await bot.add_cog(PriceCog(bot))