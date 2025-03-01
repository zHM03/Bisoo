import discord
from discord.ext import commands
import os
import asyncio

class VoiceCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_task = self.bot.loop.create_task(self.check_voice_status())

    async def check_voice_status(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            # Bot herhangi bir sesli kanalda mı?
            bot_in_voice = any(self.bot.user in vc.members for guild in self.bot.guilds for vc in guild.voice_channels)

            if not bot_in_voice:
                self.delete_temp_files()

            await asyncio.sleep(5)  # 30 saniyede bir kontrol et

    def delete_temp_files(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(current_directory, 'temps')

        if not os.path.exists(temp_dir):
            print(f"HATA: 'temps' klasörü bulunamadı! ({temp_dir})")
            return  # Eğer klasör yoksa işlemi bitir

        deleted = False
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
# Cog'u bot'a ekleme
async def setup(bot):
    await bot.add_cog(VoiceCheck(bot))
