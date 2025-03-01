import discord
from discord.ext import commands, tasks
import asyncio
from discord.errors import HTTPException

class MessageCleaner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.delete_messages.start()

    @tasks.loop(hours=24)
    async def delete_messages(self):
        channel = self.bot.get_channel(1276852302388400200)  # Mesajları silmek istediğiniz kanalın ID'sini buraya ekleyin.
        if channel:
            async for message in channel.history(limit=30):  # Silinecek mesaj sayısını azaltarak rate limit'i azaltıyoruz
                if not message.pinned:  # Sabitlenmiş mesajları atlar
                    try:
                        await message.delete()
                        await asyncio.sleep(1)  # Her mesajı silmeden önce 1 saniye bekle
                    except HTTPException as e:
                        if e.status == 429:  # Eğer rate limit hatası alırsak
                            retry_after = float(e.response.headers.get('Retry-After', 5))  # Retry-After başlığından süreyi al
                            print(f"Rate limit! Yeniden denemek için {retry_after} saniye bekleniyor.")
                            await asyncio.sleep(retry_after)  # Rate limit süresi kadar bekle
                        else:
                            print(f"Mesaj silinirken bir hata oluştu: {e}")

    @delete_messages.before_loop
    async def before_delete_messages(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(MessageCleaner(bot))
