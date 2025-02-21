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

    def search_and_play_song(self, query):
        """Şarkıyı YouTube'da arar ve oynatılabilir URL'yi döner."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if 'entries' in info:
                video_url = info['entries'][0]['url']
                title = info['entries'][0]['title']
                return video_url, title
            return None, None

    def get_playlist_songs(self, playlist_url):
        """YouTube Playlist URL'sinden şarkıları alır."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': True  # Playlistteki sadece şarkı URL'lerini almak için
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            return [(entry['url'], entry['title']) for entry in info['entries']]

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

        # Şarkıyı indirip ses akışına çalalım
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'extractaudio': True,  # Ses dosyasını çıkar
            'audioquality': 1,  # Ses kalitesini artır
            'outtmpl': 'downloads/%(id)s.%(ext)s',  # Dosyayı kaydetme yolu
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Dosyayı bellek üzerinden çal
        voice_client.play(discord.FFmpegPCMAudio(file_path), after=lambda e: self.after_play(ctx))

        # Embed mesajı ile çalan şarkıyı göster
        embed = discord.Embed(title="🎵 Şimdi Çalıyor", description=f"**{title}**", color=discord.Color.green())
        embed.add_field(name="Bağlantı", value=url, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def p(self, ctx, *, query):
        """YouTube linki, playlist veya şarkı adı alır, şarkıyı kuyruğa ekler ve eğer bot şu an çalmıyorsa başlatır."""
        if "playlist" in query:
            # Playlist linki ise şarkıları kuyruğa ekler
            playlist_songs = self.get_playlist_songs(query)
            self.song_queue.extend(playlist_songs)
        elif "https://open.spotify.com" in query:
            # Spotify linki ise şarkıyı Spotify'dan alır
            song_name, artist_name = self.get_song_info(query)
            video_url, title = self.search_and_play_song(f"{song_name} {artist_name}")
            if video_url:
                self.song_queue.append((video_url, title))
            else:
                await ctx.send("Şarkı bulunamadı.")
                return
        else:
            # Tekil YouTube şarkı linki veya şarkı adı ise doğrudan kuyruğa ekler.
            video_url, title = self.search_and_play_song(query)
            if video_url:
                self.song_queue.append((video_url, title))
            else:
                await ctx.send("Şarkı bulunamadı.")
                return

        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await self.play_next(ctx)

async def setup(bot):
    await bot.add_cog(Music(bot))
