import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from pytube import Playlist
import re
import traceback

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.playing = False
        self.voice_client = None
        self.error_channel_id = 1339957995542544435  # Hata mesajlarını göndereceğimiz kanal ID'si

    async def send_log_message(self, message):
        """Hata veya log mesajlarını belirtilen kanala gönderir."""
        channel = self.bot.get_channel(self.error_channel_id)
        if channel:
            await channel.send(message)
        else:
            print(f"Log mesajı gönderilemedi, kanal bulunamadı: {self.error_channel_id}")

    async def get_video_urls(self, playlist_url):
        """Bir YouTube oynatma listesindeki tüm video URL'lerini döndürür."""
        try:
            playlist = Playlist(playlist_url)
            video_urls = playlist.video_urls
            await self.send_log_message(f"Playlist alındı: {playlist_url}")
            return video_urls
        except Exception as e:
            await self.send_log_message(f"Playlist alınırken hata oluştu: {str(e)}\n\n{traceback.format_exc()}")
            return []

    async def is_playlist(self, url):
        """URL'nin bir oynatma listesi olup olmadığını kontrol eder."""
        try:
            return 'list=' in url
        except Exception as e:
            await self.send_log_message(f"URL kontrolü sırasında hata oluştu: {str(e)}\n\n{traceback.format_exc()}")
            return False

    async def download_audio(self, url, filename):
        """Verilen URL'den sesi indirir ve belirtilen dosya adına kaydeder."""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': filename,
                'quiet': True,
                'ignoreerrors': True,
                'geo-bypass': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            await self.send_log_message(f"İndirme tamamlandı: {url}")
        except Exception as e:
            await self.send_log_message(f"Download sırasında hata oluştu: {str(e)}\n\n{traceback.format_exc()}")

    async def play_next(self, ctx):
        """Bir sonraki şarkıyı oynatır, sıra boşsa ses kanalından çıkar."""
        try:
            if self.queue.empty():
                self.playing = False
                await self.voice_client.disconnect()
                await self.send_log_message("Kuyruk boş, sesli kanaldan çıkıldı.")
                return

            url = await self.queue.get()
            await self.send_log_message(f"Şarkı çalınmaya başlandı: {url}")

            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temps')
            os.makedirs(temp_dir, exist_ok=True)

            song_filename = re.sub(r'\W+', '', url)
            filename = os.path.join(temp_dir, f"{song_filename}.mp3")

            if not os.path.exists(filename):
                await self.download_audio(url, filename)

            if self.voice_client is None or not self.voice_client.is_connected():
                self.voice_client = await ctx.author.voice.channel.connect()

            audio_source = discord.FFmpegPCMAudio(filename)
            self.voice_client.play(audio_source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))

            await ctx.send(f"🎵 **Çalıyor:** {url}")

        except Exception as e:
            await self.send_log_message(f"Beklenmedik bir hata oluştu (play_next): {str(e)}\n\n{traceback.format_exc()}")

    @commands.command(name="p")
    async def play(self, ctx, url):
        """Bir şarkıyı veya oynatma listesini kuyruğa ekler ve çalar."""
        try:
            if not ctx.author.voice:
                await ctx.send("Bir ses kanalında olmalısınız!")
                return

            if not self.voice_client or not self.voice_client.is_connected():
                self.voice_client = await ctx.author.voice.channel.connect()

            if await self.is_playlist(url):
                video_urls = await self.get_video_urls(url)  # ✅ HATA DÜZELTİLDİ
                for video_url in video_urls:
                    await self.queue.put(video_url)
            else:
                await self.queue.put(url)

            if not self.playing:
                self.playing = True
                await self.play_next(ctx)

        except Exception as e:
            await self.send_log_message(f"Beklenmedik bir hata oluştu (play komutu): {str(e)}\n\n{traceback.format_exc()}")

async def setup(bot):
    """Müzik cog'unu bota ekler."""
    try:
        await bot.add_cog(Music(bot))
        print("Music cog başarıyla yüklendi.")
    except Exception as e:
        print(f"Cog yüklenirken hata oluştu: {e}")