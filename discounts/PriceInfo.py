import discord
from discord.ext import commands
import requests
import logging

class GamePriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = "37d8ca093b6022f360d8e48ce69932797bc3c4e2"
        # API'ye uygun lookup endpoint URL'si
        self.url = "https://api.isthereanydeal.com/lookup/game/title/{}/"  # Game lookup endpoint

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
            'key': self.api_key
        }

        # URL'yi dinamik hale getiriyoruz
        url = self.url.format(game_name)

        try:
            self.logger.debug(f"API'ye istek gönderiliyor: {url}")
            response = requests.get(url, params=params)

            if response.status_code == 200:
                self.logger.debug("API'den başarılı yanıt alındı.")
                data = response.json()

                if 'data' in data and 'price' in data['data']:
                    price = data['data']['price']
                    self.logger.info(f"{game_name} oyununun fiyatı: {price}")
                    await ctx.send(f"{game_name} oyununun fiyatı: {price}")
                    await self.log_to_channel(f"Fiyat sorgulama başarılı: {game_name} - {price}")
                else:
                    self.logger.warning(f"{game_name} oyunu için fiyat bulunamadı.")
                    await ctx.send(f"{game_name} oyunu için fiyat bulunamadı.")
                    await self.log_to_channel(f"{game_name} oyunu için fiyat bulunamadı.")
            else:
                self.logger.error(f"HTTP hatası: {response.status_code}")
                self.logger.error(f"API yanıtı: {response.text}")
                await ctx.send(f"API hatası: {response.status_code}. Detaylar: {response.text}")
                await self.log_to_channel(f"API hatası: {response.status_code} - {game_name}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API isteği sırasında hata oluştu: {e}")
            await ctx.send("API isteği sırasında bir hata oluştu.")
            await self.log_to_channel(f"API isteği sırasında hata oluştu: {e}")

# Cog'u botumuza ekliyoruz
async def setup(bot):
    await bot.add_cog(GamePriceCog(bot))