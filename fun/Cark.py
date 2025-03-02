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

        sonuç = random.choice(seçenekler)  # Rastgele bir seçenek seç
        açılar = np.linspace(0, 360, 20)  # 20 karelik dönüş animasyonu
        resimler = []
        dosya_adı = "spin.gif"

        for açı in açılar:
            fig, ax = plt.subplots(figsize=(3, 3), dpi=100)  # Daha küçük çark
            ax.set_facecolor("none")  # Arka planı şeffaf yap

            # Çarkın bölümleri
            wedges, texts = ax.pie(
                [1] * len(seçenekler),
                startangle=açı,
                colors=plt.cm.Paired.colors
            )

            # Yazıları çarkın içine ekleyelim
            for i, text in enumerate(texts):
                text.set_text("")  # Varsayılan etiketleri sil
                açı_değeri = (360 / len(seçenekler)) * i + açı  # Her bölüme açısını ver
                x = 0.6 * np.cos(np.radians(açı_değeri))  # X koordinatı
                y = 0.6 * np.sin(np.radians(açı_değeri))  # Y koordinatı
                ax.text(x, y, seçenekler[i], ha="center", va="center", fontsize=10, color="black", fontweight="bold")

            # Üstte sabit işaret (kazananın üstte durmasını sağlıyor)
            ax.text(0, 1.2, "▼", ha="center", va="center", fontsize=20, color="red", fontweight="bold")

            plt.axis("off")  # Kenar çizgilerini kaldır
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