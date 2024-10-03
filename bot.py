import asyncio
import gspread
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import BotCommand
from oauth2client.service_account import ServiceAccountCredentials

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import API_TOKEN
from handlers import start, find, upload, send

async def set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="find", description="Найти"),
        BotCommand(command="upload", description="Выгрузка"),
        BotCommand(command="send", description="Рассылка")
    ]
    await bot.set_my_commands(commands)

# Функция для создания меню с кнопками
def get_main_menu():
    # Создаем кнопки
    buttons = [
        [KeyboardButton(text="Начать работу"), KeyboardButton(text="Найти")],
        [KeyboardButton(text="Выгрузка"), KeyboardButton(text="Рассылка")]
    ]
    # Создаем разметку с кнопками
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

async def main() -> None:
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    # Настройка доступа к Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('cred.json', scope)  # Здесь указать путь до вашего кред
    client = gspread.authorize(credentials)
    sheet = client.open('Интеграция GS')  # Открытие таблицы
    sheet1 = sheet.get_worksheet(0)  # Первый лист
    sheet2 = sheet.get_worksheet(1)  # Второй лист таблицы

    # Передаем sheet в роутеры
    dp.include_router(start.router(sheet1))
    dp.include_router(find.router(sheet1))
    dp.include_router(upload.router(sheet1))
    dp.include_router(send.router(sheet2))

    await bot.delete_webhook(True)

    await set_bot_commands(bot)

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
