import discord
from discord.ext import commands
from datetime import datetime

class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.song_queue = []  # Şarkı kuyruğu
        self.is_playing = False  # Şarkı çalıp çalmadığını kontrol eder
        self.current_song = None  # Şu anda çalan şarkı
        self.is_paused = False  # Şarkının duraklatılma durumu

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

    async def get_log_channel(self, guild):
        """Log kanalını döndüren fonksiyon"""
        log_channel = discord.utils.get(guild.text_channels, name="biso-log")
        return log_channel

class Music_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Music sınıfını bot nesnesine ekliyoruz
        self.bot.music = Music(bot)

    @commands.command()
    async def s(self, ctx):
        """Şarkıyı duraklat"""
        voice_client = ctx.voice_client  # Sesli kanal bağlantısını al

        # Botun bir sesli kanalda olup olmadığını kontrol et
        if not voice_client or not voice_client.is_connected():
            await ctx.send("Bot herhangi bir sesli kanalda değil. Lütfen önce bir sesli kanala katılın.")
            return

        # Bot sesli kanalda ve oynatma yapıyorsa duraklat
        if voice_client.is_playing() and not self.bot.music.is_paused:
            voice_client.pause()  # Şarkıyı duraklat
            self.bot.music.is_paused = True  # Duraklatıldı olarak işaretle
            await ctx.message.add_reaction('✅')  # Başarılı: Duraklatıldı

            # Log mesajını 'biso-log' kanalına gönder
            await self.bot.music.log_error("Bot şarkıyı duraklattı.")

        elif self.bot.music.is_paused:
            await ctx.send("Şarkı zaten duraklatıldı.")

    @commands.command()
    async def r(self, ctx):
        """Şarkıyı devam ettir"""
        voice_client = ctx.voice_client  # Sesli kanal bağlantısını al

        # Botun bir sesli kanalda olup olmadığını kontrol et
        if not voice_client or not voice_client.is_connected():
            await ctx.send("Bot herhangi bir sesli kanalda değil. Lütfen önce bir sesli kanala katılın.")
            return

        # Bot sesli kanalda ve duraklatılmışsa, şarkıyı devam ettir
        if self.bot.music.is_paused:
            voice_client.resume()  # Şarkıyı devam ettir
            self.bot.music.is_paused = False  # Duraklatma durumu kaldır
            await ctx.message.add_reaction('✅')  # Başarılı: Devam ettirildi

            # Log mesajını 'biso-log' kanalına gönder
            await self.bot.music.log_error("Bot şarkıyı devam ettirdi.")
        else:
            await ctx.send("Şarkı zaten çalıyor.")

    @commands.command()
    async def l(self, ctx):
        """FFmpeg işlemlerini durdur, kuyrukları temizle ve kanaldan ayrıl"""
        voice_client = ctx.voice_client  # Sesli kanal bağlantısını al

        # Botun bir sesli kanalda olup olmadığını kontrol et
        if not voice_client or not voice_client.is_connected():
            await ctx.send("Bot herhangi bir sesli kanalda değil. Lütfen önce bir sesli kanala katılın.")
            return

        # Bot sesli kanalda ve oynatma yapıyorsa durdur
        if voice_client.is_playing():
            voice_client.stop()
            await ctx.message.add_reaction('✅')  # Başarılı: Durduruldu
        # Bot sesli kanalda ve bağlıysa, kanaldan ayrıl
        if voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.message.add_reaction('✅')  # Başarılı: Sesli kanaldan ayrıldı

        self.bot.music.is_playing = False  # Doğru nesneyi kullanıyoruz

        # Log mesajını 'biso-log' kanalına gönder
        await self.bot.music.log_error("Bot FFmpeg işlemleri durdurdu, kuyruk temizlendi ve sesli kanaldan ayrıldı.")

async def setup(bot):
    await bot.add_cog(Music_commands(bot))
