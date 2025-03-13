import discord
from discord.ext import commands
import requests
import logging

class GamePriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = "37d8ca093b6022f360d8e48ce69932797bc3c4e2"
        self.url = "https://api.example.com/game-price"  # API URL'sini burada değiştirebilirsiniz

        # Loglama konfigürasyonu
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.log_channel_id = 1339957995542544435  # Logların gönderileceği kanal ID'si

    async def log_to_channel(self, message):
        """Log mesajlarını belirlenen kanala gönderir."""
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            await channel.send(message)
        else:
            self.logger.error("Log kanalına gönderilemiyor!")

    @commands.command()
    async def gamefiyat(self, ctx, *, game_name: str):
        """Oyun adı ile fiyat sorgulama"""

        self.logger.info(f"{ctx.author} tarafından '{game_name}' oyununun fiyatı sorgulandı.")
        
        params = {
            'api_key': self.api_key,
            'game_name': game_name
        }

        try:
            self.logger.debug("API'ye istek gönderiliyor...")
            response = requests.get(self.url, params=params)

            if response.status_code == 200:
                self.logger.debug("API'den başarılı yanıt alındı.")
                data = response.json()
                
                if 'price' in data:
                    price = data['price']
                    self.logger.info(f"{game_name} oyununun fiyatı: {price}")
                    await ctx.send(f"{game_name} oyununun fiyatı: {price}")
                    await self.log_to_channel(f"Fiyat sorgulama başarılı: {game_name} - {price}")
                else:
                    self.logger.warning(f"{game_name} oyunu için fiyat bulunamadı.")
                    await ctx.send(f"{game_name} oyunu için fiyat bulunamadı.")
                    await self.log_to_channel(f"{game_name} oyunu için fiyat bulunamadı.")
            else:
                self.logger.error(f"API hatası: {response.status_code}")
                await ctx.send(f"API hatası: {response.status_code}")
                await self.log_to_channel(f"API hatası: {response.status_code} - {game_name}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API isteği sırasında hata oluştu: {e}")
            await ctx.send("API isteği sırasında bir hata oluştu.")
            await self.log_to_channel(f"API isteği sırasında hata oluştu: {e}")

# Cog'u botumuza ekliyoruz
async def setup(bot):
    await bot.add_cog(GamePriceCog(bot))