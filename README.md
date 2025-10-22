# Telegram Bot Assistant

Бот-помощник для управления контентом в Telegram-канале, с интеграцией LLM (например, OpenAI) для генерации идей и постов.

## Установка и запуск

### Локальный запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Скопируйте файл настроек:
```bash
cp .env.example .env
```

5. Заполните `.env` файл вашими данными:
- `BOT_TOKEN`: Токен вашего Telegram-бота
- `LLM_API_KEY`: API ключ OpenAI или другого LLM провайдера
- `CHANNEL_ID`: @username вашего канала или числовой ID канала
- Настройки базы данных (по умолчанию подходят для локального запуска с Docker)

6. Запустите PostgreSQL:
```bash
docker-compose up postgres -d
# или docker compose up postgres -d (новый синтаксис)
```

7. Запустите бота:
```bash
python bot.py
```

**Примечание:** Для тестирования бота добавьте его в канал как администратора, например, через @BotFather добавьте канал в "Channel Username". Для сбору статистики используйте mock данные; для реального - интеграция с external API.

### Запуск на VPS с Docker

1. Подготовьте VPS с Ubuntu:
- Установите Docker и Docker Compose

2. Передайте проект на VPS:
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

3. Настройте `.env` файл на VPS

4. Запустите все сервисы:
```bash
docker-compose up -d
```

## Функционал бота

- `/start`: Приветствие и инструкции
- `/generate_ideas`: Генерация идей для постов с использованием LLM
- `/report`: Получить отчет по постам с аналитикой
- Взаимодействие с идеями через inline-кнопки (утверждение, установка дат публикации)
- Генерация шаблонов постов с кнопками "Утвердить", "Опубликовать сейчас"
- Автоматическая публикация постов по расписанию с APScheduler
- Хранение данных в PostgreSQL (идеи, план контента, опубликованные посты)
- Автоматический деплой через GitHub Actions

## Структура проекта

- `bot.py`: Основной код бота
- `models.py`: Модели базы данных SQLAlchemy
- `utils.py`: Утилиты, включая функции для работы с LLM
- `config.py`: Конфигурация приложения
- `requirements.txt`: Python зависимости
- `docker-compose.yml`: Docker Compose конфигурация
- `Dockerfile`: Docker образ для бота
- `.env`: Чувствительные данные (не коммитить)
- `.env.example`: Шаблон для .env

## CI/CD

Проект использует GitHub Actions для автоматического развертывания на VPS при пуше в ветку main.

Необходимо настроить в GitHub Secrets:
- `SSH_PRIVATE_KEY`: Приватный SSH-ключ для доступа к VPS
- `VPS_HOST`: IP-адрес или домен VPS
- `VPS_USER`: Пользователь SSH
- Переменные окружения: `BOT_TOKEN`, `LLM_API_KEY`

## Разработка

Для продвижения функционала добавьте новые хэндлеры в `bot.py`, модели в `models.py`, и утилиты в `utils.py`.

## Лицензия

MIT License
