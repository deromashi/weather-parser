import requests
import fake_useragent
from bs4 import BeautifulSoup
import random
import csv
import os
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


session = requests.Session()
def weather_now(url):
    weather = None
    while weather == None:
        headers = {'user-agent': fake_useragent.UserAgent().random}
        text = []
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        weather = soup.find('section', class_='section section-content section-bottom-shadow')

    # Time and date
    data = weather.find('div', class_='now-localdate').text
    text.extend(data + '\n')

    # Temperature
    temp = weather.find('div', class_='now-weather').find('temperature-value').get('value')
    text.extend(f'Температура: {temp}°' + '\n')

    # Feeling temperature
    feel = weather.find('div', class_='now-feel').find('temperature-value').get('value')
    text.extend(f'По ощущению: {feel}°' + '\n')

    # Weather
    desc = weather.find('div', class_='now-desc').text
    text.extend(desc + '\n')

    # Other info
    info = weather.find('div', class_ = 'now-info').find_all('div', class_='now-info-item')
    text.extend('\n')

    # Wind
    wind = info[0].find(class_='item-information')
    wind_value = wind.find('speed-value').get('value')
    wind_direction = wind.text
    text.extend(f'Ветер: {wind_value} м/с ({wind_direction})' + '\n')

    # Pressure
    pressure = info[1].find(class_='item-information')
    pressure_value = pressure.find('pressure-value').get('value')
    text.extend(f'Давление: {pressure_value} мм рт. ст.' + '\n')

    # Humidity
    humidity = info[2].find(class_='item-information')
    humidity_value = humidity.find( class_='item-value').text
    text.extend(f'Влажность: {humidity_value} %' + '\n')

    # Geomagnetic field (gf)
    gf = info[4].find(class_='item-information')
    gf_value = gf.find(class_="item-value").text
    text.extend(f'Г/м: {gf_value} балла из 9'+'\n')

    # Water
    water = info[5].find(class_='item-information')
    water_value = water.find('temperature-value').get('value')
    text.extend(f'Вода: {water_value}°' + '\n')
    print(''.join(text))
    return 0

def weather(url):

    way = url.split('/')[-2]
    if way == 'now':
        weather_now(url)
        return 0
    elif way == '3-days' or way == 'weekend':
        weather_three_days(url)
        return 0
    elif way == 'month':
        weather_month(url)
        return 0

    block = None
    while block == None:
        headers = {'user-agent': fake_useragent.UserAgent().random}
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        block = soup.find('div', class_='widget-body')

    # Time

    if 'weather' in way or way == 'tomorrow':
        times = ['0:00', '3:00', '6:00', '9:00', '12:00', '15:00', '18:00', '21:00']
    elif way == '10-days' or way == '2-weeks':
        date_block = block.find('div', class_='widget-row widget-row-date')
        times = [i.find(class_='day').text + ', ' + i.find(class_='date').text for i in date_block.find_all('a')]
        print(times)
    else:
        print('Неизвестная ссылка')
        return 0

    # Weather
    weather_block = block.find('div', class_='widget-row widget-row-icon is-important')
    weather = [i.get('data-tooltip') for i in weather_block.find_all('div', class_='row-item')]

    # Temperature
    temperature_block = block.find('div', class_='widget-row widget-row-chart widget-row-chart-temperature-air row-with-caption')
    temperature = [i.get('value') for i in temperature_block.find(class_='values').find_all('temperature-value')]

    # Wind
    wind_block = block.find('div', class_='widget-row widget-row-wind row-wind row-with-caption')
    wind_speed = []
    wind_speed_description = []
    wind_direction = []
    wind_gust = []
    wind_gust_description = []

    for j in wind_block.find_all('div', class_='row-item'):
        speed = j.find_all('div')[0]
        wind_speed_description.append(speed.get('data-tooltip'))
        wind_speed.append(speed.find('speed-value').get('value'))
        wind_direction.append(speed.find(class_='wind-direction').text)
        try:
            gust = j.find_all('div')[3]
            wind_gust_description.append(gust.get('data-tooltip'))
            wind_gust.append(gust.find('speed-value').get('value'))
        except:
            wind_gust_description.append(None)
            wind_gust.append(None)

    wind = [[wind_speed[i], wind_direction[i],wind_speed_description[i], wind_gust[i], wind_gust_description[i]] for i in range(len(wind_speed))]

    # Rainfall
    rainfall_block = block.find('div', attrs={'data-row' :'precipitation-bars'})
    rainfall = [i.text for i in rainfall_block.find_all('div', class_='row-item')]

    for i in range(len(times)):
        print(f'{(times[i]+':').ljust(max(map(len, times))+1)} {temperature[i].rjust(3)}°C {weather[i].ljust(max(map(len, weather)))} {wind[i][0]} м/с ({wind[i][1].ljust(2)})  {rainfall[i]} мм')

