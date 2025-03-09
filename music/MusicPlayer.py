import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from pytube import Playlist
import re

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.playing = False
        self.voice_client = None
        self.channel_id = 1339957995542544435  # Hata mesajlarının gönderileceği kanal

    def get_video_urls(self, playlist_url):
        """Playlist URL'sinden video URL'lerini al"""
        playlist = Playlist(playlist_url)
        return playlist.video_urls

    def is_playlist(self, url):
        """Playlist URL'si olup olmadığını kontrol et"""
        return 'list=' in url

    async def check_cookies_file(self):
        """cookies.txt dosyasının olup olmadığını kontrol et"""
        if not os.path.exists("cookies.txt"):
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                await channel.send("⚠️ **Hata:** `cookies.txt` dosyası bulunamadı! Lütfen ilgili dosyayı ekleyin.")

    async def download_audio(self, url, filename):
        """Verilen URL'den ses dosyasını indir"""
        await self.check_cookies_file()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'quiet': False,
            'ignoreerrors': True,
            'geo-bypass': True,
        }
        
        print(f"{url} - İndirilmeye başlandı")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    async def play_next(self, ctx):
        if self.queue.empty():
            self.playing = False
            if self.voice_client:
                await self.voice_client.disconnect()
            return

        url = await self.queue.get()

        if self.voice_client is None or not self.voice_client.is_connected():
            self.voice_client = await ctx.author.voice.channel.connect()

        current_directory = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(current_directory, 'temps')
        os.makedirs(temp_dir, exist_ok=True)

        song_filename = re.sub(r'\W+', '', url)
        filename = os.path.join(temp_dir, f"{song_filename}.mp3")

        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)
                song_title = info_dict.get('title', 'Bilinmeyen Şarkı')
                thumbnail_url = info_dict.get('thumbnail', '')
            except yt_dlp.utils.DownloadError:
                await ctx.send("Bu şarkıyı çalamıyorum, bir sonraki şarkıya geçiyorum.")
                return await self.play_next(ctx)

        if not os.path.exists(filename):
            await self.download_audio(url, filename)

        audio_source = discord.FFmpegPCMAudio(filename)
        self.voice_client.play(audio_source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))

        embed = discord.Embed(title="🎶 Oynatılıyor", description=f"**{song_title}**", color=discord.Color.blue())
        embed.set_image(url=thumbnail_url)
        await ctx.send(embed=embed)

    @commands.command(name="p")
    async def play(self, ctx, playlist_url):
        """Playlist veya video URL'si ile müzik çalmaya başla"""
        if not ctx.author.voice:
            await ctx.send("Bir ses kanalında olmalısınız!")
            return

        if self.voice_client is None or not self.voice_client.is_connected():
            self.voice_client = await ctx.author.voice.channel.connect()

        if self.is_playlist(playlist_url):
            video_urls = self.get_video_urls(playlist_url)
            for url in video_urls:
                await self.queue.put(url)
        else:
            await self.queue.put(playlist_url)

        if not self.playing:
            self.playing = True
            await self.play_next(ctx)

    @commands.command(name="l")
    async def leave(self, ctx):
        """Bot ses kanalından ayrılır"""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            self.playing = False
            self.queue = asyncio.Queue()
            await ctx.send("Bot ses kanalından ayrıldı.")

async def setup(bot):
    await bot.add_cog(Music(bot))
