import discord
import random
import numpy as np
import matplotlib.pyplot as plt
import imageio
import os
from discord.ext import commands

class Cark(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def çark(self, ctx, *seçenekler):
        if len(seçenekler) < 2:
            await ctx.send("⚠️ En az 2 seçenek girmelisin! Örnek: `!çark valorant lol apex`")
            return

        sonuç = random.choice(seçenekler)  # Rastgele bir sonuç seç
        açılar = np.linspace(0, 360, 20)  # 20 karelik dönüş animasyonu
        resimler = []
        dosya_adı = "spin.gif"

        for açı in açılar:
            fig, ax = plt.subplots(figsize=(4, 4), dpi=100)  # Daha küçük çark
            ax.set_facecolor("none")  # Arka planı şeffaf yap
            
            # Çarkın kendisi
            wedges, texts = ax.pie(
                [1] * len(seçenekler),
                labels=seçenekler,
                startangle=açı,
                colors=plt.cm.Paired.colors,
                textprops={'fontsize': 10, 'color': "black"}  # Yazıları çarkın içine al
            )

            # Üstte sabit işaret (kazananın üstte durmasını sağlıyor)
            ax.annotate("▼", xy=(0, 1), xycoords="axes fraction", ha="center", fontsize=20, color="red")

            plt.savefig(f"frame_{int(açı)}.png", transparent=True)  # Şeffaf kaydet
            plt.close()
            resimler.append(imageio.imread(f"frame_{int(açı)}.png"))

        imageio.mimsave(dosya_adı, resimler, duration=0.05)  # GIF oluştur

        # Geçici dosyaları temizle
        for açı in açılar:
            os.remove(f"frame_{int(açı)}.png")

        await ctx.send(f"🎡 Çark dönüyor... Sonuç: **{sonuç}**", file=discord.File(dosya_adı))

        os.remove(dosya_adı)  # GIF dosyasını temizle

# Botun Cogs'a bu sınıfı yüklemesi için
async def setup(bot):
    await bot.add_cog(Cark(bot))