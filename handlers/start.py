from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import CallbackQuery, FSInputFile, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot import get_main_menu

def router(sheet):
    new_router = Router()

    # Машина состояний для ввода данных
    class UserState(StatesGroup):
        FIO = State()
        Phone = State()
        Address = State()

    @new_router.message(CommandStart())
    async def start_command(message: Message) -> None:
        # Отправляем приветственное сообщение с меню
        await message.answer("Выберите команду из меню:", reply_markup=get_main_menu())

    # Команда /start - Приветственное видео и инлайн-кнопка
    @new_router.message(F.text.startswith("Начать работу"))
    #@new_router.message(CommandStart())
    async def start_command(message: Message) -> None:
        # Создаем инлайн-клавиатуру
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Начать регистрацию", callback_data="register")]
            ]
        )
        # Отправляем приветственное видео
        video = FSInputFile("привет.mp4")
        await message.answer_video(video=video, reply_markup=inline_kb)

    # Обработка нажатия инлайн-кнопки
    @new_router.callback_query(F.data.startswith("register"))
    async def register_user(call: CallbackQuery, state: FSMContext) -> None:
        await call.message.answer("Введите ваше ФИО:")
        await state.set_state(UserState.FIO)

    # Ввод ФИО
    @new_router.message(StateFilter(UserState.FIO))
    async def enter_fio(message: Message, state: FSMContext) -> None:
        await state.update_data(fio=message.text)
        await message.answer("Введите ваш номер телефона:")
        await state.set_state(UserState.Phone)

    # Ввод номера телефона
    @new_router.message(StateFilter(UserState.Phone))
    async def enter_phone(message: Message, state: FSMContext) -> None:
        await state.update_data(phone=message.text)
        await message.answer("Введите ваш адрес проживания:")
        await state.set_state(UserState.Address)

    # Ввод адреса
    @new_router.message(StateFilter(UserState.Address))
    async def enter_address(message: Message, state: FSMContext) -> None:
        await state.update_data(address=message.text)

        user_data = await state.get_data()
        fio = user_data['fio']
        phone = user_data['phone']
        address = user_data['address']

        # Сохранение данных в Google Sheets
        sheet.append_row([fio, phone, address])

        await message.answer(f"Ваши данные сохранены.\nФИО: {fio}\nТелефон: {phone}\nАдрес: {address}")
        await state.clear()

    return new_router
