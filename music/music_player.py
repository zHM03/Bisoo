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

    def get_video_urls(self, playlist_url):
        # Playlist URL'sinden video URL'lerini al
        playlist = Playlist(playlist_url)
        video_urls = playlist.video_urls
        return video_urls

    def is_playlist(self, url):
        # Playlist URL'sinin olup olmadığını kontrol et
        playlist_pattern = r'list='  # Playlist URL'lerini tanımlayacak basit bir regex
        return bool(re.search(playlist_pattern, url))

    async def download_audio(self, url, filename):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'quiet': True
        }

        print(f"İndirilen dosya yolu: {filename}")  # Şarkının indirileceği yolu yazdır

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    async def play_next(self, ctx):
        if self.queue.empty():
            self.playing = False
            await self.voice_client.disconnect()
            return
        
        url = await self.queue.get()

        # Music modülünün bulunduğu klasörü al
        current_directory = os.path.dirname(os.path.abspath(__file__))
        
        # temps klasörünü oluştur
        temp_dir = os.path.join(current_directory, 'temps')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Şarkı dosyasını kaydetmek için sayaç kullan
        song_count = len(os.listdir(temp_dir)) + 1  # Zaten mevcut dosya sayısını al ve 1 ekle
        filename = os.path.join(temp_dir, f"song {song_count}.mp3")

        await self.download_audio(url, filename)

        # Bağlantıyı kontrol et
        if self.voice_client is None or not self.voice_client.is_connected():
            self.voice_client = await ctx.author.voice.channel.connect()

        # Sesli kanala çalmak için ses kaynağını kullan
        audio_source = discord.FFmpegPCMAudio(filename)
        self.voice_client.play(audio_source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))

        await ctx.send(f"Çalıyor: {url}")

        # Oynatma tamamlandığında dosyayı silmek için belirli bir süre bekle
        await asyncio.sleep(60)  # Oynatma işleminin bitmesi için 3 saniye bekle, gerekirse artırabilirsin
        os.remove(filename)  # Şarkıyı oynattıktan sonra dosyayı sil

    @commands.command(name="p")
    async def play(self, ctx, playlist_url):
        if not ctx.author.voice:
            await ctx.send("Bir ses kanalında olmalısınız!")
            return

        if not self.voice_client or not self.voice_client.is_connected():
            self.voice_client = await ctx.author.voice.channel.connect()

        if self.is_playlist(playlist_url):
            # Playlist URL'si olduğunda pytube ile video URL'lerini al
            video_urls = self.get_video_urls(playlist_url)
            for url in video_urls:
                await self.queue.put(url)
        else:
            # Tekil video URL'si olduğunda direkt olarak URL'yi kuyruğa ekle
            await self.queue.put(playlist_url)

        if not self.playing:
            self.playing = True
            await self.play_next(ctx)

async def setup(bot):
    await bot.add_cog(Music(bot))
