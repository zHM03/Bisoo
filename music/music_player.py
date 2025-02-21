import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []  # Şarkı kuyruğu listesi

    async def after_play(self, ctx):
        """Sıradaki şarkıyı başlatır veya botu kanaldan çıkarır."""
        if self.song_queue:
            self.song_queue.pop(0)  # Çalan şarkıyı kuyruğundan çıkar
            await self.play_next(ctx)
        else:
            voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice_client:
                # Eğer ses client'ı varsa, ses kanalından çık
                await voice_client.disconnect()
                print(f"Bot {ctx.guild.name} kanalından çıktı.")  # Kontrol amacıyla çıktı mesajı
            self.song_queue = []  # Kuyruğu sıfırla

    async def play_next(self, ctx):
        """Sıradaki şarkıyı oynatır."""
        if not self.song_queue:
            return  # Liste boşsa bir şey yapma

        url, title = self.song_queue[0]  # İlk şarkıyı al
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if not voice_client:
            voice_client = await ctx.author.voice.channel.connect()

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'noplaylist': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = f"downloads/{info['id']}.webm"

        def after_callback(e):
            asyncio.run_coroutine_threadsafe(self.after_play(ctx), self.bot.loop)

        voice_client.play(discord.FFmpegPCMAudio(file), after=after_callback)

        # Embed mesajı ile güncellenmiş listeyi göster
        await self.send_queue_embed(ctx)

        # Şarkı bitene kadar bekle
        while voice_client.is_playing() or voice_client.is_paused():
            await asyncio.sleep(1)

        # Şarkı bitince dosyayı sil
        if os.path.exists(file):
            os.remove(file)

    @commands.command()
    async def p(self, ctx, url):
        """Şarkıyı kuyruğa ekler ve embed ile gösterir."""
        ydl_opts = {'quiet': True}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Bilinmeyen Şarkı')

        self.song_queue.append((url, title))  # (URL, Şarkı adı)

        # Eğer bot şu an çalmıyorsa sıradaki şarkıyı başlat
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await self.play_next(ctx)
        else:
            await self.send_queue_embed(ctx)

    @commands.command()
    async def queue(self, ctx):
        """Mevcut şarkı kuyruğunu gösterir."""
        await self.send_queue_embed(ctx)

    async def send_queue_embed(self, ctx):
        """Embed mesaj olarak mevcut sırayı gösterir."""
        if not self.song_queue:
            await ctx.send("🎵 Şu an çalma listesinde şarkı yok.")
            return

        embed = discord.Embed(title="🎶 Şarkı Kuyruğu", color=discord.Color.orange())
        for i, (url, title) in enumerate(self.song_queue, 1):
            embed.add_field(name=f"{i}. {title}", value=url, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))
