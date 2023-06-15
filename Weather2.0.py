from env import TOKEN
from enw import API_KEY
from ent import IAM
from schema import Root
import requests
import time
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import random
import logging
from aiogram.types import Message
from pprint import pprint
# Загружаем переменные окружения
load_dotenv()

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Время кэширования данных о погоде (в секундах)
CACHE_TIME = 300

# Словарь для кэширования данных о погоде
weather_cache = {}


# Обработчик команды /start
@dp.message_handler(commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    await message.reply("Привет! Я бот, который может сообщить тебе погоду в любом городе. Просто напиши мне название города.")
    await state.set_state("ask_city")

# Обработчик сообщений с текстом
@dp.message_handler(state="ask_city")
async def _(message: types.Message, state: FSMContext):
    # Получаем название города из сообщения пользователя
     city_name = message.text

    # Формирование URL API для API погоды
     api_url = f'https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city_name}&lang=ru'
     api_url = f'https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city_name}&lang=ru'

    # Отправка запроса к API погоды
     response = requests.get(api_url)
        

    # Проверка успешности запроса
     if response.status_code == 200:
        # Разбор JSON-ответа
          data = response.json()
          root = Root.from_dict(data)
          pprint(data)
        # Получение температуры и описания погоды из ответа
          temperature = data['current']['temp_c']
          weather_description = data['current']['condition']['text']
          temperaturefeel = data['current']['feelslike_c']
          windspdfalse = data['current']['wind_kph']
          winddir =data['current']['wind_dir']
          windspdtrue = windspdfalse * 5/18
          localtm = data['location']['localtime']
          humidityy =data['current']['humidity']
          pressure =data['current']['pressure_mb']

          sunrisee = []
          sunsett = []
          rainchance = []

          for estimation in data['forecast']['forecastday']:
               sunrisee.append(estimation['astro']['sunrise'])
               sunsett.append(estimation['astro']['sunset'])
               rainchance.append(estimation['day']['daily_chance_of_rain'])


        # Определение соответствующей рекомендации по одежде на основе температуры
          if temperature < 10:
               clothing_recommendation = 'Сейчас очень холодно, поэтому Вы должны надеть теплую куртку, перчатки и шапку.'
          elif temperature < 20:
               clothing_recommendation = 'Сейчас прохладно, поэтому Вы можете надеть легкую куртку или свитер.'
          else:
               clothing_recommendation = 'Сейчас тепло, поэтому Вы можете надеть футболку и шорты.'

        # Отправка сообщения пользователю с температурой, описанием погоды и рекомендацией по одежде
          await message.reply(f"Местное время: {localtm}\n"
               f"Погода в городе: {city_name}\nТемпература: {temperature}C°\n"
               f"Влажность: {humidityy}%\nДавление: {pressure} мм.рт.ст\nВетер: {windspdtrue:.2f} м/с\nНапраление ветра: {winddir}\n"
               f"Восход солнца {sunrisee}: \nЗакат солнца {sunsett}: \nВероятность осадков: {rainchance}%\n"
               f"{clothing_recommendation}"
               f"Хорошего дня!"
               )
     else:
        # Отправка сообщения об ошибке пользователю, если запрос был неудачным
          await message.reply('Извините, я не смог получить информацию о погоде для этого города. Пожалуйста, попробуйте еще раз позже.')





# MUST BE AFTER ALL COMMANDS
@dp.message_handler(Text(startswith="/"))
async def _(message: types.Message, state: FSMContext):
     await message.reply("Такой команды не существует, попробуй снова")
# Запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)