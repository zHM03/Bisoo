import discord
from discord.ext import commands
import aiohttp

UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY"  # Buraya kendi API anahtarınızı ekleyin

class Wallpaper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_image_url = None  # Son gönderilen görseli saklamak için değişken

    @commands.command()
    async def wallpaper(self, ctx, *, query: str = "wallpaper"):
        """Belirtilen kelimeye göre rastgele bir Full HD veya daha yüksek çözünürlükte duvar kağıdı gönderir (tekrarsız)."""
        url = f"https://api.unsplash.com/photos/random?query={query}&orientation=landscape&client_id={UNSPLASH_ACCESS_KEY}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    image_url = data.get("urls", {}).get("raw", "")  # RAW format en yüksek kaliteyi sağlar
                    
                    if image_url and image_url != self.last_image_url:
                        self.last_image_url = image_url  # Yeni görseli kaydet
                        if not image_url.endswith((".jpg", ".png")):
                            image_url += "&fm=jpg&q=100"  # JPG formatında ve maksimum kalitede olsun
                        
                        embed = discord.Embed(title=f"İşte bir {query} duvar kağıdı!", color=discord.Color.blue())
                        embed.set_image(url=image_url)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f"Üzgünüm, '{query}' için yeni bir duvar kağıdı bulamıyorum. 😢 Lütfen tekrar deneyin.")
                else:
                    await ctx.send("API'ye erişirken bir hata oluştu. 😕")

async def setup(bot):
    await bot.add_cog(Wallpaper(bot))
