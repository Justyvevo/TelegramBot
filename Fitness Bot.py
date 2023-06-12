from env import TOKEN
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import random
import logging
from aiogram.types import Message
from itertools import tee
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


import pandas as pd
import numpy as np

def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

# Создаем списки упражнений для каждого диапазона возраста, веса и роста
exercises_by_age = {
    18: ['Отжимания 3 по 20', 'Приседания 3 по 45', 'Подтягивания 3 по 10', 'Жим штанги лежа x11','Планка на 60 секунд', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 60 минут'],
    26: ['Отжимания 3 по 17', 'Приседания 3 по 40', 'Подтягивания 3 по 7', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 50 минут'],
    36: ['Отжимания 3 по 15', 'Приседания 3 по 30', 'Подтягивания 3 по 6', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 40 минут'],
    46: ['Отжимания 3 по 12', 'Приседания 3 по 25', 'Подтягивания 3 по 5', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 30 минут'],
    56: ['Отжимания 3 по 10', 'Приседания 3 по 20', 'Подтягивания 3 по 4', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 20 минут'],
    1000: None
} 

default_by_age = []

# Сделать три класса: Easy, Medium, Hard  внутри сделать другие списки с упражнениями

exercises_by_weight = {
    50: ['Отжимания 3 по 20', 'Приседания 3 по 45', 'Подтягивания 3 по 10', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 60 минут'],
    61: ['Отжимания 3 по 17', 'Приседания 3 по 40', 'Подтягивания 3 по 7', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 50 минут'],
    71: ['Отжимания 3 по 15', 'Приседания 3 по 30', 'Подтягивания 3 по 6', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 40 минут'],
    81: ['Отжимания 3 по 12', 'Приседания 3 по 25', 'Подтягивания 3 по 5', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 30 минут'],
    91: ['Отжимания 3 по 10', 'Приседания 3 по 20', 'Подтягивания 3 по 4', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 30 минут'],
    1000: None
}

default_by_weight = []

exercises_by_height = {
    150: ['Отжимания 3 по 20', 'Приседания 3 по 45', 'Подтягивания 3 по 10', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 60 минут'],
    161: ['Отжимания 3 по 17', 'Приседания 3 по 40', 'Подтягивания 3 по 7', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 50 минут'],
    171: ['Отжимания 3 по 15', 'Приседания 3 по 30', 'Боковая планка на 30 секунд на каждую сторону', 'Подтягивания 3 по 6', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 40 минут'],
    181: ['Отжимания 3 по 12', 'Приседания 3 по 25', 'Подтягивания 3 по 5', 'Скручивания', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 30 минут'],
    200: ['Отжимания 3 по 10', 'Приседания 3 по 20', 'Подтягивания 3 по 4', 'Жим штанги лежа x11', 'Жим гантелей 3 по 7', 'Подъемы на носки с утяжелением и задержкой на верхней точке 3 по 15', 'Жим ногами 3 по 10', 'Становая тяга 3 по 6', 'Фитнес-бег 30 минут'], 
    1000: None
}

default_by_height = []

   
@dp.message_handler(commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    await message.reply("Привет! Я помогу тебе создать систему тренировок на неделю. Напиши мне свой возраст:")
    await state.set_state("ask_age")
    


@dp.message_handler(commands=['generate'], state="*")
async def generate_program(message: types.Message, state: FSMContext):
    data = await state.get_data()
    request = dict()
    if "age" in data:
        request["age"] = data["age"]
    if "weight" in data:
        request["weight"] = data["weight"]
    if "height" in data:
        request["height"] = data["height"]
    table = create_workout_table(**request)
    await message.answer(str(table))



@dp.message_handler(state="ask_age")
async def ask_weight(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data({"age": int(message.text)})
        await message.reply("Отлично! А теперь напиши свой вес:")
        await state.set_state("ask_weight")
    else:
        await message.reply("Напиши, пожалуйста, только цифры. Например, 25")


@dp.message_handler(state="ask_weight")
async def ask_height(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data({"weight": int(message.text)})
        await message.reply("Отлично! А теперь напиши свой рост:")
        await state.set_state("ask_height")
    else:
        await message.reply("Напиши, пожалуйста, только цифры. Например, 67")


@dp.message_handler(state="ask_height")
async def ask_height(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data({"height": int(message.text)})
        await message.reply("Отлично! Напиши, пожалуйста, один из трех уровней тренировки: Сложный, Средний или Легкий")
        await state.set_state("ask_level")
    else:
        await message.reply("Напиши, пожалуйста, только цифры. Например, 180")


@dp.message_handler(state="ask_level")
async def ask_training_level(message: types.Message, state: FSMContext):
    training_levels = ["Сложный", "Средний", "Легкий"]
    if message.text in training_levels:
       await message.reply("Спасибо! Я получил все необходимые данные. Я сформирую для тебя систему тренировок на неделю. Используй команду /generate")
        # здесь можно добавить код для создания системы тренировок
    else:
        await message.reply("Напиши, пожалуйста, один из трех уровней тренировки: Сложный, Средний или Легкий")

# Создаем таблицу с упражнениями
def create_workout_table(age=18, weight=70, height=180, **_):
    # Выбираем список упражнений для каждого диапазона возраста, веса и роста

    for less, more in pairwise(exercises_by_age.keys()):
        if age >= less and age < more:
            age_exercises = exercises_by_age[less]
            break
    else:
        age_exercises = list(default_by_age)

    for less, more in pairwise(exercises_by_weight.keys()):
         if weight >= less and weight < more:
             weight_exercises = exercises_by_weight[less]
             break

    for less, more in pairwise(exercises_by_height.keys()):
         if height >= less and height < more:
             height_exercises = exercises_by_height[less]
             break

    # Объединяем списки упражнений в один список
    all_exercises = age_exercises  + weight_exercises + height_exercises
    # Выбираем случайные упражнения из списка
    workout = random.choices(all_exercises, k=7)

    # Возвращаем таблицу с упражнениями
    workout_table = pd.DataFrame({'Упражнения': workout})
    workout_table.index += 1
    return workout_table
workout_table = create_workout_table
# MUST BE AFTER ALL COMMANDS
@dp.message_handler(Text(startswith="/"))
async def _(message: types.Message, state: FSMContext):
     await message.reply("Такой команды не существует, попробуй снова")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