def weather_three_days(url): # three days and weekends
    block = None
    while block == None:
        headers = {'user-agent': fake_useragent.UserAgent().random}
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        block = soup.find('div', class_='widget-items js-scroll-item')

    # Date
    date_block = block.find('div', class_='widget-row widget-row-tod-date')
    date = [i.text for i in date_block.find_all('a')][:3]

    # DataTime
    datatime = ["Ночь", "Утро", "День", "Вечер"]

    # Weather
    weather_block = block.find('div', class_='widget-row widget-row-icon is-important')
    weather = [[i.get('data-tooltip') for i in weather_block.find_all('div', class_='row-item')[j*4:j*4+4]] for j in range(3)]
     # Сгруппированы по четыре

    # Temperature
    temp_block = block.find('div', class_='values')
    temp = [[i.find('temperature-value').get('value') for i in temp_block.find_all('div', class_='value')[j*4:j*4+4]] for j in range(3)]

    # Wind
    wind_block = block.find('div', class_='widget-row widget-row-wind row-wind row-with-caption')
    wind_speed = []
    wind_speed_description = []
    wind_direction = []
    wind_gust = []
    wind_gust_description = []

    for j in wind_block.find_all('div', class_='row-item'):
        speed = j.find_all('div')[0]
        wind_speed_description.append(speed.get('data-tooltip'))
        wind_speed.append(speed.find('speed-value').get('value'))
        wind_direction.append(speed.find(class_='wind-direction').text)
        try:
            gust = j.find_all('div')[3]
            wind_gust_description.append(gust.get('data-tooltip'))
            wind_gust.append(gust.find('speed-value').get('value'))
        except:
            wind_gust_description.append(None)
            wind_gust.append(None)

    wind = [[[wind_speed[i], wind_direction[i], wind_speed_description[i], wind_gust[i], wind_gust_description[i]] for i in range(j*4, j*4+4)] for j in range(3)]

    # Rainfall
    rainfall_block = block.find('div', attrs={'data-row': 'precipitation-bars'})
    rainfall = [[i.text for i in rainfall_block.find_all('div', class_='row-item')[j*4:j*4+4]] for j in range(3)]

    for i in range(3):
        print(date[i])
        for j in range(4):
            print(f'{(datatime[j]+':').ljust(6)} {temp[i][j]} °C {weather[i][j].ljust(max(map(len, weather[i])))} {wind[i][j][0].rjust(3)} м/с ({wind[i][j][2]}) {rainfall[i][j]} мм')
        print()

def weather_month(url):
    block = None
    while block == None:
        headers = {'user-agent': fake_useragent.UserAgent().random}
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        block = soup.find('div', class_='widget-body')

    date = []
    weather = []
    temp_max = []
    temp_min = []

    for day in block.find_all('a', class_='row-item row-item-month-date'):
        date.append(day.find('div', class_='date').text)
        weather.append(day.get('data-tooltip'))
        temp_max.append(day.find('div', class_='maxt').find('temperature-value').get('value'))
        temp_min.append(day.find('div', class_='mint').find('temperature-value').get('value'))

    if date == []:
        weather_month(url)
    for i in range(len(date)):
        print(f'{(date[i] + ':').ljust(max(map(len, date))+1)} {weather[i].ljust(max(map(len, weather)))} {temp_max[i]}°C ({temp_min[i]}°C)')

def update_this_country(country_url, country):
    url = 'https://www.gismeteo.ru'
    regions, name = get_urls(url + country_url)

    with open(f'countries/{country}.csv', mode='w', encoding='utf-8') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',', lineterminator='\r')
        file_writer.writerow(['Страна','Регион', 'Район', 'Населенный пункт', 'URL'])
        if country == 'Россия':
            file_writer.writerow(['Россия', 'Москва (город федерального значения)', '-', 'Москва', '/weather-moscow-4368/'])

        # Only cities
        if name == 'Пункты':
            settlements = regions
            for settlement in settlements:
                file_writer.writerow([country,'-', '-', settlement[0].strip(), settlement[1]])

        # Districts and cities
        elif name == 'Районы':
            for district in regions:
                settlements, name = get_urls(url + district[1])
                if not (settlements):
                    print(f"Район '{district[0].split()}' пропущен")
                    continue
                for settlement in settlements:
                    file_writer.writerow([country, '-', district[0].strip(), settlement[0].strip(), settlement[1]])

        # Regions, districts and cities
        else:
            for region in regions:
                print(region[0])
                districts, name = get_urls(url + region[1])
                if not (districts):
                    print(f'Регион "{region[0].strip()}" пропущен')
                    continue

                # Cities without district
                if name == 'Пункты':
                    settlements = districts
                    for settlement in settlements:
                        file_writer.writerow([country, region[0].strip(), '-', settlement[0].strip(), settlement[1]])
                    continue

                # All names
                for district in districts:
                    settlements, name = get_urls(url + district[1])
                    if not (settlements):
                        print(f"Район '{district[0].strip()}' пропущен")
                        continue
                    for settlement in settlements:
                        file_writer.writerow([country, region[0].strip(), district[0].strip(), settlement[0].strip(), settlement[1]])

