from pytube import Playlist

def get_video_urls(playlist_url):
    # Playlist'i al
    playlist = Playlist(playlist_url)
    
    # Playlist'teki video URL'lerini doğrudan alıyoruz
    video_urls = playlist.video_urls
    
    return video_urls

# Kullanım
playlist_url = "https://www.youtube.com/watch?v=i22fa3pFpi8&list=PL4O5_OEp-Q9ZkPaKnEgTt0442_5b01fib"  # Playlist URL'si
video_urls = get_video_urls(playlist_url)

# Video URL'lerini yazdır
for idx, url in enumerate(video_urls, 1):
    print(f"{idx}. {url}")
