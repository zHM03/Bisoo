import asyncio
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Spotify API ayarları
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.log_channel_name = "biso-log"  # Loglar için kanal adı
        self.ytdl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '256',
            }],
        }

    async def get_log_channel(self, guild):
        """Belirtilen guild'deki log kanalını bul"""
        return discord.utils.get(guild.text_channels, name=self.log_channel_name)

    def log_message(self, message):
        """Log mesajını tarih, saat ile birlikte formatlayarak döndür"""
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {message}"

    async def log_error(self, message):
        """Log kanalına hata mesajı gönder"""
        formatted_message = self.log_message(message)
        for guild in self.bot.guilds:
            log_channel = await self.get_log_channel(guild)
            if log_channel:
                await log_channel.send(f"**Log:** {formatted_message}")

    async def play_song(self, ctx, audio_url, song_title):
        """Şarkıyı çalmaya başla"""
        if not ctx.author.voice:
            await ctx.message.add_reaction('❌')  # Hata: Sesli kanalda değil
            await self.log_error(f"'{ctx.author}' şarkı çalmaya çalıştı ancak sesli kanalda değildi.")
            return

        # Eğer bot sesli kanalda değilse bağlan
        if not self.voice_client or not self.voice_client.is_connected():
            self.voice_client = await ctx.author.voice.channel.connect()
            await self.log_error(f"Biso sesli kanala bağlandı: {ctx.author.voice.channel.name}")

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        def after_playing(error):
            if error:
                self.bot.loop.create_task(self.log_error(f"Şarkı çalarken bir hata oluştu: {error}"))
            if self.voice_client and self.voice_client.is_connected():
                self.bot.loop.create_task(self.voice_client.disconnect())

        try:
            self.voice_client.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), after=after_playing)
            await ctx.message.add_reaction('✅')  # Başarılı: Şarkı çalıyor
            await self.log_error(f"Şarkı çalıyor: '{song_title}'")

        except Exception as e:
            await ctx.message.add_reaction('❌')  # Hata: Oynatma sırasında problem
            await self.log_error(f"Şarkıyı oynatırken bir hata oluştu: {e}")

    @commands.command()
    async def p(self, ctx, *, link_or_song):
        """YouTube veya Spotify bağlantısından şarkı ekler veya şarkı adıyla YouTube'dan arama yapar"""
        with YoutubeDL(self.ytdl_opts) as ydl:
            try:
                if "spotify.com/track" in link_or_song:
                    track_id = link_or_song.split('/')[-1].split('?')[0]
                    track_info = sp.track(track_id)
                    track_name = track_info['name']
                    search_url = f"ytsearch:{track_name}"
                    info = ydl.extract_info(search_url, download=False)
                    video_url = info['entries'][0]['url']
                elif "youtube.com/watch" in link_or_song or "youtu.be" in link_or_song:
                    info = ydl.extract_info(link_or_song, download=False)
                    video_url = info['url']
                    track_name = info['title']
                else:
                    search_url = f"ytsearch:{link_or_song}"
                    info = ydl.extract_info(search_url, download=False)
                    video_url = info['entries'][0]['url']
                    track_name = info['entries'][0]['title']

                if not ctx.author.voice:
                    await ctx.message.add_reaction('❌')
                    await self.log_error(f"'{ctx.author}' şarkı çalmaya çalıştı ancak sesli kanalda değildi.")
                    return

                await self.play_song(ctx, video_url, track_name)

            except Exception as e:
                await ctx.message.add_reaction('❌')
            try:
                await ctx.send("Hrrr çaldığımı görmüyon mü.")
            except Exception as e:
                await self.log_error(f"Bir hata oluştu: {e}")

async def setup(bot):
    await bot.add_cog(Music(bot))  # Music cogs'ı ekliyoruz

