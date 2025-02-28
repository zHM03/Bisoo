import requests
import json
from discord.ext import commands, tasks
import asyncio

class GameBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json_file = 'user_games.json'  # JSON dosya adı
        self.user_games = self.load_user_games()  # JSON dosyasındaki veriyi yüklüyoruz
        self.channel_id = 1341428278879326298  # Bildirimlerin gönderileceği kanal ID'si
        self.check_discounts.start()  # İndirimleri düzenli olarak kontrol etmeye başlıyoruz

    def load_user_games(self):
        # JSON dosyasından verileri yükle
        try:
            with open(self.json_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # Dosya bulunmazsa, boş bir sözlük döndürüyoruz

    def save_user_games(self):
        # JSON dosyasına verileri kaydet
        with open(self.json_file, 'w') as f:
            json.dump(self.user_games, f, indent=4)

    async def get_steam_game_id(self, game_name, ctx):
        # Oyun adını temizliyoruz ve API isteği yapıyoruz
        game_name = game_name.strip().lower()
        url = 'https://store.steampowered.com/api/storesearch'
        params = {
            'term': game_name,  # Arama terimi
            'category': '998',  # İndirime giren oyunlar kategorisi
            'cc': 'us'  # Amerikan Doları (USD) ile veri alıyoruz
        }

        try:
            response = requests.get(url, params=params).json()
            if 'items' in response:
                found_games = []
                # Sonuçlar arasında oyun adı eşleşmesi yapıyoruz
                for item in response['items']:
                    if game_name in item['name'].lower():
                        found_games.append(item)

                # Birden fazla oyun bulunduysa seçim yapmasını istiyoruz
                if len(found_games) > 1:
                    game_choices = "\n".join([f"{index + 1}. {game['name']}" for index, game in enumerate(found_games)])
                    if ctx:
                        await ctx.send(f"Birden fazla oyun bulundu:\n{game_choices}\nLütfen bir oyun numarası girin.")

                    def check(m):
                        return m.author == ctx.author and m.content.isdigit() and 1 <= int(m.content) <= len(found_games) if ctx else False

                    try:
                        msg = await self.bot.wait_for('message', check=check, timeout=30)
                        selected_game = found_games[int(msg.content) - 1]
                        return selected_game['id']  # Seçilen oyunun ID'sini döndürüyoruz
                    except:
                        if ctx:
                            await ctx.send("Geçerli bir seçenek girilmedi, işlem iptal edildi.")
                        return None
                elif len(found_games) == 1:
                    return found_games[0]['id']  # Sadece bir oyun bulunduğunda o oyunun ID'sini döndürüyoruz
            return None  # Eğer oyun bulunmazsa None döner
        except requests.exceptions.RequestException as e:
            print(f"API isteği sırasında bir hata oluştu: {e}")
            return None

    def get_steam_game_price(self, game_id):
        # Steam API'yi kullanarak gerçek fiyatları alıyoruz.
        url = f'https://store.steampowered.com/api/appdetails?appids={game_id}'
        try:
            response = requests.get(url).json()
            if str(game_id) in response and response[str(game_id)]['success']:
                # Fiyat bilgisi ve para birimi alınıyor
                data = response[str(game_id)]['data']
                price_usd = data['price_overview']['final'] / 100  # Steam fiyatı genellikle cent olarak gelir
                discount_percent = data['price_overview']['discount_percent']  # İndirim oranı
                return price_usd, discount_percent  # Fiyat ve indirim oranını döndürüyoruz
            else:
                return None, None
        except requests.exceptions.RequestException as e:
            print(f"Fiyat alma sırasında hata oluştu: {e}")
            return None, None

    @commands.command()
    async def addgame(self, ctx, *, game_name: str):
        game_name_lower = game_name.lower().strip()  # Oyun adını küçük harfe çeviriyoruz

        # Eğer kullanıcı zaten bu oyunu eklemişse, tekrar eklemiyoruz
        if str(ctx.author.id) in self.user_games:
            if any(game['game_name'] == game_name_lower for game in self.user_games[str(ctx.author.id)]):
                await ctx.send(f"{game_name} zaten kaydedilmiş!")
                return

        game_id = await self.get_steam_game_id(game_name_lower, ctx)  # Asenkron fonksiyonla oyun ID'sini alıyoruz

        if not game_id:
            await ctx.send(f"{game_name} oyunu bulunamadı veya işlem iptal edildi.")
            return

        price, discount = self.get_steam_game_price(game_id)  # Oyun fiyatını ve indirimi alıyoruz

        if price is None:
            await ctx.send(f"{game_name} fiyat bilgisi alınamadı.")
            return

        # Eğer oyun indirime girmişse listeye eklemiyoruz
        if discount > 0:
            await ctx.send(f"{game_name} şu anda indirime girdi, bu nedenle kaydedilmedi.")
        else:
            if str(ctx.author.id) not in self.user_games:
                self.user_games[str(ctx.author.id)] = []

            # Oyun zaten kaydedilmediyse ekleniyor
            self.user_games[str(ctx.author.id)].append({"game_name": game_name_lower, "price": price, "discount": discount})
            self.save_user_games()  # Oyun eklendikten sonra JSON dosyasını kaydediyoruz
            await ctx.send(f"{game_name} başarıyla listeye eklendi! Fiyatı: ${price:.2f} USD.")

    @commands.command()
    async def listgames(self, ctx):
        # Kullanıcının kaydettiği oyunları listele
        if str(ctx.author.id) in self.user_games:
            games = self.user_games[str(ctx.author.id)]
            game_list = "\n".join([f"{game['game_name']} - ${game['price']:.2f} USD" for game in games])
            await ctx.send(f"Kaydedilen oyunlar:\n{game_list}")
        else:
            await ctx.send("Henüz kaydedilen bir oyununuz yok.")

    @commands.command()
    async def removegame(self, ctx, *, game_name: str):
        game_name_lower = game_name.lower().strip()  # Oyun adını küçük harfe çeviriyoruz

        # Kullanıcı kaydettikleri oyunları kontrol ediyoruz
        if str(ctx.author.id) not in self.user_games or not self.user_games[str(ctx.author.id)]:
            await ctx.send("Henüz kaydedilen bir oyununuz yok.")
            return

        # Oyun adını kaydeden oyunlar arasında arıyoruz
        user_games = self.user_games[str(ctx.author.id)]
        game_to_remove = next((game for game in user_games if game['game_name'] == game_name_lower), None)

        if game_to_remove:
            # Oyun bulunursa, kaydedilen oyunlar listesinde çıkarıyoruz
            self.user_games[str(ctx.author.id)].remove(game_to_remove)
            self.save_user_games()  # JSON dosyasına kaydediyoruz
            await ctx.send(f"{game_name} başarıyla listeden kaldırıldı.")
        else:
            await ctx.send(f"{game_name} kaydedilen oyunlar arasında bulunamadı.")


    @tasks.loop(minutes=10)  # Her 10 dakikada bir kontrol eder
    async def check_discounts(self):
        channel = self.bot.get_channel(self.channel_id)  # Bildirim kanalı
        for user_id, games in self.user_games.items():
            for game in games:
                game_name = game['game_name']
                game_id = await self.get_steam_game_id(game_name, None)  # Asenkron fonksiyonla oyun ID'sini alıyoruz

                if not game_id:
                    continue

                price, discount = self.get_steam_game_price(game_id)  # Fiyat ve indirim oranını alıyoruz

                if price is None:
                    continue

                # Eğer indirim oranı 0'dan büyükse, indirime girmiş demektir
                if discount > 0:
                    user = self.bot.get_user(int(user_id))  # Kullanıcıyı ID ile buluyoruz
                    if user:
                        await channel.send(f"{game_name} şu anda indirime girdi! {user.mention} oyununu listeye eklemişti.")  # Kanalda bildirim gönderiyoruz

async def setup(bot):
    await bot.add_cog(GameBot(bot))
