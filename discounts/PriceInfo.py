import discord
from discord.ext import commands
import requests

class PriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1339957995542544435  # Log mesajlarının gönderileceği kanal ID'si

    async def send_log_message(self, message: str):
        """Log kanalına mesaj gönderir."""
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            await channel.send(f"📜 **Log Mesajı:**\n```{message}```")
        else:
            print("Log kanalı bulunamadı!")

    @commands.command(name="price")
    async def get_game_price(self, ctx, *, game_name: str):
        """Kullanıcıdan gelen oyun ismini CheapShark API ile arar ve fiyat bilgisini getirir."""
        
        log_message = f"📢 **{game_name}** için fiyat bilgisi sorgulanıyor...\n"
        await self.send_log_message(log_message)
        
        url = f"https://api.cheapshark.com/api/1.0/games?title={game_name}"
        response = requests.get(url)
        
        if response.status_code != 200:
            error_msg = f"🚨 CheapShark API'ye istek başarısız! Hata kodu: {response.status_code}"
            await ctx.send(error_msg)
            await self.send_log_message(error_msg)
            return

        data = response.json()

        # Eğer API'den boş veri dönerse
        if not data:
            not_found_msg = f"⚠️ **{game_name}** adlı oyun bulunamadı!"
            await ctx.send(not_found_msg)
            await self.send_log_message(not_found_msg)
            return
        
        # İlk bulunan oyunu alalım
        game_info = data[0]
        game_id = game_info.get("gameID", "Bilinmiyor")
        cheapest_deal_id = game_info.get("cheapestDealID", "Bilinmiyor")
        
        # En ucuz fiyatı almak için API isteği yapalım
        deal_url = f"https://api.cheapshark.com/api/1.0/deals?id={cheapest_deal_id}"
        deal_response = requests.get(deal_url)
        
        if deal_response.status_code != 200:
            error_msg = f"🚨 Deal API'ye istek başarısız! Hata kodu: {deal_response.status_code}"
            await ctx.send(error_msg)
            await self.send_log_message(error_msg)
            return

        deal_data = deal_response.json()

        # Fiyat bilgilerini alalım
        cheapest_price = deal_data.get("gameInfo", {}).get("salePrice", "Bilinmiyor")
        retail_price = deal_data.get("gameInfo", {}).get("retailPrice", "Bilinmiyor")
        store_id = deal_data.get("gameInfo", {}).get("storeID", "Bilinmiyor")

        # Detaylı log mesajı oluştur
        log_message = (
            f"✅ **{game_name}** için fiyat bilgisi bulundu!\n"
            f"🔹 Game ID: {game_id}\n"
            f"🔹 Cheapest Deal ID: {cheapest_deal_id}\n"
            f"🔹 Satış Fiyatı: ${cheapest_price}\n"
            f"🔹 Orijinal Fiyat: ${retail_price}\n"
            f"🔹 Store ID: {store_id}"
        )
        await self.send_log_message(log_message)

        # Embed mesajı oluştur
        embed = discord.Embed(title=f"{game_name} Fiyat Bilgisi", color=discord.Color.green())
        embed.add_field(name="İndirimli Fiyat", value=f"${cheapest_price}", inline=False)
        embed.add_field(name="Orijinal Fiyat", value=f"${retail_price}", inline=False)
        embed.add_field(name="Store ID", value=f"{store_id}", inline=False)

        # Cevabı kullanıcıya gönder
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PriceCog(bot))