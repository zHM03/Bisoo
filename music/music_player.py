import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from pytube import Playlist
import re
import requests

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.playing = False
        self.voice_client = None

    def get_video_urls(self, playlist_url):
        """Playlist URL'sinden video URL'lerini al"""
        playlist = Playlist(playlist_url)
        return playlist.video_urls

    def is_playlist(self, url):
        """Playlist URL'sinin olup olmadığını kontrol et"""
        playlist_pattern = r'list='  # Playlist URL'lerini tanımlayacak basit bir regex
        return bool(re.search(playlist_pattern, url))

    async def download_audio(self, url, filename):
        """Verilen URL'den ses dosyasını indir"""
        ydl_opts = {
            'format': 'bestaudio/best',        # En iyi ses formatını seç
            'outtmpl': filename,               # Çıktı dosya adı
            'quiet': False,                     # Sadece hataları göster
            'ignoreerrors': True,              # Hatalı videoları atla
            'geo-bypass': True,
        }
        print(f"{url} - İndirilmeye başlandı")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    async def play_next(self, ctx):
        if self.queue.empty():
            self.playing = False
            if self.voice_client:
                await self.voice_client.disconnect()  # Kanaldan ayrıl
            return

        url = await self.queue.get()

        # Sesli kanala bağlan (Zaten bağlıysa bağlanma)
        if self.voice_client is None or not self.voice_client.is_connected():
            self.voice_client = await ctx.author.voice.channel.connect()

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
                print(f"Hata: {e}")

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

    def search_youtube(self, query):
        """YouTube'da şarkıyı arar ve URL'yi döner"""
        search_url = f"https://www.youtube.com/results?search_query={query}"
        html = requests.get(search_url).text
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        return f"https://www.youtube.com/watch?v={video_ids[0]}"

    @commands.command(name="p")
    async def play(self, ctx, *args):
        """Playlist, video URL'si veya şarkı ismi ile müzik çalmaya başla"""
        if not ctx.author.voice:
            await ctx.send("Bir ses kanalında olmalısınız!")
            return

        if self.voice_client is None or not self.voice_client.is_connected():
            # Ses kanalına bağlan
            self.voice_client = await ctx.author.voice.channel.connect()

        if args:
            # Eğer şarkı ismi verilmişse, YouTube'da ara ve oynat
            query = ' '.join(args)
            video_url = self.search_youtube(query)
            await self.queue.put(video_url)
        elif len(args) == 1 and self.is_playlist(args[0]):
            # Playlist URL'si olduğunda pytube ile video URL'lerini al
            video_urls = self.get_video_urls(args[0])
            for url in video_urls:
                await self.queue.put(url)
        else:
            # Tekil video URL'si olduğunda direkt olarak URL'yi kuyruğa ekle
            await self.queue.put(args[0])

        if not self.playing:
            self.playing = True
            # Eğer bot şarkı çalmıyorsa, play_next fonksiyonunu çağır
            await self.play_next(ctx)

    @commands.command(name="l")
    async def leave(self, ctx):
        """Bot ses kanalından ayrılır"""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            self.playing = False
            self.queue = asyncio.Queue()  # Kuyruğu sıfırla
            await ctx.message.add_reaction("😿")  # Komutu kullanan kullanıcının mesajına tepki ekle


async def setup(bot):
    await bot.add_cog(Music(bot))
