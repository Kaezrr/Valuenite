from csv import DictReader
import requests
import time
import re

pattern = re.compile('[\W_]')

def main(path):

    start_time = time.time()

    global apps 
    apps = get_apps()
    games, app_ids = [], []
    highest, lowest = 0, 0

    with open(path, encoding='utf-8-sig') as file:
        reader = DictReader(file)
        for row in reader:
            games.append(pattern.sub('', row['Name']).lower())
    
    counter = 0
    for game in games:
        id = get_id(game)
        if id:
            app_ids.append(id)
            counter += 1
            if counter > 49:
                app_ids.append('limit')
                counter = 0
    
    q = ','.join(app_ids)
    splits = q.split(',limit')

    for item in splits:
        tup = get_price(item)
        highest += tup[0]
        lowest += tup[1]

    return f"Number of games in Playnite library: {len(games)}\nNumber of games identified by Steam: {len(app_ids)}\nMaximum value of library: ${round(highest, 2)}\nMinimum value of library: ${round(lowest, 2)}\n\nTime taken to execute: {round(time.time() - start_time, 3)}s"            


def get_price(id):
    base_url = 'http://store.steampowered.com/api/appdetails'

    params = {
            'appids': id,
            'cc': 'us',
            'filters': 'price_overview'
        }

    response = requests.get(base_url, params=params)

    high, low = 0, 0
    if response.status_code == 200:
        data = response.json()
        for item in data:
            item = data[item]
            if item['success'] == True and len(item['data']) > 0:
                item = item['data']
                high += item['price_overview']['initial'] / 100
                low += item['price_overview']['final'] / 100
    
    return high, low


def get_apps():
    base_url = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'

    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()['applist']['apps']
        for name in data:
            name['name'] = pattern.sub('', name['name']).lower()

        return data
    
    return None


def get_id(name):
    for app in apps:
        if name == app['name']:
            return str(app['appid'])
    return None
      