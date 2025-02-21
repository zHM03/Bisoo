import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio
import os
from dotenv import load_dotenv

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []  # Şarkı kuyruğu

        # .env dosyasından çevresel değişkenleri yükle
        load_dotenv()

        # Spotify Authentication
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                                                              client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                                                              redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
                                                              scope="user-library-read"))

    def get_song_info(self, spotify_url):
        """Spotify URL'sinden şarkı bilgilerini alır."""
        track = self.sp.track(spotify_url)
        song_name = track['name']
        artist_name = track['artists'][0]['name']
        return song_name, artist_name

    def search_and_play_song(self, song_name, artist_name):
        """Şarkıyı YouTube'da arar ve oynatılabilir URL'yi döner."""
        search_query = f"{song_name} {artist_name}"
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
            video_url = info['entries'][0]['url']
            title = info['entries'][0]['title']
            return video_url, title

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
                print("✅ Bot kanaldan ayrıldı!")  # Log çıktısı

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

        # Dosya adını şarkı adı ve şarkıcı adıyla oluştur
        song_name, artist_name = title.split(" - ")
        file_name = f"downloads/{song_name} - {artist_name}.webm"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_name,
            'noplaylist': True,
            'quiet': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        def after_callback(error):
            if error:
                print(f"Şarkı oynatma sırasında hata oluştu: {error}")
            self.bot.loop.create_task(self.after_play(ctx))

            # Oynatma bittikten sonra dosyayı sil
            if os.path.exists(file_name):
                os.remove(file_name)

        voice_client.play(discord.FFmpegPCMAudio(file_name), after=after_callback)

        # Embed mesajı ile çalan şarkıyı göster
        embed = discord.Embed(title="🎵 Şimdi Çalıyor", description=f"**{title}**", color=discord.Color.green())
        embed.add_field(name="Bağlantı", value=url, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def p(self, ctx, spotify_url):
        """Spotify URL'si alır, şarkıyı kuyruğa ekler ve eğer bot şu an çalmıyorsa başlatır."""
        song_name, artist_name = self.get_song_info(spotify_url)
        video_url, title = self.search_and_play_song(song_name, artist_name)
        
        self.song_queue.append((video_url, title))

        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await self.play_next(ctx)

async def setup(bot):
    await bot.add_cog(Music(bot))