import json
import requests
import telebot
import datetime
import time
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
last_city = None
scheduled_message = None
sending_weather = False

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот погоды. Чтобы узнать погоду, просто напиши название города.")


def get_weather_for_date(city, date):
    res = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        # найти прогноз погоды (3 часа)
        for item in data["list"]:
            item_datetime = datetime.datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
            if item_datetime.date() == date.date():
                return item
    return None


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
        bot.reply_to(message, 'Вы еще не указали город. Сначала укажите город.')


@bot.message_handler(func=lambda message: message.text.lower() == "погода на 3 дня")
def get_weather_three_days(message):
    global last_city  # хранение города

    # если есть город в хранилище то выполняется
    if last_city:
        city = last_city
        current_date = datetime.datetime.now()
        tomorrow_date = current_date + datetime.timedelta(days=1)
        day_after_tomorrow_date = current_date + datetime.timedelta(days=2)
        third_day_date = current_date + datetime.timedelta(days=3)

        # погода 3 дней
        tomorrow_weather = get_weather_for_date(city, tomorrow_date)
        day_after_tomorrow_weather = get_weather_for_date(city, day_after_tomorrow_date)
        third_day_weather = get_weather_for_date(city, third_day_date)

        if tomorrow_weather and day_after_tomorrow_weather and third_day_weather:
            temp_tomorrow = tomorrow_weather["main"]["temp"]
            temp_day_after_tomorrow = day_after_tomorrow_weather["main"]["temp"]
            temp_third_day = third_day_weather["main"]["temp"]
            weather_description_en_tomorrow = tomorrow_weather["weather"][0]["description"]
            weather_description_en_day_after_tomorrow = day_after_tomorrow_weather["weather"][0]["description"]
            weather_description_en_third_day = third_day_weather["weather"][0]["description"]

            # перевод слов
            weather_description_ru_tomorrow = weather_mapping.get(weather_description_en_tomorrow, weather_description_en_tomorrow)
            weather_description_ru_day_a_tomorrow = weather_mapping.get(weather_description_en_day_after_tomorrow, weather_description_en_day_after_tomorrow)
            weather_description_ru_3_day = weather_mapping.get(weather_description_en_third_day, weather_description_en_third_day)

            # сообщение о погоде
            weather_info = (f'🏙️Погода в {city.capitalize()}:\n\n'
                            f'📅 Завтра:\n'
                            f'🌤️Погода: {weather_description_ru_tomorrow}\n'
                            f'🌡️Температура: {temp_tomorrow}°C\n\n'
                            f'📅 Послезавтра:\n'
                            f'🌤️Погода: {weather_description_ru_day_a_tomorrow}\n'
                            f'🌡️Температура: {temp_day_after_tomorrow}°C\n\n'
                            f'📅 Через 3 дня:\n'
                            f'🌤️Погоды: {weather_description_ru_3_day}\n'
                            f'🌡️Температура: {temp_third_day}°C\n')

            bot.reply_to(message, weather_info)
        else:
            bot.reply_to(message, f'Не удалось получить погоду для {city}... 🥺')
    else:
        bot.reply_to(message, 'Вы еще не указали город. Пожалуйста, укажите город.')


# клавиатура над чатом
markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(telebot.types.KeyboardButton("Присылать каждый час"))
markup.add(telebot.types.KeyboardButton("Стоп"))
markup.add(telebot.types.KeyboardButton("Погода на 3 дня"))
markup.add(telebot.types.KeyboardButton("Завтра"))

# рассылка погодывп
@bot.message_handler(content_types=['text'])
def get_weather(message):
    global last_city, scheduled_message, sending_weather

    if message.text == "Присылать каждый час":
        if sending_weather:
            bot.send_message(message.chat.id, "Рассылка уже активна.")
        else:
            sending_weather = True
            last_city = None
            scheduled_message = bot.send_message(message.chat.id, "Информация о погоде будет приходить каждый час. Нажмите 'Стоп', чтобы остановить.")
            send_weather_periodically(message.chat.id)
    elif message.text == "Стоп":
        if sending_weather:
            sending_weather = False
            last_city = None
            bot.send_message(message.chat.id, "Рассылка остановлена. Нажмите 'Присылать каждый час', чтобы возобновить.", reply_markup=markup)
            if scheduled_message:
                bot.delete_message(message.chat.id, scheduled_message.message_id)
        else:
            bot.send_message(message.chat.id, "Рассылка уже остановлена...")
    else:
        last_city = message.text.strip().lower()  # город последний
        send_weather(message.chat.id)


def send_weather(chat_id):
    global last_city
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={last_city}&appid={API}&units=metric')
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
            bot.send_photo(chat_id, file, caption=weather_info, reply_markup=markup)
    else:
        bot.send_message(chat_id, f'Город указан неверно или я такой не знаю... 🥺')


def send_weather_periodically(chat_id):
    while sending_weather:
        if last_city:
            send_weather(chat_id)
        time.sleep(3600)  # таймер 1 часпа


if __name__ == "__main__":
    bot.polling(none_stop=True)


# чтобы бот не останавливался
bot.polling(none_stop=True)
