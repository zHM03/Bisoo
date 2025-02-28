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

    async def get_steamdb_game_id(self, game_name, ctx):  
        # SteamDB API kullanarak oyun ID'sini buluyoruz
        game_name = game_name.strip().lower()
        url = 'https://api.steampowered.com/ISteamApps/GetAppList/v2'  # SteamDB API'den oyunları almak için
        try:
            response = requests.get(url).json()
            # Oyunları arıyoruz ve adlarıyla eşleştiriyoruz
            games = response.get('applist', {}).get('apps', [])
            found_games = [game for game in games if game_name in game['name'].lower()]
            
            if len(found_games) == 1:
                return found_games[0]['appid']  # Oyun bulunduysa ID'sini döndürüyoruz
            elif len(found_games) > 1:
                game_choices = "\n".join([f"{index + 1}. {game['name']}" for index, game in enumerate(found_games)])
                if ctx:
                    await ctx.send(f"Birden fazla oyun bulundu:\n{game_choices}\nLütfen bir oyun numarası girin.")
                
                def check(m):
                    return m.author == ctx.author and m.content.isdigit() and 1 <= int(m.content) <= len(found_games)

                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=30)
                    selected_game = found_games[int(msg.content) - 1]
                    return selected_game['appid']
                except:
                    if ctx:
                        await ctx.send("Geçerli bir seçenek girilmedi, işlem iptal edildi.")
                    return None
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"API isteği sırasında bir hata oluştu: {e}")
            return None

    def get_steamdb_game_price(self, game_id):  
        # SteamDB API'den fiyatı alıyoruz
        url = f'https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2?appid={game_id}'  
        try:
            response = requests.get(url).json()
            if response.get("game", {}).get("steamPrice"):
                price = response["game"]["steamPrice"]
                return price["final"] / 100  # Steam fiyatı genellikle cent olarak gelir
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Fiyat alma sırasında hata oluştu: {e}")
            return None

    @commands.command()
    async def addgame(self, ctx, *, game_name: str):  
        game_name_lower = game_name.lower().strip()  # Oyun adını küçük harfe çeviriyoruz  

        if str(ctx.author.id) in self.user_games:  
            if any(game['game_name'] == game_name_lower for game in self.user_games[str(ctx.author.id)]):  
                await ctx.send(f"{game_name} zaten kaydedilmiş!")  
                return  

        game_id = await self.get_steamdb_game_id(game_name_lower, ctx)  

        if not game_id:  
            await ctx.send(f"{game_name} oyunu bulunamadı veya işlem iptal edildi.")  
            return  

        price = self.get_steamdb_game_price(game_id)  # Fiyat bilgisini alıyoruz  

        if price is None:  
            await ctx.send(f"{game_name} fiyat bilgisi alınamadı.")  
            return  

        if str(ctx.author.id) not in self.user_games:  
            self.user_games[str(ctx.author.id)] = []  

        self.user_games[str(ctx.author.id)].append({"game_name": game_name_lower, "price": price})  
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

    @tasks.loop(minutes=10)  # Her 10 dakikada bir kontrol eder  
    async def check_discounts(self):  
        channel = self.bot.get_channel(self.channel_id)  
        for user_id, games in self.user_games.items():  
            for game in games:  
                game_name = game['game_name']  
                game_id = await self.get_steamdb_game_id(game_name, None)  

                if not game_id:  
                    continue  

                price = self.get_steamdb_game_price(game_id)  

                if price is None:  
                    continue  

                if price < game['price']:  
                    user = self.bot.get_user(int(user_id))  
                    if user:  
                        await channel.send(f"{game_name} şu anda indirime girdi! {user.mention} oyununu listeye eklemişti.")  

async def setup(bot):
    await bot.add_cog(GameBot(bot))