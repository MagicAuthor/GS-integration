from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

def router(sheet):
    new_router = Router()

    @new_router.message(or_f((Command("find")), F.text.startswith("Найти")))
    async def find_command(message: Message) -> None:
        data = sheet.get_all_records()
        if data:
            current_contact = data[0]
            contact_msg = f"ФИО: {current_contact['ФИО']}\nТелефон: {current_contact['Телефон']}\nАдрес: {current_contact['Адрес']}"
            navigation_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Назад", callback_data="prev_0"),
                     InlineKeyboardButton(text="Вперед", callback_data="next_0")]
                ]
            )
            await message.answer(contact_msg, reply_markup=navigation_kb)
        else:
            await message.answer("Контакты не найдены")

    @new_router.callback_query(or_f(F.data.startswith("next_"), F.data.startswith("prev_")))
    async def navigate_contacts(call: CallbackQuery) -> None:
        data = sheet.get_all_records()
        current_index = int(call.data.split("_")[1])
        # Определяем следующий индекс с проверкой границ
        if call.data.startswith("next_"):
            next_index = min(current_index + 1, len(data) - 1)
        else:
            next_index = max(current_index - 1, 0)

        current_contact = data[next_index]
        contact_msg = f"ФИО: {current_contact['ФИО']}\nТелефон: {current_contact['Телефон']}\nАдрес: {current_contact['Адрес']}"

        # Генерация инлайн-клавиатуры с учетом границ
        navigation_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Назад",
                                         callback_data=f"prev_{next_index}") if next_index > 0 else InlineKeyboardButton(
                        text="Назад", callback_data="none", callback_data_disabled=True),
                    InlineKeyboardButton(text="Вперед", callback_data=f"next_{next_index}") if next_index < len(
                        data) - 1 else InlineKeyboardButton(text="Вперед", callback_data="none",
                                                            callback_data_disabled=True)
                ]
            ]
        )

        await call.message.edit_text(contact_msg, reply_markup=navigation_kb)

    return new_router
