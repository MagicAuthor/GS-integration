import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
