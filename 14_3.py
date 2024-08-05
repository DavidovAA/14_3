from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


api = ''
bot = Bot(token = api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = InlineKeyboardMarkup()
button1 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
button2 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
kb.add(button1)
kb.add(button2)

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Купить'),
            KeyboardButton(text='Информация'),
            KeyboardButton(text='Рассчитать')
        ]
    ], resize_keyboard=True
)

catalog_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Product1', callback_data='product_buying')],
        [InlineKeyboardButton(text='Product2', callback_data='product_buying')],
        [InlineKeyboardButton(text='Рroduct3', callback_data='product_buying')],
        [InlineKeyboardButton(text='Product4', callback_data='product_buying')]
    ], resize_keyboard=True
)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands = ['start'])
async def start(message):
    await message.answer('Введите команду /start, чтобы начать общение', reply_markup = start_kb)

@dp.message_handler(text = 'Информация')
async def info(message):
    await message.answer('Мы продаем бады')

@dp.message_handler(text = 'Рассчитать')
async def price(message):
    await message.answer('Выберите опцию', reply_markup = start_kb)

@dp.message_handler(text = 'Купить')
async def get_buying_list(message):
    for i in range(1, 5):
        await message.answer(f'Название: Product{i}' | f'Описание: Описание{i}' | 'Цена: {i*100}')
        with open(f'Files/{i}.jpg', 'rb') as jpg:
            await message.answer_photo(jpg)
    await message.answer('Выберите продукт для покупки', reply_markup = catalog_kb)

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Поздравляем! Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5; '
                              'для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.')
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(first=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(second=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(third=message.text)
    data = await state.get_data()
    podschet_kallorii = (10*data['third'])+(6.25*data['second'])-(5*data['first'])+5
    await message.answer(f'Ваша суточная норма каллорий составляет: {podschet_kallorii}')
    await state.finish()

@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
