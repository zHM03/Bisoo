import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from pytube import Playlist
import re
import traceback  # Yığın izleme için

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.playing = False
        self.voice_client = None
        self.error_channel_id = 1339957995542544435  # Hata mesajlarını göndereceğimiz kanal ID'si

    async def send_log_message(self, message):
        # Log mesajlarını belirtilen kanala gönder
        channel = self.bot.get_channel(self.error_channel_id)
        if channel:
            await channel.send(message)
        else:
            print(f"Log mesajı gönderilemedi, kanal bulunamadı: {self.error_channel_id}")

    async def get_video_urls(self, playlist_url):
        try:
            playlist = Playlist(playlist_url)
            video_urls = playlist.video_urls
            await self.send_log_message(f"Playlist alındı: {playlist_url}")
            return video_urls
        except Exception as e:
            error_message = f"Playlist URL'si işlenirken hata oluştu: {str(e)}"
            traceback_message = traceback.format_exc()
            await self.send_log_message(f"{error_message}\n\nYığın İzleme:\n{traceback_message}")
            raise

    def is_playlist(self, url):
        try:
            playlist_pattern = r'list='  # Playlist URL'lerini tanımlayacak basit bir regex
            is_playlist = bool(re.search(playlist_pattern, url))
            await self.send_log_message(f"URL kontrol edildi: {url}, Playlist: {is_playlist}")
            return is_playlist
        except Exception as e:
            error_message = f"URL kontrolü sırasında hata oluştu: {str(e)}"
            traceback_message = traceback.format_exc()
            await self.send_log_message(f"{error_message}\n\nYığın İzleme:\n{traceback_message}")
            raise

    async def download_audio(self, url, filename):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',        # En iyi ses formatını seç
                'outtmpl': filename,               # Çıktı dosya adı
                'quiet': False,                     # Sadece hataları göster
                'ignoreerrors': True,              # Hatalı videoları atla
                'geo-bypass': True,
            }
            await self.send_log_message(f"İndirilmeye başlandı: {url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            await self.send_log_message(f"İndirme tamamlandı: {url}")

        except yt_dlp.utils.DownloadError as e:
            error_message = f"Download error for {url}: {str(e)}"
            traceback_message = traceback.format_exc()
            await self.send_log_message(f"{error_message}\n\nYığın İzleme:\n{traceback_message}")
            raise

        except Exception as e:
            error_message = f"Beklenmedik bir hata oluştu (Download Audio): {str(e)}"
            traceback_message = traceback.format_exc()
            await self.send_log_message(f"{error_message}\n\nYığın İzleme:\n{traceback_message}")
            raise

    async def play_next(self, ctx):
        try:
            if self.queue.empty():
                self.playing = False
                await self.voice_client.disconnect()
                await self.send_log_message("Kuyruk boş, sesli kanaldan çıkıldı.")
                return

            url = await self.queue.get()
            await self.send_log_message(f"Şarkı çalınmaya başlandı: {url}")

            # Music modülünün bulunduğu klasörü al
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # temps klasörünü oluştur
            temp_dir = os.path.join(current_directory, 'temps')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Şarkı dosyasının adını belirle (URL'ye göre)
            song_filename = re.sub(r'\W+', '', url)  # URL'den özel karakterleri kaldır
            filename = os.path.join(temp_dir, f"{song_filename}.mp3")

            # Şarkının başlığını almak için yt_dlp kullan
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info_dict = ydl.extract_info(url, download=False)
                    song_title = info_dict.get('title', 'Bilinmeyen Şarkı')
                    thumbnail_url = info_dict.get('thumbnail', '')
                except yt_dlp.utils.DownloadError as e:
                    error_message = f"Video bilgileri çıkarılırken hata oluştu: {str(e)}"
                    traceback_message = traceback.format_exc()
                    await self.send_log_message(f"{error_message}\n\nYığın İzleme:\n{traceback_message}")

                    embed = discord.Embed(
                        title="❌ Hrrrrr ❌",
                        description=f"**{url}** \nBen bunu çalamam, bir sonraki şarkıya geçiyorum.",
                        color=discord.Color.red()
                    )
                    embed.set_footer(text="Error: Bisonun Keyfi")
                    
                    await ctx.send(embed=embed)
                    return await self.play_next(ctx)

            # Eğer şarkı zaten indirilmişse, tekrar indirme
            if not os.path.exists(filename):
                await self.download_audio(url, filename)

            # Sesli kanala bağlan
            if self.voice_client is None or not self.voice_client.is_connected():
                self.voice_client = await ctx.author.voice.channel.connect()

            # Sesli kanalda çal
            audio_source = discord.FFmpegPCMAudio(filename)
            self.voice_client.play(audio_source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))

            # Embed oluştur ve gönder
            embed = discord.Embed(
                title="🎶Miyaaavvv🎶",
                description=f"**{song_title}**",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Şarkıcı: BISOOO🐱")
            embed.set_image(url=thumbnail_url)

            await ctx.send(embed=embed)

            # Sıradaki şarkıyı önceden indir (ama kuyruğun dışına çıkartma!)
            if not self.queue.empty():
                next_url = self.queue._queue[0]  
                next_song_filename = re.sub(r'\W+', '', next_url)  
                next_filename = os.path.join(temp_dir, f"{next_song_filename}.mp3")

                # Eğer şarkı yoksa indir
                if not os.path.exists(next_filename):
                    self.bot.loop.create_task(self.download_audio(next_url, next_filename))

        except Exception as e:
            error_message = f"Beklenmedik bir hata oluştu (play_next): {str(e)}"
            traceback_message = traceback.format_exc()
            await self.send_log_message(f"{error_message}\n\nYığın İzleme:\n{traceback_message}")
            raise

    @commands.command(name="p")
    async def play(self, ctx, playlist_url, song_name=None):
        try:
            if not ctx.author.voice:
                await ctx.send("Bir ses kanalında olmalısınız!")
                return

            if not self.voice_client or not self.voice_client.is_connected():
                self.voice_client = await ctx.author.voice.channel.connect()

            if song_name:
                # Şarkı ismi verildiğinde arama yap
                await self.search_and_play(ctx, song_name)

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

        except Exception as e:
            error_message = f"Beklenmedik bir hata oluştu (play komutu): {str(e)}"
            traceback_message = traceback.format_exc()
            await self.send_log_message(f"{error_message}\n\nYığın İzleme:\n{traceback_message}")
            raise

async def setup(bot):
    try:
        await bot.add_cog(Music(bot))
        print("Music cog başarıyla yüklendi.")
    except Exception as e:
        print(f"Cog yüklenirken hata oluştu: {e}")
