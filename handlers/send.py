from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter, and_f, or_f
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

def router(sheet):
    new_router = Router()

    class MailingState(StatesGroup):
        waiting_for_text = State()
        waiting_for_photo = State()
        waiting_for_confirmation = State()

    @new_router.message(or_f((Command("send")), F.text.startswith("Рассылка")))
    async def send_command(message: Message, state: FSMContext) -> None:
        await message.answer("Отправьте сообщение для рассылки")
        await state.set_state(MailingState.waiting_for_text)

    # Получение текста от администратора
    @new_router.message(StateFilter(MailingState.waiting_for_text))
    async def get_mailing_text(message: Message, state: FSMContext) -> None:
        await state.update_data(mailing_text=message.text)
        await message.answer("Теперь отправьте фото для рассылки")
        await state.set_state(MailingState.waiting_for_photo)

    # Получение фото от администратора
    @new_router.message(StateFilter(MailingState.waiting_for_photo))#, content_types=["photo"])
    async def get_mailing_photo(message: Message, state: FSMContext) -> None:
        photo = message.photo[-1].file_id  # Получаем file_id фото
        await state.update_data(mailing_photo=photo)

        # Запрашиваем подтверждение
        data = await state.get_data()
        text = data['mailing_text']

        confirm_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить", callback_data="confirm"),
                 InlineKeyboardButton(text="Отменить", callback_data="cancel")]
            ]
        )

        await message.answer("Так выглядит ваше сообщение:")
        await message.answer_photo(photo=photo, caption=text)
        await message.answer("Все правильно?", reply_markup=confirm_kb)

        await state.set_state(MailingState.waiting_for_confirmation)

    # Список пользователей (можно получать его из Google Sheets)
    users = ["1089398402", "1712657654"]

    @new_router.callback_query(and_f(F.data.startswith("confirm"), StateFilter(MailingState.waiting_for_confirmation)))
    async def confirm_mailing(call: CallbackQuery, state: FSMContext, bot: Bot) -> None:
        data = await state.get_data()
        mailing_text = data['mailing_text']
        mailing_photo = data['mailing_photo']
        # Рассылка всем пользователям
        for user_id in users:
            try:
                await bot.send_photo(chat_id=user_id, photo=mailing_photo, caption=mailing_text)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

        # Логирование в Google Sheets
        sheet.append_row([mailing_text, mailing_photo, str(call.message.date)])  # Сохраняем текст, фото и дату

        await call.message.answer("Рассылка успешно завершена")
        await state.clear()

    # Отмена рассылки
    @new_router.callback_query(and_f(F.data.startswith("cancel")), StateFilter(MailingState.waiting_for_confirmation))
    async def cancel_mailing(call: CallbackQuery, state: FSMContext) -> None:
        await call.message.answer("Рассылка отменена")
        await state.clear()

    return new_router
