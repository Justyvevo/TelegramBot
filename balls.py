import requests
from env import TOKEN
from enw import API_KEY
import time
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import random
import logging
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import schedule
from pprint import pprint
from schema import Root
import requests
import asyncio
# Загружаем переменные окружения
load_dotenv()

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Время кэширования данных о погоде (в секундах)
CACHE_TIME = 300

# Словарь для кэширования данных о погоде
weather_cache = {}

# Клавиатура с кнопкой для включения отправки уведомлений







# Обработчик команды /start
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Включить уведомления о погоде'))

# Флаг, определяющий, включены ли уведомления
notifications_enabled = False

# Обработчик команды /start
@dp.message_handler(commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    await message.reply("Привет! Я бот, который может сообщить тебе погоду в любом городе. Просто напиши мне название города.")
    # Проверяем состояние флага уведомлений и устанавливаем соответствующую клавиатуру
    if notifications_enabled:
        keyboard = start_keyboard.remove('Включить уведомления о погоде')
    else:
        keyboard = start_keyboard
    await message.reply("Чтобы включить уведомления о погоде, пропиши команду /set_city.", reply_markup=keyboard)

# Запускаем планировщик задач в отдельном потоке

# Обработчик нажатия кнопки
@dp.message_handler(Text(equals='Включить уведомления о погоде'), state="*")
async def enable_notifications(message: types.Message, state: FSMContext):
    global notifications_enabled
    # await state.update_data(city="Moscow")
    data = await state.get_data()
    city = data.get("city")
    if not city: 
        ... # Введите ваш город
        await state.set_state("ask_city")
    else:
        if not notifications_enabled:
            notifications_enabled = True
            # Здесь вызывайте функцию send_weather_notification с выбранным городом
            # Не забудьте добавить асинхронность к функции
            # Пример: await send_weather_notification(city_name)
            await message.reply("Уведомления о погоде включены.")
        else:
            await message.reply("Уведомления о погоде уже включены.")

# callback | CallbackData

@dp.message_handler(commands=["set_city"], state = "*")
async def _(message: types.Message, state: FSMContext):
    await message.reply("Введите название города")
    await state.set_state("ask_city")

dp.message_handler(commands=['delete_set'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    await message.reply("Уведомления были выкллючены")
  


# Обработчик сообщений с текстом
@dp.message_handler(state="ask_city")
async def _(message: types.Message, state: FSMContext):
    city = message.text
    print(city)
    await state.update_data({"city": city})
    ... 
    await state.reset_state(with_data=False) # ...
    weather = get_weather(city_name=city) 
    await message.reply(weather)
    await asyncio.sleep(1)
    await message.reply(weather)



# Обработчик сообщений с текстом
def get_weather(city_name: str): # Заменить на функцию, которая ничего не отправляет пользователю; А просто возвращает строку или что-то в этом роде. 
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
        return (f"Местное время: {localtm}\n"
            f"Погода в городе: {city_name}\nТемпература: {temperature}C°\n"
            f"Влажность: {humidityy}%\nДавление: {pressure} мм.рт.ст\nВетер: {windspdtrue:.2f} м/с\nНапраление ветра: {winddir}\n"
            f"Восход солнца {sunrisee}: \nЗакат солнца {sunsett}: \nВероятность осадков: {rainchance}\n"
            f"Хорошего дня!"
            )
    else:
        # Отправка сообщения об ошибке пользователю, если запрос был неудачным
        return('Извините, я не смог получить информацию о погоде для этого города. Пожалуйста, попробуйте еще раз позже.')


# MUST BE AFTER ALL COMMANDS
@dp.message_handler(Text(startswith="/"))
async def _(message: types.Message, state: FSMContext):
     await message.reply("Такой команды не существует, попробуй снова")

# Запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

    @dp.message_handler(Text(equals='Что такое dn?'))
async def enable_notifications(message: types.Message, state: FSMContext):
    await message.reply("Deez nuts in your mouth!")
    await bot.send_video(message.chat.id, 'https://media.tenor.com/_8YhYtl4gWAAAAAC/deez-nuts.gif', None, 'Text')

@dp.message_handler(Text(equals='Устрой дождь из лягушек'))
async def enable_notifications(message: types.Message, state: FSMContext):
   await bot.send_video(message.chat.id, 'https://i.gifer.com/MI2d.gif', None, 'Text')