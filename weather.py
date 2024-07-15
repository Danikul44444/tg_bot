import datetime
import requests
import json
from datetime import  timedelta
def calculate_real_time(timezone_offset):
    current_time = datetime.datetime.now(datetime.UTC)
    target_time = current_time + timedelta(seconds=timezone_offset)

    return f"({target_time.hour:02d}:{target_time.minute:02d}:{target_time.second:02d}) {target_time.day:02d}/{target_time.month:02d}/{target_time.year:04d}"

def get_wind_direction(degrees):
    directions = ["Северное", "Северо-восток", "Восток", "Юго-восток", "Юг", "Юго-запад", "Запад", "Серево-запад"]
    index = round((degrees + 22.5) / 45) % 8
    return directions[index]

with open('settings.json', 'r', encoding='utf-8') as f:
    bot_file = json.load(f)

def check_city(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={bot_file["WEATHER_TOKEN"]}'
    respo = requests.get(url)
    if respo.ok:
        return True
    else:
        return False



def weather_city(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={bot_file["WEATHER_TOKEN"]}'
    respo = requests.get(url)
    if respo.ok:
        json_list = respo.json()
        city = json_list['name']
        temp = int(json_list['main']['temp'])
        if temp > 0:
            temp = f'+{temp}'
        time = calculate_real_time(json_list['timezone'])
        wind_speed = json_list['wind']['speed']
        wind = get_wind_direction(json_list['wind']['deg'])
        return f'🏙Город: {city}\n🌡️Температура: {temp}°C\n🌬️Ветер: {wind_speed}м/c, {wind}\n⏰Время: {time}\n'
    else:
        return False

