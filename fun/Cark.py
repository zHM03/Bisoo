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
            fig, ax = plt.subplots(figsize=(5, 5))
            wedges, texts = ax.pie([1]*len(seçenekler), labels=seçenekler, startangle=açı, colors=plt.cm.Paired.colors)
            plt.savefig(f"frame_{int(açı)}.png")
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