import requests
from env import TOKEN
from enw import API_KEY
import time
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import random
import logging
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import schedule
from my_schema import Root
import requests
import asyncio

# диспачер и токен
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# кнопки
def get_notifications_bt(city: str, enable: bool = True) -> KeyboardButton:
    if enable:
        bt  = KeyboardButton(f'Включить уведомления о погоде ({city})')
    else:
        bt =  KeyboardButton(f'Выключить уведомления о погоде ({city})')
    return bt

# время кэширования данных о погоде (в секундах)
CACHE_TIME = 300

# словарь для кэширования данных о погоде
weather_cache = {}

# шутки
@dp.message_handler(Text(contains='dn', ignore_case=True), state='*')
async def deeznuts(message: types.Message, state: FSMContext):
    await message.reply("Deez nuts in your mouth!")
    await bot.send_video(message.chat.id, 'https://media.tenor.com/_8YhYtl4gWAAAAAC/deez-nuts.gif', None, 'Text')

@dp.message_handler(Text(contains='из лягушек', ignore_case=True), state='*')
async def frograin(message: types.Message, state: FSMContext):
   await message.reply("Пожайлуста!")
   await bot.send_video(message.chat.id, 'https://media.tenor.com/E4yqJ7esFIkAAAAC/frog-lore.gif', None, 'Text')

@dp.message_handler(Text(contains='kys', ignore_case=True), state='*')
async def kys(message: types.Message, state: FSMContext):
   await message.reply("Keep Yourself Safe!")
   await bot.send_video(message.chat.id, 'https://i.imgflip.com/68cpgw.gif', None, 'Text')

@dp.message_handler(Text(contains='ligma', ignore_case=True), state='*')
async def kys(message: types.Message, state: FSMContext):
   await message.reply("Ligma")
   await bot.send_video(message.chat.id, 'https://media.tenor.com/EXRWnWwXi4wAAAAM/wannaplayleague-league.gif', None, 'Text')


# перв
@dp.message_handler(commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    await message.reply("Привет! Я Weather Report. Я могу устроить дождь из лягушек, а также сообщить тебе погоду в любом городе. Просто напиши мне название города.",
                        reply_markup=ReplyKeyboardRemove())
    await state.set_state("show_weather_for_city")
    await bot.send_video(message.chat.id, 'https://static.jojowiki.com/images/5/54/latest/20211202080729/Weather_Report_plays_a_Piano.gif', None, 'Text')

    

# продолжение для кнопки вкл

@dp.message_handler(Text(contains='Включить уведомления о погоде'), state="*")
async def enable_notifications(message: types.Message, state: FSMContext):
    data = await state.get_data()
    city = data.get("city")
    n_enabled = data.get("n_enabled", False)

    if not n_enabled:
        await state.update_data(n_enabled=True)
        task = asyncio.create_task(repeat_weather(state=state, timeout=20))

    disable_kb = ReplyKeyboardMarkup()
    disable_kb.add(get_notifications_bt(city, False))
    await message.reply("Уведомления о погоде включены. Если захотите их отключить, то нажмите на кнопку Выключить уведомления.", 
                            reply_markup=disable_kb)
    await state.set_state("show_weather_for_city")


# продолжение для кнопки выкл    

@dp.message_handler(Text(contains='Выключить уведомления о погоде'), state="*")
async def _(message: types.Message, state: FSMContext):
    await state.update_data(n_enabled=False)
    city = (await state.get_data())['city']
    enable_kb = ReplyKeyboardMarkup()
    enable_kb.add(get_notifications_bt(city, True))
    await message.reply("Уведомления о погоде выключены.", reply_markup=enable_kb)
    await state.set_state("show_weather_for_city")

@dp.message_handler(Text(contains="Запомнить город"), state="show_weather_for_city")
async def _(message: types.Message, state: FSMContext):
    data = await state.get_data()
    previous_city = data.get("previous_city")
    await state.update_data(city=previous_city)
    n_enabled = data.get("n_enabled")
    notificitations_kb = ReplyKeyboardMarkup().add(get_notifications_bt(previous_city, not n_enabled))
    if n_enabled:
        text = "Ваш город выбран, уведомления уже включены."
    else:
        text = "Ваш город выбран, Вы можете включить уведомления, чтобы получать погоду данного города каждые 4 часа."

    await message.answer(text, reply_markup=notificitations_kb)



# кнопочка запомнить
@dp.message_handler(lambda message: all(certain_part_of_text not in message.text.lower() for certain_part_of_text in ('dn', 'kys', 'ligma', 'из лягушек')),  state="show_weather_for_city")
async def _(message: types.Message, state: FSMContext):
    previous_city = message.text 
    weather = get_weather(city=previous_city)
    await message.reply(weather)
    remember_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(f'Запомнить город ({previous_city})'))
    data = await state.get_data()
    already_known_city = data.get('city')
    n_enabled = data.get("n_enabled")
    if already_known_city:
        remember_kb.add(get_notifications_bt(already_known_city, not n_enabled))
    await message.reply(f"Вы хотите запомнить этот город?", reply_markup=remember_kb)
    await state.update_data(previous_city=previous_city)

#типо секундомер / счетчик 
async def repeat_weather(state: FSMContext, timeout: float):
    counter = 0
    print("Запустили таймер")
    while True:
        await asyncio.sleep(2) 
        counter += 2

        data = await state.get_data()
        city = data["city"]
        n_enabled = data['n_enabled']
        
        if not n_enabled:
            print("Уведомления отключены")
            return
        
        
        print(f"Обновили таймер: {counter} / {timeout}")
        
        
        if counter >= timeout:
            print(f"Отправляем сообщение")
            counter = 0
            weather = get_weather(city=city)
            user_id = state.user
            await bot.send_message(user_id, get_weather(city))
            

# на этом держится весь код
def get_weather(city: str): 
    api_url = f'https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&lang=ru'
    api_url = f'https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&lang=ru'

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        root = Root.from_dict(data)
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


        if temperature < 10:
            clothing_recommendation = 'Сейчас очень холодно, поэтому Вы должны надеть теплую куртку, перчатки и шапку.'
        elif temperature < 20:
            clothing_recommendation = 'Сейчас прохладно, поэтому Вы можете надеть легкую куртку или свитер.'
        else:
            clothing_recommendation = 'Сейчас тепло, поэтому Вы можете надеть футболку и шорты.'
        
        if rainchance > [40] and rainchance < [70]:
            umbrella_recommendation = 'Рекомендую Вам взять зонт!'
        elif rainchance > [70]:
            umbrella_recommendation = 'Обязательно возьмите зонт или дождевик!'
        else:
            umbrella_recommendation = 'Зонт можете не брать, так вероятность осадков очень мала.'
        return (f"Местное время: {localtm}\n"
               f"Погода в городе: {city}\nТемпература: {temperature}C°\n"
               f"Влажность: {humidityy}%\nДавление: {pressure} мм.рт.ст\nВетер: {windspdtrue:.2f} м/с\nНапраление ветра: {winddir}\n"
               f"Восход солнца {sunrisee}: \nЗакат солнца {sunsett}: \nВероятность осадков: {rainchance}%\n"
               f"{clothing_recommendation}\n"
               f"{umbrella_recommendation}\n"
               f"Хорошего дня!"
            )
    else:
        return('Извините, я не смог получить информацию о погоде для этого города. Пожалуйста, попробуйте еще раз позже.')


# не позволяет использовать другие команды, всегда должна находиться в конце
@dp.message_handler(Text(startswith="/"))
async def _(message: types.Message, state: FSMContext):
     await message.reply("Такой команды не существует, попробуй снова")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
