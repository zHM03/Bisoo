import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os
from youtubesearchpython import VideosSearch  # YouTube'da arama yapmak için

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []  # Şarkı kuyruğu
        self.temp_folder = "temp"  # Geçici dosya klasörü
        os.makedirs(self.temp_folder, exist_ok=True)

    async def after_play(self, ctx):
        """Şarkı bittikten sonra kuyruğu kontrol eder. Eğer şarkı yoksa bot kanaldan ayrılır."""
        if self.song_queue:
            self.song_queue.pop(0)  # Mevcut şarkıyı kaldır
            await self.play_next(ctx)  # Sıradaki şarkıyı çal
        else:
            await asyncio.sleep(3)  # Discord'un işlemesi için küçük bir gecikme
            voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice_client and not voice_client.is_playing():
                await voice_client.disconnect()
                print("✅ Bot kanaldan ayrıldı!")

    async def play_next(self, ctx):
        """Sıradaki şarkıyı oynatır. Kuyruk boşsa botu kanaldan çıkarır."""
        if not self.song_queue:
            voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice_client:
                await asyncio.sleep(3)
                await voice_client.disconnect()
                print("✅ Kuyruk boş, bot kanaldan ayrıldı!")
            return

        url, title = self.song_queue[0]  # İlk şarkıyı al
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if not voice_client:
            voice_client = await ctx.author.voice.channel.connect()

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'compat_opts': 'no-youtube-channel-redirect'  # YouTube yönlendirme hatalarını önler
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = f"{self.temp_folder}/{info['id']}.webm"

        def after_callback(error):
            if error:
                print(f"Şarkı oynatma sırasında hata oluştu: {error}")
            self.bot.loop.create_task(self.after_play(ctx))

            if os.path.exists(file):
                os.remove(file)

        voice_client.play(discord.FFmpegPCMAudio(file), after=after_callback)

        embed = discord.Embed(title="🎵 Şimdi Çalıyor", description=f"**{title}**", color=discord.Color.green())
        embed.add_field(name="Bağlantı", value=url, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def p(self, ctx, url):
        """Şarkıyı veya playlist içindeki şarkıları aratıp çalar."""
        ydl_opts = {'quiet': True}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if info.get('_type') == 'playlist':
                # Playlist içindeki şarkıları bulup kuyruğa ekle
                await ctx.send(f"🎶 Playlist bulundu! **{len(info['entries'])} şarkı ekleniyor...**")
                for entry in info['entries']:
                    song_title = entry.get('title', 'Bilinmeyen Şarkı')
                    song_artist = entry.get('artist', '')  # Bazı şarkılarda sanatçı bilgisi olmayabilir
                    search_query = f"{song_artist} {song_title}" if song_artist else song_title

                    # YouTube'da şarkıyı arayarak ilk sonucu al
                    video_url = await self.search_youtube(search_query)
                    if video_url:
                        await self.add_song_and_play(ctx, video_url, song_title)

                await ctx.send(f"✅ Playlist'teki şarkılar kuyruğa eklendi!")
            else:
                # Tek bir şarkıyı kuyruğa ekle
                title = info.get('title', 'Bilinmeyen Şarkı')
                self.song_queue.append((url, title))

                if not ctx.voice_client or not ctx.voice_client.is_playing():
                    await self.play_next(ctx)

    async def search_youtube(self, query):
        """YouTube'da verilen sorguyu aratır ve ilk videonun URL'sini döndürür."""
        search = VideosSearch(query, limit=1)
        result = await asyncio.to_thread(search.result)
        if result and result['result']:
            return result['result'][0]['link']
        return None

    async def add_song_and_play(self, ctx, song_url, song_title):
        """Şarkıyı kuyruğa ekler ve oynatmaya başlar."""
        self.song_queue.append((song_url, song_title))

        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    @commands.command()
    async def q(self, ctx):
        """Mevcut şarkı kuyruğunu gösterir."""
        await self.send_queue_embed(ctx)

    async def send_queue_embed(self, ctx):
        """Mevcut sırayı embed olarak gösterir."""
        if not self.song_queue:
            await ctx.send("🎵 Şu an çalma listesinde şarkı yok.")
            return

        embed = discord.Embed(title="🎶 Kuyruk 🎶", color=discord.Color.orange())
        for i, (url, title) in enumerate(self.song_queue, 1):
            embed.add_field(name=f"{i}. {title}", value=url, inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Music(bot))
