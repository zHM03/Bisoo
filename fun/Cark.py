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
            await ctx.send("⚠️ En az 2 seçenek girmelisin! Örnek: `!çark a b c d`")
            return

        açılar = np.linspace(0, 360 * 3, 20)  # 3 tur dönüp duracak
        resimler = []
        dosya_adı = "spin.gif"

        final_açı = random.uniform(0, 360)  # Rastgele bir açıda duracak
        bölüm_sayısı = len(seçenekler)
        bölüm_açısı = 360 / bölüm_sayısı  # Her bölümün açısı

        # Kazananı hesapla (Çarkın üst kısmında olan bölüm)
        kazanan_index = int((360 - final_açı) // bölüm_açısı) % bölüm_sayısı
        kazanan = seçenekler[kazanan_index]

        for açı in açılar:
            döndürme_açısı = açı + final_açı  # Çarkın son açısına göre döndür
            fig, ax = plt.subplots(figsize=(3, 3), dpi=100)
            ax.set_facecolor("none")  

            wedges, _ = ax.pie(
                [1] * bölüm_sayısı,
                startangle=döndürme_açısı,
                colors=plt.cm.Paired.colors
            )

            # Yazıları çarkın içine ekleyelim
            for i in range(bölüm_sayısı):
                açı_değeri = (bölüm_açısı * i) + döndürme_açısı + (bölüm_açısı / 2)
                x = 0.6 * np.cos(np.radians(açı_değeri))
                y = 0.6 * np.sin(np.radians(açı_değeri))
                ax.text(x, y, seçenekler[i], ha="center", va="center", fontsize=10, color="black", fontweight="bold")

            # Üstte sabit işaret
            ax.text(0, 1.2, "▼", ha="center", va="center", fontsize=20, color="red", fontweight="bold")

            plt.axis("off")
            plt.savefig(f"frame_{int(açı)}.png", transparent=True)
            plt.close()
            resimler.append(imageio.imread(f"frame_{int(açı)}.png"))

        imageio.mimsave(dosya_adı, resimler, duration=0.05)

        # Geçici dosyaları temizle
        for açı in açılar:
            os.remove(f"frame_{int(açı)}.png")

        await ctx.send(f"🎡 Çark dönüyor... Sonuç: **{kazanan}**", file=discord.File(dosya_adı))

        os.remove(dosya_adı)

async def setup(bot):
    await bot.add_cog(Cark(bot))