o
    ��g�  �                   @   s�   d dl Z d dlmZmZ d dlZd dlZd dlmZ d dlZd dl	Z	e�  e�
d�ZdZdd� Zdd	� Zd
d� Zdd� Zdd� ZG dd� dej�Zdd� ZdS )�    N)�commands�tasks)�load_dotenvZCRYPTOCOMPARE_API_KEYz,https://min-api.cryptocompare.com/data/pricec                 C   s"   t �� }|�d�}d|� d|� �S )u>   Log mesajını tarih, saat ile birlikte formatlayarak döndürz%Y-%m-%d %H:%M:%S�[z] )�datetime�now�strftime)�self�messager   �	timestamp� r   �Nc:\Users\HISOUL\Desktop\Projeler\Discord Bots\Harley Boyz\biso\other\crypto.py�log_message   s   
r   c                 �   sH   �| � |�}| jjD ]}| �|�I dH }|r!|�d|� ��I dH  q
dS )u"   Log kanalına hata mesajı gönderNz	**Log:** )r   �bot�guilds�get_log_channel�send)r	   r
   �formatted_message�guild�log_channelr   r   r   �	log_error   s   �
��r   c                 �   s   �t jj|jdd�}|S )u#   Log kanalını döndüren fonksiyonzbiso-log)�name)�discord�utils�get�text_channels)r	   r   r   r   r   r   r      s   �r   c                 C   sj   t � d| �� � d�}ddt� �i}tj||d�}|�� }td|� �� d|v r3d|v r3|d |d fS d	S )
Nz?fsym=z&tsyms=USD,TRY�AuthorizationzApikey )�headersu   API Yanıtı: ZUSDZTRY)NN)�BASE_URL�upper�API_KEY�requestsr   �json�print)�coin_symbol�urlr   �response�datar   r   r   �get_crypto_price#   s   
�r(   c                 C   s   d� | ��dd�S )u?   Sayısal değeri daha okunabilir hale getiren format fonksiyonuz{:,.2f}�,�.)�format�replace)�pricer   r   r   �format_price2   s   r.   c                   @   sH   e Zd Zdd� Zdd� Zejddd�dd	� �Ze�	� d
e
fdd��ZdS )�Cryptoc                 C   s   || _ | j��  d S �N)r   �send_daily_price�start)r	   r   r   r   r   �__init__7   s   zCrypto.__init__c                 C   s   | j ��  d S r0   )r1   �cancel)r	   r   r   r   �
cog_unload;   s   zCrypto.cog_unload�   T)�hours�	reconnectc                 �   s�   �t j �� }|jdkrB|jdkrB| j�d�}td�\}}|r8|r8t|�}t|�}|�d|� d|� d��I d H  n
| jj	�
d�I d H  t�d�I d H  d S )	Nr   l   *:Y� ZBTCu   24 saatlik BTC fiyatı: $�    / ₺�	... (YTD)u   BTC fiyatı alınamadı.�<   )r   r   �hour�minuter   �get_channelr(   r.   r   �musicr   �asyncio�sleep)r	   r   �channel�	price_usd�	price_try�formatted_usd�formatted_tryr   r   r   r1   >   s   �
 zCrypto.send_daily_price�coinc                 �   sv   �|� � }t|�\}}|r,|r,t|�}t|�}|�|�� � d|� d|� d��I dH  dS |�|�� � d��I dH  dS )u,   Belirli bir coin'in fiyatını yazacak komutu    fiyatı: $r9   r:   Nu     için fiyat verisi bulunamadı.)�lowerr(   r.   r   r   )r	   �ctxrG   r$   rC   rD   rE   rF   r   r   r   �cryptoN   s   �*zCrypto.cryptoN)�__name__�
__module__�__qualname__r3   r5   r   �loopr1   r   �command�strrJ   r   r   r   r   r/   6   s    
r/   c                 �   s   �| � t| ��I d H  d S r0   )�add_cogr/   )r   r   r   r   �setup\   s   �rR   )r   �discord.extr   r   r!   r@   �dotenvr   �osr   �getenvr    r   r   r   r   r(   r.   �Cogr/   rR   r   r   r   r   �<module>   s"    
&