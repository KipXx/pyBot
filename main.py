
import json

import requests
import telebot
from telebot import types


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
    'heavy intensity rain': 'сильный дождь',
}

city_weather_data = {}


# начало
last_city = ""


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот погоды. Чтобы узнать погоду, просто напиши название города.")


@bot.message_handler(func=lambda message: message.text.lower() == "завтра")
def get_weather_tomorrow(message):
    global last_city
    # завтра
    if last_city:
        res = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={last_city}&appid={API}&units=metric')

        if res.status_code == 200:
            data = json.loads(res.text)
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
        bot.reply_to(message, 'Вы еще не указали город. Пожалуйста, укажите город.')


@bot.message_handler(content_types=['text'])
def get_weather(message):
    global last_city
    city = message.text.strip().lower()
    last_city = city

    # виртуальная клавиатура "завтра"
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("Завтра"))

    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        weather_description_en = data["weather"][0]["description"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        humidity = data["main"]["humidity"]

        # перевод слов
        weather_description_ru = weather_mapping.get(weather_description_en, weather_description_en)

        # сообщение о погоде
        weather_info = (f'🌤️Сейчас погода: {weather_description_ru}\n'
                        f'🌡️Температура: {temp}°C\n'
                        f'🤲Ощущается как: {feels_like}°C\n'
                        f'💧Влажность: {humidity}%\n'
                        f'🎈Давление: {pressure} мбар\n'
                        f'🍃Скорость ветра: {wind_speed} м/с')

        image = 'sun.png' if temp > 15.0 else 'cloud.png'
        with open(image, 'rb') as file:
            bot.send_photo(message.chat.id, file, caption=weather_info, reply_markup=markup)
    else:
        bot.reply_to(message, f'Город указан неверно или я такой не знаю... 🥺')


# чтобы бот не останавливался
bot.polling(none_stop=True)
