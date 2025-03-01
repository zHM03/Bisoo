import discord
import asyncio
from discord.ext import commands, tasks
import time

class EmbedCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_embeds.start()  # Embed kontrolünü başlat
        self.last_request_time = time.time()  # Son istek zamanı

    def cog_unload(self):
        self.check_embeds.cancel()  # Cog'un yüklenmesi kaldırıldığında kontrolü durdur

    @tasks.loop(seconds=5)  # Her 5 saniyede bir çalışacak
    async def check_embeds(self):
        target_channel_id = 1341428278879326298  # Hedef kanal ID'si

        # Hedef kanal
        channel = self.bot.get_channel(target_channel_id)
        if not channel:
            print("Kanal bulunamadı!")
            return

        # Son 100 mesajı kontrol et
        async for message in channel.history(limit=100):
            if message.author == self.bot.user and message.embeds:
                embed_content = message.embeds[0].to_dict()  # Embed içeriğini sözlük formatına çevir

                # Kanaldaki diğer mesajları kontrol et
                async for old_message in channel.history(limit=1000):
                    if old_message.author == self.bot.user and old_message.embeds:
                        old_embed_content = old_message.embeds[0].to_dict()

                        # Eğer embed içerikleri eşleşirse
                        if old_embed_content == embed_content and old_message.id != message.id:
                            try:
                                # Rate-limiting kontrolü
                                wait_time = max(0, 1.5 - (time.time() - self.last_request_time))  # 1.5 saniye bekleme
                                await asyncio.sleep(wait_time)  # Bekleme ekle
                                await message.delete()  # Yeni mesajı sil
                                self.last_request_time = time.time()  # Son istek zamanını güncelle
                                print(f"Yeni embed silindi: {message.id}")
                                break  # Aynı embed bulunduğu anda işlemi sonlandır
                            except discord.errors.Forbidden as e:
                                print(f"Yeni mesaj silinemedi: {message.id}. Hata: {e}")
                            except discord.NotFound as e:
                                print(f"Yeni mesaj bulunamadı: {message.id}. Hata: {e}")
                            return

async def setup(bot):
    await bot.add_cog(EmbedCheck(bot))
