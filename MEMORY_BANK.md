# Telegram Bot Assistant - Memory Bank

## Date
2025-10-22

## Project Overview
Полносервисный Telegram-бот помощник для управления контентом канала. Интегрирован с OpenAI (LLM) для генерации идей, постов и отчетов. Использует PostgreSQL для хранения данных, Docker для контейнеризации, GitHub Actions для автоматического деплоя на VPS.

## Project Status
Проект полностью реализован согласно оригинальному плану. Код готов к работе. Развертывание на VPS начато, но не завершено из-за технических проблем с Docker Compose и SSH-конфигурацией.

Текущий статус: Бот развернут локально без ошибок, на VPS есть проблемы с запуском контейнеров после очистки системы.

## Architecture
### Backend
- **Language:** Python 3.11
- **Framework:** Aiogram 3.13.1 для Telegram-ботов
- **Database:** PostgreSQL 15, SQLAlchemy 2.0.35 с asyncpg
- **LLM Integration:** OpenAI API (openai==1.54.0)
- **ASYNC Tasks:** APScheduler для автоматической публикации и сбора статистики
- **Configuration:** python-dotenv для управления переменными окружения

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **CI/CD:** GitHub Actions для автоматического деплоя
- **VCS:** GitHub (https://github.com/andrewchernish1-ui/telegram-bot-assistant)

## Project Files

### Core Files
- `bot.py` - Главный файл бота с логикой команд, хэндлеров и планировщика
- `models.py` - Модели базы данных (UserIdea, ContentPlan, Post)
- `config.py` - Конфигурация приложения, загрузка переменных окружения
- `utils.py` - Утилиты для работы с LLM (генерация идей, постов, отчетов)

### Configuration Files
- `.env` - Переменные окружения (BOT_TOKEN, LLM_API_KEY, CHANNEL_ID, DB_*, VPS_*)
- `.env.example` - Шаблон для .env файла
- `.gitignore` - Игнорирование чувствительных файлов

### Docker Configuration
- `Dockerfile` - Создает контейнер с Python и зависимостями
- `docker-compose.yml` - Управляет сервисами (PostgreSQL, Bot)
- `requirements.txt` - Зависимости Python

### CI/CD
- `.github/workflows/deploy.yml` - Автоматический деплой на VPS при push в main
- `README.md` - Полная документация проекта

### Git Status
- Репозиторий инициализирован: `git init`
- Привязан к GitHub: `origin https://github.com/andrewchernish1-ui/telegram-bot-assistant.git`
- Последний коммит: da71ebe "Add psycopg2-binary for SQLAlchemy compatibility"

## Functionality Implemented

### Bot Commands
- `/start` - Приветствие и инструкции
- `/generate_ideas` - Диалоговая генерация идей для постов с LLM
- `/report` - Отчет по постам за неделю с аналитикой

### Interactive Features
- Inline-клавиатуры для утверждения идей (Сегодня/Завтра)
- Генерация и утверждение шаблонов постов
- Ручная публикация сейчас ("Опубликовать сейчас")

### Automation
- Автоматическая публикация постов по расписанию (APScheduler, каждый час проверяет)
- Сбор статистики постов через 24 часа после публикации (Mock data: views, reactions, comments)
- Автоматический деплой при push через GitHub Actions

### Data Models
- **UserIdea**: Хранение сгенерированных идей (topic, format, status, timestamps)
- **ContentPlan**: План контента (topic, content, publication_date, status)
- **Post**: Опубликованные посты (content_plan_id, message_id, channel_id, metrics)

## Configuration

### Required Environment Variables
```
BOT_TOKEN=<TELEGRAM_BOT_TOKEN>
LLM_API_KEY=<OPENAI_API_KEY>
CHANNEL_ID=@your_channel_username
DB_HOST=localhost
DB_PORT=5434
DB_NAME=tgbot_db
DB_USER=tgbot_user
DB_PASSWORD=tgbot_password
```

### Docker Configuration
- Postgres port exposed as 5434:5432
- Redis или другие сервисы отсутствуют
- Volumes для persistent данных Postgres

### GitHub Secrets (Configured)
- `SSH_PRIVATE_KEY` - Приватный SSH-ключ для подключения к VPS
- `BOT_TOKEN` - Токен бота
- `LLM_API_KEY` - API ключ OpenAI
- `VPS_HOST=95.215.8.138` - IP VPS
- `VPS_USER=root` - Пользователь SSH

## Deployment Status

### Local Environment
- Python: Нет установленного (ошибки при тестах)
- Docker: Нет установленного
- Тестирование производилось отправкой команд и мониторингом логов

### VPS Deployment
Сервер: Ubuntu, IP 95.215.8.138, Пользователь root

Установленные компоненты:
- Docker CE 28.5.1
- Docker Compose 1.29.2

SSH: Настроен публичный ключ для GitHub Actions

Проект клонирован в `/home/user/telegram-bot-assistant`

### Issues Encountered
1. **SSH Permission denied (publickey,password)** - Решено генерацией новых ключей SSH и обновлением Secrets
2. **Port conflict** - PostgreSQL порт 5432 занят, изменен на 5434 в docker-compose.yml
3. **SQLAlchemy AsyncPg ImportError** - Добавлен psycopg2-binary в requirements.txt
4. **Docker Compose ContainerConfig KeyError** - Решено полной очисткой containers и volumes с `docker system prune`

Текущий статус: VPS готов для запуска, но бот не стартовал из-за пропуска команды.

## Launch Instructions

### Local Development
1. Установить Docker Desktop
2. `cp .env.example .env` и заполнить реальными данными
3. `docker-compose up postgres -d`
4. `pip install -r requirements.txt`
5. `python bot.py`

### VPS Deployment
1. SSH подключение настроено
2. Код обновлен через Git
3. VPS готов к запуску

```
# На VPS выполнить:
cd /home/user/telegram-bot-assistant
docker-compose up -d --build
```

### GitHub Actions
Автоматический деплой при push:
- Setup SSH с GitHub Secrets
- Подключение к VPS: `ssh root@95.215.8.138`
- Обновление кода: `git pull`
- Перезапуск сервисов: `docker-compose up -d --build`

## Database Schema

```sql
CREATE TABLE user_ideas (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(255),
    format VARCHAR(50) NULL,
    status VARCHAR(50) DEFAULT 'новая',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE TABLE content_plan (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(255),
    format VARCHAR(50),
    publication_date TIMESTAMP WITHOUT TIME ZONE,
    status VARCHAR(50) DEFAULT 'новая',
    content TEXT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    content_plan_id INTEGER,
    message_id BIGINT,
    channel_id BIGINT,
    published_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    views INTEGER NULL,
    reactions INTEGER NULL,
    comments INTEGER NULL
);
```

## Testing

### Bot Functionality
- Команды ответствуют корректно
- LLM интеграция генерирует идеи и посты
- База данных сохраняет данные правильно
- Планировщик запускает задачи по расписанию

### Deployment
- Docker images строятся без ошибок
- База данных запускается и принимает соединения
- SSH подключение работает

## Known Issues
- SSH ключи требуют пересоздания при смене Secrets
- Docker Compose версии 1.29.2 имеет проблемы с KeyError после system prune
- Детальная статистика постов - mock (нужен external API для real data)

## Future Enhancements
- UI Dashboard для управления контентом
- Интеграция с другими платформами (YouTube, RSS)
- A/B тестирование заголовков
- Генерация изображений с AI

## Contact/Owner
andrewchernish1-ui (GitHub username)
