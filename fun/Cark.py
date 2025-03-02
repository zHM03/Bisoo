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
            await ctx.send("⚠️ En az 2 seçenek girmelisin! Örnek: `!çark a b c d e`")
            return

        tur_sayısı = 3  # Kaç tam tur dönecek
        kare_sayısı = 20  # Animasyon için kaç kare oluşturulacak
        açılar = np.linspace(0, 360 * tur_sayısı, kare_sayısı)  # Döndürme açıları
        son_açı = random.uniform(0, 360)  # Rastgele son durma açısı
        çark_açısı = açılar + son_açı

        dosya_adı = "cark_animasyon.gif"
        resimler = []
        bölüm_sayısı = len(seçenekler)
        bölüm_açısı = 360 / bölüm_sayısı  # Her seçeneğin açısı
        geçici_dosyalar = []  # Geçici dosyaları takip etmek için liste

        # Özel renk dizisi (sırasıyla tekrar eder)
        renkler = ["#ff4545", "#00ff99", "#006aff", "#ff4545"]
        renkler = [renkler[i % len(renkler)] for i in range(bölüm_sayısı)]  # Döngüyle renkleri eşleştir

        for açı in çark_açısı:
            fig, ax = plt.subplots(figsize=(4, 4), dpi=300)
            ax.set_facecolor("none")  # Arka plan şeffaf

            # Çarkı çiz
            wedges, _ = ax.pie(
                [1] * bölüm_sayısı,
                startangle=açı,
                colors=renkler,
                wedgeprops={"edgecolor": "black", "linewidth": 2}  # Kenar çizgileri eklendi
            )

            # Yazıları ekle
            for i in range(bölüm_sayısı):
                yazı_açısı = (bölüm_açısı * i) + açı + (bölüm_açısı / 2)
                x = 0.6 * np.cos(np.radians(yazı_açısı))
                y = 0.6 * np.sin(np.radians(yazı_açısı))
                ax.text(x, y, seçenekler[i], ha="center", va="center", fontsize=12, color="black", fontweight="bold")

            # Üstte sabit duran işaret (▼)
            ax.text(0, 1.1, "▼", ha="center", va="center", fontsize=20, color="red", fontweight="bold")

            plt.axis("off")
            resim_adı = f"frame_{int(açı)}.png"
            plt.savefig(resim_adı, transparent=True, bbox_inches='tight', pad_inches=0.1)
            plt.close()
            geçici_dosyalar.append(resim_adı)  # Dosya adını listeye ekle
            resimler.append(imageio.imread(resim_adı))

        # Animasyonu oluştur
        imageio.mimsave(dosya_adı, resimler, duration=0.05)

        # Geçici dosyaları temizle
        for dosya in geçici_dosyalar:
            if os.path.exists(dosya):
                os.remove(dosya)

        await ctx.send("🎡 Çark dönüyor...", file=discord.File(dosya_adı))

        # Çark animasyonunu da temizle
        if os.path.exists(dosya_adı):
            os.remove(dosya_adı)

async def setup(bot):
    await bot.add_cog(Cark(bot))