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

    async def check_cookies_file(self, ctx):
        """cookies.txt dosyasının varlığını kontrol eder"""
        if not os.path.exists("cookies.txt"):
            embed = discord.Embed(
                title="⚠️ Uyarı ⚠️",
                description="cookies.txt dosyası bulunamadı! Lütfen dosyanın mevcut olduğundan emin olun.",
                color=discord.Color.red()
            )
            channel = self.bot.get_channel(123456789012345678)  # Buraya ilgili kanalın ID'sini koy
            if channel:
                await channel.send(embed=embed)

    async def cog_load(self):
        """Bot başlatıldığında cookies.txt dosyasını kontrol eder"""
        await self.check_cookies_file()

    def get_video_urls(self, playlist_url):
        """Playlist URL'sinden video URL'lerini al"""
        playlist = Playlist(playlist_url)
        return playlist.video_urls

    def is_playlist(self, url):
        """Playlist URL'sinin olup olmadığını kontrol et"""
        playlist_pattern = r'list='
        return bool(re.search(playlist_pattern, url))

    async def download_audio(self, url, filename):
        """Verilen URL'den ses dosyasını indir"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'quiet': False,
            'ignoreerrors': True,
            'geo-bypass': True,
            'cookiefile': "cookies.txt"  # Cookies dosyasını kullan
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
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        song_filename = re.sub(r'\W+', '', url)
        filename = os.path.join(temp_dir, f"{song_filename}.mp3")

        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)
                song_title = info_dict.get('title', 'Bilinmeyen Şarkı')
                thumbnail_url = info_dict.get('thumbnail', '')
            except yt_dlp.utils.DownloadError as e:
                print(f"Hata: {e}")

                embed = discord.Embed(
                    title="❌ Hata ❌",
                    description=f"**{url}** \nBu şarkıyı çalamıyorum, bir sonrakine geçiyorum.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return await self.play_next(ctx)

        if not os.path.exists(filename):
            await self.download_audio(url, filename)

        audio_source = discord.FFmpegPCMAudio(filename)
        self.voice_client.play(audio_source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))

        embed = discord.Embed(
            title="🎶 Şu an çalıyor 🎶",
            description=f"**{song_title}**",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Şarkıcı: BISOOO🐱")
        embed.set_image(url=thumbnail_url)

        await ctx.send(embed=embed)

        if not self.queue.empty():
            next_url = self.queue._queue[0]  
            next_song_filename = re.sub(r'\W+', '', next_url)  
            next_filename = os.path.join(temp_dir, f"{next_song_filename}.mp3")

            if not os.path.exists(next_filename):
                self.bot.loop.create_task(self.download_audio(next_url, next_filename))

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
            await ctx.send("Bot ses kanalından ayrıldı ve işlem sıfırlandı.")

async def setup(bot):
    await bot.add_cog(Music(bot))