def update_world_urls():
    url = 'https://www.gismeteo.ru'
    worldwide, name = get_urls(url + '/catalog')
    with open('worldwide.csv', mode='w', encoding='utf-8') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',', lineterminator='\r')
        file_writer.writerow(['Страна', 'URL'])
        file_writer.writerows(worldwide)

    with open('worldwide.csv', mode='r', encoding='utf-8') as csvfile:
        file_reader = csv.reader(csvfile)
        countries = list(file_reader)[168:169] #[1:]
        for country in countries:
            country_name = country[0].strip()
            print('-' * 10 + country_name + '-' * 10)
            country_url = country[1].strip()
            update_this_country(country_url, country_name)

    connect_world_urls()

def get_urls(url):
    catalog = None
    attempt = 1
    while catalog == None and attempt <= 5:
        if attempt > 1:
            time.sleep(0.5)
            headers = {'user-agent': fake_useragent.UserAgent().random}
            print('-')
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36'}
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        catalog = soup.find_all('section', class_='catalog-body')
        if len(catalog) == 2:
            catalog = catalog[1]
        elif len(catalog) == 1:
            catalog = catalog[0]
        else:
            catalog = None
        attempt += 1
    if catalog == None:
        return None, None
    name = catalog.find('div', class_='catalog-subtitle').text
    groups = [[i.text.strip(), i.get('href')] for i in catalog.find_all('a')]
    return groups, name

def connect_world_urls():
    with open('worldwide.csv', mode='r', encoding='utf-8') as csvfile:
        worldwide = csv.reader(csvfile)
        countries = list(worldwide)[1:]
        with open('countries/World.csv', mode='w', encoding='utf-8') as csvfile:
            file_writer = csv.writer(csvfile, delimiter=',', lineterminator='\r')
            for country in countries:
                with open(f'countries/{country[0].strip()}.csv', mode='r', encoding='utf-8') as csvfile:
                    file_reader = csv.reader(csvfile)
                    spisok = list(file_reader)[1:]
                file_writer.writerows(spisok)

def show():
    with open('countries/World.csv', mode='r', encoding='utf-8') as csvfile:

        # Introduce
        print('Приветствую Вас в моем мини-приложении')
        print('Для выхода - при выборе города введите 0')

        url = 'https://www.gismeteo.ru'
        file_reader = csv.reader(csvfile)
        folder_dict = {}

        for row in file_reader:
            if row[1] == '-':
                if row[2] == '-':
                    point = f'{row[0]}'
                else:
                    point = f'{row[2]}, {row[0]}'
            else:
                if row[2] == '-':
                    point = f'{row[1]}, {row[0]}'
                else:
                    point = f'{row[2]}, {row[1]}, {row[0]}'

            if row[3].strip().lower() not in folder_dict:
                folder_dict[row[3].strip().lower()] = [{point :row[4]}]
            else:
                folder_dict[row[3].strip().lower()].append({point :row[4]})

        while True:
            name = input('Введите город: ').lower()

            if name == '0':
                break
            elif name not in folder_dict:
                print('Неверно написан город')
                continue
            elif len(folder_dict[name]) == 1:
                sub_url = list(folder_dict[name][0].values())[0]
                # print(sub_url)
                # print(*weather_now(url + sub_url+'now', headers), sep='')
            else:
                choose = {}
                for i in range(len(folder_dict[name])):
                    choose[i] = list(folder_dict[name][i].values())[0]
                    print(f'{i+1} - {list(folder_dict[name][i].keys())[0]}')
                print()
                while True:
                    try:
                        n = int(input('Выберете нужный: ').strip())-1
                    except ValueError:
                        print('Ты совершил большую ошибку')
                        continue
                    if 0 <= n < len(choose):
                        # print(choose[n])
                        sub_url = choose[n]
                        # print(*weather_now(url + choose[n] + 'now', headers), sep ='')
                        break
                    else:
                        print('Неверный выбор, дружок')
            print()
            print('Выберете интересующее вас время')
            urls = {1: 'now/', 2: '', 3: 'tomorrow/', 4: '3-days/', 5: 'weekend/', 6: '10-days/', 7: '2-weeks/', 8: 'month/'}
            names = {1: 'Сейчас', 2: 'Сегодня', 3: 'Завтра', 4: '3 дня', 5: "Выходные", 6: "10 дней", 7: "2 недели", 8: "Месяц"}
            for i in range(1, len(names)+1):
                print(f'{i} - {names[i]}')
            while True:
                try:
                    n = int(input('Выберете нужный: ').strip())
                except ValueError:
                    print('Ты совершил большую ошибку')
                    continue
                if 1 <= n <= len(names):
                    # print(choose[n])
                    sub_url = sub_url + urls[n]
                    # print(*weather_now(url + choose[n] + 'now', headers), sep ='')
                    break
                else:
                    print('Неверный выбор, дружок')
            weather(url + sub_url)
            print('\n')

show()