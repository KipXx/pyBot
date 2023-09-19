import json
import requests
import telebot
import datetime
import time


class WeatherBot:
    def __init__(self, bot_token, openweathermap_api_key):
        self.bot = telebot.TeleBot(bot_token)
        self.API = openweathermap_api_key

        # перевод
        with open('weather_data.json', 'r', encoding='utf-8') as json_file:
            self.weather_mapping = json.load(json_file)

        self.city_weather_data = {}
        self.last_city = None
        self.scheduled_message = None

        # Словарь для отслеживания подключенных пользователей и состояния их рассылки
        self.subscribed_users = {}

        # Атрибут для отслеживания состояния рассылки
        self.sending_weather = False

        # Инициализируем клавиатуру для кнопок
        self.markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.markup.add(telebot.types.KeyboardButton("Присылать каждый час"))
        # self.markup.add(telebot.types.KeyboardButton("Стоп"))
        self.markup.add(telebot.types.KeyboardButton("Погода на 3 дня"))
        self.markup.add(telebot.types.KeyboardButton("Завтра"))

        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.bot.send_message(message.chat.id, "Привет! Я бот погоды. Чтобы узнать погоду, просто напиши название города.")

        @self.bot.message_handler(func=lambda message: message.text.lower() == "завтра")
        def get_weather_tomorrow(message):
            if self.last_city:
                tomorrow_weather_info = self.get_weather_for_date(self.last_city,
                                                                  datetime.datetime.now() + datetime.timedelta(days=1))
                if tomorrow_weather_info:
                    self.bot.send_message(message.chat.id, tomorrow_weather_info, reply_markup=self.markup)
                else:
                    self.bot.send_message(message.chat.id,
                                          f'Не удалось получить прогноз погоды на завтра для {self.last_city}... 🥺')
            else:
                self.bot.send_message(message.chat.id, 'Вы еще не указали город. Сначала укажите город.')

        # погода на 3 дня
        @self.bot.message_handler(func=lambda message: message.text.lower() == "погода на 3 дня")
        def get_weather_three_days(message):
            if self.last_city:
                city = self.last_city
                current_date = datetime.datetime.now()
                tomorrow_date = current_date + datetime.timedelta(days=1)
                day_after_tomorrow_date = current_date + datetime.timedelta(days=2)
                third_day_date = current_date + datetime.timedelta(days=3)

                tomorrow_weather_info = self.get_weather_for_date(city, tomorrow_date)
                day_after_tomorrow_weather_info = self.get_weather_for_date(city, day_after_tomorrow_date)
                third_day_weather_info = self.get_weather_for_date(city, third_day_date)

                if tomorrow_weather_info and day_after_tomorrow_weather_info and third_day_weather_info:
                    weather_info = (f'🏙️Погода в {city.capitalize()}:\n\n'
                                    f'📅Завтра:\n'
                                    f'{tomorrow_weather_info}\n\n'
                                    f'📅Послезавтра:\n'
                                    f'{day_after_tomorrow_weather_info}\n\n'
                                    f'📅Через 3 дня:\n'
                                    f'{third_day_weather_info}\n')

                    self.bot.send_message(message.chat.id, weather_info, reply_markup=self.markup)
                else:
                    self.bot.send_message(message.chat.id,
                                          f'Не удалось получить прогноз погоды на 3 дня для {city}... 🥺')
            else:
                self.bot.send_message(message.chat.id, 'Вы еще не указали город. Пожалуйста, укажите город.')

        # рассылка каждый час1
        @self.bot.message_handler(func=lambda message: True)
        def handle_city(message):
            if message.text.lower() == "стоп":
                if self.sending_weather:
                    self.sending_weather = False
                    if message.chat.id in self.subscribed_users:
                        self.subscribed_users[message.chat.id] = False
                    # клава
                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add(telebot.types.KeyboardButton("Присылать каждый час"))
                    markup.add(telebot.types.KeyboardButton("Погода на 3 дня"))
                    markup.add(telebot.types.KeyboardButton("Завтра"))
                    self.bot.send_message(message.chat.id, "Рассылка погоды остановлена.", reply_markup=markup)
                else:
                    self.bot.send_message(message.chat.id, "Рассылка погоды уже остановлена.")
            elif message.text.lower() == "присылать каждый час":
                if self.sending_weather:
                    self.bot.send_message(message.chat.id, "Рассылка уже запущена!")
                else:
                    self.sending_weather = True
                    # Уберите клавиатуру с кнопкой "Присылать каждый час" и добавьте кнопку "Стоп"
                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add(telebot.types.KeyboardButton("Стоп"))
                    markup.add(telebot.types.KeyboardButton("Погода на 3 дня"))
                    markup.add(telebot.types.KeyboardButton("Завтра"))
                    self.bot.send_message(message.chat.id,
                                          "Рассылка погоды запущена. Погода будет присылаться каждый час.",
                                          reply_markup=markup)
                    self.subscribed_users[message.chat.id] = True
                    self.send_weather_periodically(message.chat.id)
            else:
                self.last_city = message.text.lower()
                self.send_weather(message.chat.id, self.last_city)

    # общая погда (на сегодня)
    def get_weather_for_date(self, city, date):
        res = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.API}&units=metric')

        if res.status_code == 200:
            data = json.loads(res.text)

            for weather_data in data["list"]:
                forecast_datetime = datetime.datetime.utcfromtimestamp(weather_data["dt"])

                if forecast_datetime.date() == date.date():
                    weather_description_en = weather_data["weather"][0]["description"]
                    weather_description_ru = self.weather_mapping.get(weather_description_en, weather_description_en)
                    temp = weather_data["main"]["temp"]
                    feels_like = weather_data["main"]["feels_like"]
                    humidity = weather_data["main"]["humidity"]
                    pressure = weather_data["main"]["pressure"]
                    wind_speed = weather_data["wind"]["speed"]

                    weather_info = (f'🌤️ Погода: {weather_description_ru}\n'
                                    f'🌡️ Температура: {temp}°C\n'
                                    f'🤲 Ощущается как: {feels_like}°C\n'
                                    f'💧 Влажность: {humidity}%\n'
                                    f'🎈 Давление: {pressure} мбар\n'
                                    f'🍃 Скорость ветра: {wind_speed} м/с')
                    return weather_info
        return None

    # скан
    def send_weather(self, chat_id, city):
        weather_info = self.get_weather_for_date(city, datetime.datetime.now())
        if weather_info:
            self.bot.send_message(chat_id, weather_info, reply_markup=self.markup)
        else:
            self.bot.send_message(chat_id, f'Не удалось получить погоду для {city}... 🥺')

    # таймер на час
    def send_weather_periodically(self, chat_id):
        while self.sending_weather:
            if self.last_city:
                self.send_weather(chat_id, self.last_city)
            time.sleep(3600)

    # запуск бота
    def start_bot(self):
        self.bot.polling(none_stop=True)


if __name__ == "__main__":
    token = '5946513884:AAGkl2MPaJ5sK0BRYsbWkY6PV23JJBF1-aU'
    api_key = '709e3cbe105d05f7bfdb27403929d3bc'
    bot = WeatherBot(token, api_key)
    bot.start_bot()
