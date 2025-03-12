import discord
from discord.ext import commands
import requests

class PriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1339957995542544435  # Log mesajlarının gönderileceği kanal ID'si

    async def send_log_message(self, message: str):
        """Belirtilen log kanalına mesaj gönderir."""
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            await channel.send(f"📜 **Log Mesajı:**\n```{message}```")
        else:
            print("Log kanalı bulunamadı!")

    @commands.command(name="price")
    async def get_game_price(self, ctx, *, game_name: str):
        """Kullanıcıdan gelen oyun ismini CheapShark API ile arar ve fiyat bilgisini getirir."""
        
        log_message = f"📢 **{game_name}** için fiyat bilgisi sorgulanıyor..."
        await self.send_log_message(log_message)

        api_url = f"https://api.cheapshark.com/api/1.0/games?title={game_name}"
        await self.send_log_message(f"🌐 CheapShark API'ye istek atılıyor: {api_url}")

        try:
            response = requests.get(api_url, timeout=10)
            await self.send_log_message(f"🔄 CheapShark API yanıtı alındı, HTTP Kodu: {response.status_code}")

            if response.status_code != 200:
                await self.send_log_message(f"⚠️ Hata: API başarısız döndü, HTTP {response.status_code}")
                await ctx.send(f"CheapShark API'ye bağlanırken hata oluştu! (Kod: {response.status_code})")
                return

            data = response.json()
            await self.send_log_message(f"📦 CheapShark API JSON Yanıtı:\n{data}")

            if not data:
                await self.send_log_message(f"⚠️ API yanıtı boş geldi, oyun bulunamadı.")
                await ctx.send(f"⚠️ {game_name} için fiyat bilgisi bulunamadı!")
                return

            # İlk uygun oyunu seç
            game = data[0]  
            game_id = game["gameID"]
            title = game["external"]

            await self.send_log_message(f"🎮 Oyun bulundu! Game ID: {game_id}, Adı: {title}")

            # Fiyat bilgisi çekmek için yeni API isteği
            deal_url = f"https://api.cheapshark.com/api/1.0/deals?storeID=1&title={game_name}"
            await self.send_log_message(f"💰 Fiyat bilgisi için API'ye istek atılıyor: {deal_url}")

            deal_response = requests.get(deal_url, timeout=10)
            await self.send_log_message(f"🔄 Fiyat API yanıtı alındı, HTTP Kodu: {deal_response.status_code}")

            if deal_response.status_code != 200:
                await self.send_log_message(f"⚠️ Hata: Fiyat API başarısız döndü, HTTP {deal_response.status_code}")
                await ctx.send(f"⚠️ {game_name} için fiyat bilgisi alınamadı!")
                return

            deal_data = deal_response.json()

            if not deal_data:
                await self.send_log_message(f"⚠️ Fiyat bilgisi bulunamadı.")
                await ctx.send(f"⚠️ {game_name} için fiyat bilgisi bulunamadı!")
                return

            deal = deal_data[0]
            current_price = deal["salePrice"]
            original_price = deal["normalPrice"]

            # Embed mesaj oluştur
            embed = discord.Embed(title=f"{title} Fiyat Bilgisi", color=discord.Color.green())
            embed.add_field(name="💲 Şu anki Fiyat", value=f"${current_price}", inline=True)
            embed.add_field(name="💰 Orijinal Fiyat", value=f"${original_price}", inline=True)
            embed.set_footer(text="Fiyatlar CheapShark API'den alınmıştır.")

            await ctx.send(embed=embed)
            await self.send_log_message(f"✅ {title} fiyat bilgisi başarıyla gönderildi!")

        except requests.exceptions.RequestException as e:
            error_msg = f"⚠️ Hata: API isteğinde bir hata oluştu: {str(e)}"
            await self.send_log_message(error_msg)
            await ctx.send("⚠️ Fiyat bilgisi alınırken bir hata oluştu!")

async def setup(bot):
    await bot.add_cog(PriceCog(bot))