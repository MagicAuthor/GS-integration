import requests

from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message
from urllib.parse import urlencode

from config import YANDEX_API_KEY

def geocode_address(address):
    base_url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "geocode": address,
        "format": "json",
        "apikey": YANDEX_API_KEY
    }
    response = requests.get(base_url, params=params)
    json_response = response.json()
    try:
        pos = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        longitude, latitude = pos.split(" ")
        return float(latitude), float(longitude)
    except (KeyError, IndexError):
        return None

def generate_yandex_map_url(coordinates):
    base_url = "https://static-maps.yandex.ru/1.x/"
    markers = "~".join([f"{lon},{lat},pm2rdm" for lat, lon in coordinates])
    params = {
        "l": "map",  # тип карты: map - обычная карта
        "pt": markers,  # добавляем маркеры
        "size": "650,450"  # размер изображения
    }
    map_url = f"{base_url}?{urlencode(params)}"
    return map_url  # Возвращаем URL карты


def router(sheet):
    new_router = Router()

    @new_router.message(or_f((Command("upload")), F.text.startswith("Выгрузка")))
    async def upload_command(message: Message) -> None:
        data = sheet.get_all_records()
        addresses = [entry['Адрес'] for entry in data]  # Извлекаем список адресов
        # Получаем координаты для всех адресов
        coordinates = [geocode_address(address) for address in addresses]
        coordinates = [coord for coord in coordinates if coord]  # Убираем пустые значения

        # Если координаты получены, продолжаем обработку
        if coordinates:
            # Генерируем URL карты с помощью координат
            map_url = generate_yandex_map_url(coordinates)
            await message.answer(f"Вот ссылка на карту: {map_url}")
        else:
            await message.answer("Не удалось получить координаты для указанных адресов")

    return new_router
