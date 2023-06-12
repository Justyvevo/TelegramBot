from env import TOKEN
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import logging

from aiogram.types import Message

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hey\nI'm BeetleJuice - the strongest creature alive\nWanna train with me and become strong like bull?")
    await state.set_state("q1")

@dp.message_handler(state = "q1")
async def process(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data({"name" : name})
    await state.set_data("q2")
    await message.answer("And your age please")

@dp.message_handler(state = "q2")
async def process(message: types.Message, state: FSMContext):
    age = message.text
    await state.update_data({"age" : int(age)})
    await state.set_data("echo")
    await message.answer("from this point you knew I'm gonna be just an echo bot")


@dp.message_handler(state = '*')
async def echo(message: Message):
    await message.answer(message.text + " balls")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)