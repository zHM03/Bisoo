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
            await channel.send(message)
        else:
            print("Log kanalı bulunamadı!")

    @commands.command(name="price")
    async def get_game_price(self, ctx, *, game_name: str):
        # Steam API URL'si (AppList ile oyunları listele)
        steam_api_url = f"http://api.steampowered.com/ISteamApps/GetAppList/v2/"
        await self.send_log_message(f"Steam API'ye istek atılıyor: {steam_api_url}")

        # Steam API'den oyun listesi al
        try:
            response = requests.get(steam_api_url)
            if response.status_code != 200:
                await ctx.send(f"Steam API'den veri alınırken bir hata oluştu: {response.status_code}")
                await self.send_log_message(f"Steam API'den veri alınırken hata oluştu: {response.status_code}")
                return

            data = response.json()
            await self.send_log_message(f"Steam API yanıtı alındı: {data}")
        except Exception as e:
            await ctx.send(f"Steam API'ye bağlanırken bir hata oluştu: {e}")
            await self.send_log_message(f"Steam API bağlanırken hata: {e}")
            return

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

        # Oyun için fiyat ve indirim bilgilerini al (Steam Store API üzerinden)
        price_url = f"https://api.steampowered.com/ISteamEconomy/GetAssetPrices/v1?appid={game_app_id}&key={self.steam_api_key}"
        await self.send_log_message(f"Fiyat bilgisi almak için Steam API'ye istek atılıyor: {price_url}")

        try:
            price_response = requests.get(price_url)
            if price_response.status_code != 200:
                await ctx.send(f"Fiyat verileri alınırken bir hata oluştu: {price_response.status_code}")
                await self.send_log_message(f"Fiyat verileri alınırken hata oluştu: {price_response.status_code}")
                return

            price_data = price_response.json()
            await self.send_log_message(f"Fiyat API yanıtı alındı: {price_data}")
        except Exception as e:
            await ctx.send(f"Fiyat verilerine bağlanırken bir hata oluştu: {e}")
            await self.send_log_message(f"Fiyat verilerine bağlanırken hata: {e}")
            return

        # Fiyat ve indirim bilgilerini kontrol et
        if "price" not in price_data or "discount" not in price_data:
            await ctx.send(f"{game_name} için fiyat bilgisi alınamadı.")
            await self.send_log_message(f"{game_name} için fiyat bilgisi alınamadı.")
            return

        # En son indirim ve fiyat bilgilerini al
        discount_price = price_data['discount']['final_price']
        original_price = price_data['price']['original_price']
        discount_start_time = price_data['discount']['start_time']
        discount_end_time = price_data['discount']['end_time']

        # Embed mesajı oluştur
        embed = discord.Embed(title=f"{game_name} Fiyat Bilgisi", color=discord.Color.green())
        embed.add_field(name="İndirim Fiyatı", value=f"${discount_price / 100:.2f}", inline=False)
        embed.add_field(name="Orijinal Fiyat", value=f"${original_price / 100:.2f}", inline=False)
        embed.add_field(name="İndirim Başlangıcı", value=f"<t:{discount_start_time}:F>", inline=False)
        embed.add_field(name="İndirim Bitişi", value=f"<t:{discount_end_time}:F>", inline=False)

        await ctx.send(embed=embed)

        # Fiyat bilgisini logla
        await self.send_log_message(f"{game_name} Fiyatı: İndirimli Fiyat: ${discount_price / 100:.2f}, Orijinal Fiyat: ${original_price / 100:.2f}")

async def setup(bot):
    await bot.add_cog(PriceCog(bot))