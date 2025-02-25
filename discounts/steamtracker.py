import discord
from discord.ext import commands, tasks
import json
import requests
import os  # os modülünü import ettik

class SteamTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_games = {}
        self.load_user_data()
        self.check_for_discounts.start()

    def load_user_data(self):
        # Modülün bulunduğu dizini almak
        module_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(module_dir, 'user_games.json')  # JSON dosyasının tam yolu

        try:
            with open(file_path, 'r') as f:
                self.user_games = json.load(f)
        except FileNotFoundError:
            self.user_games = {}

    def save_user_data(self):
        # Modülün bulunduğu dizini almak
        module_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(module_dir, 'user_games.json')  # JSON dosyasının tam yolu

        with open(file_path, 'w') as f:
            json.dump(self.user_games, f)

    @commands.command()
    async def addgame(self, ctx, *, game_name: str):  # *game_name ile tüm metni alıyoruz
        game_name_lower = game_name.lower().strip()  # Oyun adını küçük harfe çevirip boşlukları temizliyoruz
        game_id = self.get_steam_game_id(game_name_lower)
        
        if not game_id:
            await ctx.send(f"{game_name} oyunu bulunamadı.")
            return
        
        price, discount = self.get_steam_game_price(game_name_lower)

        if discount > 0:
            await ctx.send(f"{game_name} şu anda indirime girdi, bu nedenle kaydedilmedi.")
        else:
            if str(ctx.author.id) not in self.user_games:
                self.user_games[str(ctx.author.id)] = []
            
            self.user_games[str(ctx.author.id)].append({"game_name": game_name_lower, "price": price, "discount": discount})
            self.save_user_data()
            await ctx.send(f"{game_name} başarıyla listeye eklendi! Fiyatı: {price} TL.")

    @commands.command()
    async def gamelist(self, ctx):
        """Kullanıcının kaydettiği oyunları listeler."""
        user_id = str(ctx.author.id)
        
        if user_id not in self.user_games or not self.user_games[user_id]:
            await ctx.send("Henüz kaydedilmiş bir oyununuz yok.")
            return
        
        game_list = "\n".join([f"{game['game_name'].capitalize()} - Fiyat: {game['price']} TL, İndirim: %{game['discount']}" for game in self.user_games[user_id]])
        
        await ctx.send(f"Kaydedilen Oyunlar:\n{game_list}")

    def get_steam_game_data(self, game_name):
        search_url = f'https://store.steampowered.com/api/storesearch?term={game_name}&category_ownership=1&cc=us'
        try:
            response = requests.get(search_url)
            response.raise_for_status()  # HTTP hata durumlarını kontrol et
            data = response.json()

            if data['total'] == 0:
                return None, None, None  # Oyun bulunamadı

            # İlk sonucu alalım
            game_info = data['items'][0]
            game_id = game_info['id']
            price, discount = self.get_steam_game_price(game_id)
            return game_id, price, discount
        except requests.exceptions.RequestException as e:
            print(f"API isteği sırasında bir hata oluştu: {e}")
            return None, None, None

    def get_steam_game_price(self, game_name):
        game_id = self.get_steam_game_id(game_name)
        if not game_id:
            return None, None
        
        url = f'https://store.steampowered.com/api/appdetails?appids={game_id}'
        response = requests.get(url).json()
        
        if response.get(str(game_id)) and response[str(game_id)].get('data'):
            price = response[str(game_id)]['data'].get('price_overview', {}).get('final_formatted', 'Bilinmiyor')
            discount = response[str(game_id)]['data'].get('price_overview', {}).get('discount_percent', 0)
            return price, discount
        return None, None

    def get_steam_game_id(self, game_name):
        game_name = game_name.strip().lower()  # Oyun adı başındaki ve sonundaki boşlukları temizle ve küçük harfe çevir
        url = f'https://store.steampowered.com/api/storesearch'
        params = {
            'term': game_name,  # Oyun adıyla tam arama yapıyoruz
            'category': '998',  # İndirime giren oyunlar kategorisi
            'cc': 'tr'  # Bölge seçeneği (Türkiye)
        }
        
        try:
            response = requests.get(url, params=params).json()

            if 'items' in response:
                for item in response['items']:
                    # Oyun adının küçük harflerle ve boşluklar göz ardı edilerek karşılaştırma yapılması
                    if game_name in item['name'].lower():  # Küçük harf karşılaştırması
                        return item['id']  # Oyun ID'sini döndürüyoruz
            return None  # Eğer oyun bulunmazsa None döner
        except requests.exceptions.RequestException as e:
            print(f"API isteği sırasında bir hata oluştu: {e}")
            return None

    @tasks.loop(hours=24)
    async def check_for_discounts(self):
        discount_channel_id = 1341428278879326298  # Sabit kanal ID'si (örneğin, #indirimler kanalı)
        discount_channel = self.bot.get_channel(discount_channel_id)  # Kanal objesini alıyoruz
    
        if not discount_channel:
                print(f"Kanal {discount_channel_id} bulunamadı.")
                return  
    
        for user_id, games in self.user_games.items():
            for game_data in games:
                game_name = game_data["game_name"]
                price, discount = self.get_steam_game_price(game_name)
                
                if discount > 0 and game_data["discount"] == 0:  # Eğer indirim varsa ve daha önce yoktu
                    user = self.bot.get_user(int(user_id))
                    if user:
                        # Embed mesajını oluşturuyoruz
                        embed = discord.Embed(
                            title=f"{game_name} İndirime Girdi!",  # Başlık kısmı
                            description=f"{game_name} artık **%{discount}** indirimde! 🎉",  # Açıklama
                            color=0x00FF00  # Renk kodu (Yeşil - İndirim için uygun)
                        )
                        
                        # Embed'e eski ve yeni fiyatı ekliyoruz
                        embed.add_field(name="Eski Fiyat", value=f"**{game_data['price']} TL**", inline=True)
                        embed.add_field(name="Yeni Fiyat", value=f"**{price} TL**", inline=True)
                        
                        # Bildirimi gönderiyoruz
                        await user.send(embed=embed)
                    
                    # Verileri güncelliyoruz
                    game_data["discount"] = discount
                    game_data["price"] = price
                    self.save_user_data()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog {self.__class__.__name__} yüklendi.')
        if not self.check_for_discounts.is_running():
            self.check_for_discounts.start()

async def setup(bot):
    await bot.add_cog(SteamTracker(bot))
