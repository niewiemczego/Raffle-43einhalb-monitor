import requests
import time
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed

DELAY = 5
ALREADY_SENT = []
WEBHOOK_URL = "PASTE DISCORD WEBHOOK URL HERE"

def raffles_data():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    }
    raffles_urls = []
    raffles_names = []
    raffles_images = []
    raffles_price = []
    raffles_dates = []
    raffles_sku = []
    url = 'https://releases.43einhalb.com/'
    try:
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        raffles_list = soup.find_all('div', attrs={'class': 'col-12 col-sm-6 col-md-4'})
        available_raffles = [raffle for raffle in raffles_list if raffle.find('span', attrs={'class': 'display-variation soldout'}) == None]
        
        if len(available_raffles) > 0:
            raffle_urls = [raffle.find('a', attrs={'class': 'text-decoration-none'}).get('href') for raffle in available_raffles]
            for raffle_url in raffle_urls:
                page = requests.get(f'https://releases.43einhalb.com{raffle_url}', headers=headers)
                soup = BeautifulSoup(page.content, 'html.parser')
                raffles_urls.append(page.url)
                raffles_names.append(soup.find('h1', attrs={'class': 'h3'}).text)
                raffles_images.append(soup.find('img', attrs={'itemprop': 'associatedMedia'}).get('src'))
                raffles_price.append(soup.find('span', attrs={'itemprop': 'price'}).text)
                raffles_dates.append(soup.find('p', attrs={'class': 'raffleDetails'}).text.split('\n')[1][12:].split(' um '))
                raffles_sku.append(soup.find('span', attrs={'class': 'text-muted'}).text)
                
            data = {}
            data['raffles_urls'] = raffles_urls
            data['raffles_names'] = raffles_names
            data['raffles_images'] = raffles_images
            data['raffles_price'] = raffles_price
            data['raffles_dates'] = raffles_dates
            data['raffles_sku'] = raffles_sku
            return data
        return False
    except Exception as e:
        print(f"ERROR OCCURED!\n{e}")

def send_webhok(data, index, value):
    webhook = DiscordWebhook(url=WEBHOOK_URL, username="Tim Solutions makes difference", avatar_url="https://i.imgur.com/8KANDeK.jpg")
    embed = DiscordEmbed(title=data['raffles_names'][index], color='92A9BD', url=value)
    embed.set_thumbnail(url=data['raffles_images'][index])
    embed.add_embed_field(name="**:calendar: Date**", value=f"{data['raffles_dates'][index][0]}, {data['raffles_dates'][index][1][:5]} (CET)", inline=False)
    embed.add_embed_field(name="**:moneybag: Retail**", value=f"{data['raffles_price'][index]}", inline=False)
    embed.add_embed_field(name="**:pushpin: SKU**", value=f"{data['raffles_sku'][index]}", inline=False)
    embed.set_footer(
        text="Tim Solutions makes difference", 
        icon_url="https://i.imgur.com/8KANDeK.jpg"
    )
    embed.set_timestamp()
    webhook.add_embed(embed)
    response = webhook.execute()

def check_for_raffles():
    print("Started monitoring 43einhalb raffles!")
    while 1:
        print("Checking raffles...")
        try:
            data = raffles_data()
            if data:
                for index, value in enumerate(data['raffles_urls']):
                    if data['raffles_urls'][index] not in ALREADY_SENT:
                        print(f"New raffle: {data['raffles_urls'][index]}")
                        ALREADY_SENT.append(data['raffles_urls'][index])
                        send_webhok(data, index, value)
                        time.sleep(5)
                    else:
                        print(f"{data['raffles_urls'][index]} Has been already sent!")
            else:
                print("No available raffles!")
            print(f"Sleeping for {DELAY} seconds")
            time.sleep(DELAY)
        except Exception as e:
            print(f"ERROR OCCURED!\n{e}")


if __name__ == "__main__":
    check_for_raffles()
