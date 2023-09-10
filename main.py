<<<<<<< HEAD
import telebot
import requests
import json
import telegram

from telebot import types
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
=======

import datetime
import json
from datetime import datetime

import requests
import telebot
from telebot import types
>>>>>>> c49539c (Initial commit)


bot = telebot.TeleBot('5946513884:AAGkl2MPaJ5sK0BRYsbWkY6PV23JJBF1-aU')
API = '709e3cbe105d05f7bfdb27403929d3bc'

# переводчик
weather_mapping = {
    'clear sky': 'ясно',
    'few clouds': 'малооблачно',
    'scattered clouds': 'рассеянные облака',
    'overcast clouds': 'затянуто облаками',
    'broken clouds': 'облачно',
    'shower rain': 'ливень',
    'rain': 'дождь',
    'thunderstorm': 'гроза',
    'snow': 'снег',
    'mist': 'туман',
    'haze': 'лёгкий туман',
    'light rain': 'небольшой дождь',
    'light intensity shower rain': 'ливень с интенсивностью света',
    'fog': 'туман',
<<<<<<< HEAD

}


=======
    'heavy intensity rain': 'сильный дождь',

}

city_weather_data = {}
>>>>>>> c49539c (Initial commit)

# начало
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Какого города вы хотите узнать погоду?')

<<<<<<< HEAD
@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip().lower()
=======

# хранилище городов
last_city = ""


@bot.message_handler(func=lambda message: message.text.lower() == "завтра")
def get_weather_tomorrow(message):
    global last_city

    # погода завтра
    if last_city:
        res = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={last_city}&appid={API}&units=metric')

        if res.status_code == 200:
            data = json.loads(res.text)
            # погода через 24 часа (по 3 часа)
            tomorrow_weather = data["list"][8]
            temp = tomorrow_weather["main"]["temp"]
            feels_like = tomorrow_weather["main"]["feels_like"]
            weather_description_en = tomorrow_weather["weather"][0]["description"]
            pressure = tomorrow_weather["main"]["pressure"]
            wind_speed = tomorrow_weather["wind"]["speed"]
            humidity = tomorrow_weather["main"]["humidity"]

            # перевод слов
            weather_description_ru = weather_mapping.get(weather_description_en, weather_description_en)

            # сообщение о погоде на завтра
            weather_info = (f'🌤️Погода на завтра в {last_city.capitalize()}: {weather_description_ru}\n'
                            f'🌡️Температура: {temp}°C\n'
                            f'🤲Ощущается как: {feels_like}°C\n'
                            f'💧Влажность: {humidity}%\n'
                            f'🎈Давление: {pressure} мбар\n'
                            f'🍃Скорость ветра: {wind_speed} м/с')

            bot.reply_to(message, weather_info)
        else:
            bot.reply_to(message, f'Не удалось получить погоду для {last_city}... 🥺')
    else:
        bot.reply_to(message, 'Вы еще не указали город. Пожалуйста, укажите город после команды /погода.')


@bot.message_handler(content_types=['text'])
def get_weather(message):
    global last_city
    city = message.text.strip().lower()
    last_city = city  # последний город
>>>>>>> c49539c (Initial commit)
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        weather_description_en = data["weather"][0]["description"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        humidity = data["main"]["humidity"]

<<<<<<< HEAD
        weather_description_ru = weather_mapping.get(weather_description_en, weather_description_en)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Погода на завтра', ))
=======
        # перевод слов
        weather_description_ru = weather_mapping.get(weather_description_en, weather_description_en)

        # кнопки для сообщений погоды на завтра
>>>>>>> c49539c (Initial commit)

        # сообщение о погоде
        weather_info = (f'🌤️Сейчас погода: {weather_description_ru}\n'
                        f'🌡️Температура: {temp}°C\n'
                        f'🤲Ощущается как: {feels_like}°C\n'
                        f'💧Влажность: {humidity}%\n'
                        f'🎈Давление: {pressure} мбар\n'
                        f'🍃Скорость ветра: {wind_speed} м/с')
<<<<<<< HEAD


=======
>>>>>>> c49539c (Initial commit)
        image = 'sun.png' if temp > 15.0 else 'cloud.png'
        with open(image, 'rb') as file:
            bot.send_photo(message.chat.id, file, caption=weather_info)
    else:
        bot.reply_to(message, f'Город указан неверно или я такой не знаю... 🥺')

<<<<<<< HEAD
=======

>>>>>>> c49539c (Initial commit)
# чтобы бот не останавливался
bot.polling(none_stop=True)
