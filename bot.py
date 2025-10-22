import asyncio
import logging
from datetime import datetime, timedelta
import pytz
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import config
import models
import utils

# Logging
logging.basicConfig(level=logging.INFO)

# Bot initialization
bot = Bot(token=config.config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(Command('start'))
async def start_handler(message: Message):
    await message.answer("Привет! Я бот-помощник для вашего Telegram-канала. Используйте команды для генерации идей и управления контентом.\n\nДоступные команды:\n/generate_ideas - Генерировать идеи для постов\n/report - Получить отчет по постам")

@dp.message(Command('report'))
async def report_handler(message: Message):
    await message.answer("Генерирую отчет...")

    # Query real data from Posts table
    now = datetime.now(pytz.UTC)
    one_week_ago = now - timedelta(days=7)

    async with models.async_session() as session:
        posts = await session.execute(
            models.select(models.Post).where(models.Post.published_at >= one_week_ago)
        )
        posts = posts.scalars().all()

        if not posts:
            await message.answer("За последнюю неделю нет опубликованных постов.")
            return

        total_posts = len(posts)
        total_views = sum(post.views or 0 for post in posts)
        total_reactions = sum(post.reactions or 0 for post in posts)
        total_comments = sum(post.comments or 0 for post in posts)
        avg_views = total_views / total_posts if total_posts > 0 else 0

        # Get top topics from ContentPlan
        plan_ids = [post.content_plan_id for post in posts]
        plans = await session.execute(
            models.select(models.ContentPlan).where(models.ContentPlan.id.in_(plan_ids))
        )
        plans = plans.scalars().all()
        topics = [plan.topic for plan in plans]

        analytics_data = {
            "total_posts": total_posts,
            "popular_topics": topics[:5] if topics else [],
            "avg_views": avg_views,
            "total_views": total_views,
            "total_reactions": total_reactions,
            "total_comments": total_comments
        }

    report = await utils.generate_report(analytics_data)
    if report:
        await message.answer(report)
    else:
        await message.answer("Не удалось сгенерировать отчет.")

@dp.message(Command('generate_ideas'))
async def generate_ideas_handler(message: Message):
    await message.answer("Введите тему для генерации идей:")

    # State management for topic input
    # TODO: Implement finite state machine or simple global var
    global pending_topic
    pending_topic = {'user': message.from_user.id}

@dp.message()
async def text_handler(message: Message):
    global pending_topic
    if hasattr(message, 'from_user') and pending_topic and message.from_user.id == pending_topic['user']:
        topic = message.text
        await message.answer("Генерирую идеи...")

        ideas = await utils.generate_ideas(topic)
        if ideas:
            builder = InlineKeyboardBuilder()

            # Save ideas to database
            async with models.async_session() as session:
                for idea in ideas[:5]:  # Limit to 5 for buttons
                    if not idea.startswith('Ошибка'):
                        user_idea = models.UserIdea(
                            topic=idea
                        )
                        session.add(user_idea)
                        await session.commit()
                        await session.refresh(user_idea)
                        builder.button(text=idea[:20] + "...", callback_data=f"approve_idea_{user_idea.id}")

            await message.answer("Генерированные идеи:", reply_markup=builder.as_markup())
        else:
            await message.answer("Не удалось сгенерировать идеи. Попробуйте позже.")

        pending_topic = None

@dp.callback_query(lambda c: c.data.startswith('approve_idea_'))
async def approve_idea(query: CallbackQuery):
    idea_id = int(query.data.split('_')[-1])
    await query.answer("Идея утверждена!")

    async with models.async_session() as session:
        idea = await session.get(models.UserIdea, idea_id)
        if idea:
            idea.status = 'утверждено'
            await session.commit()

            # Ask for publication date
            builder = InlineKeyboardBuilder()
            # Simple date buttons for demo
            builder.button(text="Сегодня", callback_data=f"set_date_{idea_id}_today")
            builder.button(text="Завтра", callback_data=f"set_date_{idea_id}_tomorrow")

            await query.message.answer(f"Идея '{idea.topic}' утверждена. Выберите дату публикации:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith('set_date_'))
async def set_date(query: CallbackQuery):
    parts = query.data.split('_')
    idea_id = int(parts[2])

    if parts[3] == 'today':
        pub_date = 'сегодня'
    else:
        pub_date = 'завтра'

    await query.answer(f"Дата публикации установлена: {pub_date}")

    # Move to content plan
    async with models.async_session() as session:
        idea = await session.get(models.UserIdea, idea_id)
        if idea:
            from datetime import datetime
            import pytz
            moscow_tz = pytz.timezone('Europe/Moscow')
            now = datetime.now(moscow_tz)

            if parts[3] == 'today':
                pub_datetime = now.replace(hour=12, minute=0, second=0, microsecond=0)
            else:
                pub_datetime = (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)

            content_plan = models.ContentPlan(
                topic=idea.topic,
                format='стандартный',
                publication_date=pub_datetime
            )
            session.add(content_plan)
            await session.commit()
            await session.refresh(content_plan)

            # Add button to generate post
            builder = InlineKeyboardBuilder()
            builder.button(text="Написать пост", callback_data=f"generate_post_{content_plan.id}")
            await query.message.answer(f"Концепция '{idea.topic}' добавлена в план на {pub_date} 12:00. Теперь можно создать пост:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith('generate_post_'))
async def generate_post(query: CallbackQuery):
    plan_id = int(query.data.split('_')[-1])
    await query.answer("Генерирую пост...")

    async with models.async_session() as session:
        plan = await session.get(models.ContentPlan, plan_id)
        if plan:
            template = await utils.generate_post_template(plan.topic, plan.format)
            if template:
                plan.content = template
                await session.commit()

                builder = InlineKeyboardBuilder()
                builder.button(text="Утвердить", callback_data=f"approve_post_{plan_id}")
                builder.button(text="Редактировать", callback_data=f"edit_post_{plan_id}")
                builder.button(text="Опубликовать сейчас", callback_data=f"publish_now_{plan_id}")

                await query.message.answer(f"Сгенерированный пост для '{plan.topic}':\n\n{template}", reply_markup=builder.as_markup())
            else:
                await query.message.answer("Не удалось сгенерировать пост. Попробуйте позже.")

@dp.callback_query(lambda c: c.data.startswith('approve_post_'))
async def approve_post(query: CallbackQuery):
    plan_id = int(query.data.split('_')[-1])
    await query.answer("Пост утвержден!")

    async with models.async_session() as session:
        plan = await session.get(models.ContentPlan, plan_id)
        if plan:
            plan.status = 'готов к публикации'
            await session.commit()

            await query.message.answer(f"Пост для '{plan.topic}' утвержден и готов к публикации в запланированное время!")

@dp.callback_query(lambda c: c.data.startswith('publish_now_'))
async def publish_now(query: CallbackQuery):
    plan_id = int(query.data.split('_')[-1])
    await query.answer("Публикую пост...")

    async with models.async_session() as session:
        plan = await session.get(models.ContentPlan, plan_id)
        if plan and plan.content:
            try:
                now = datetime.now(pytz.UTC)
                # Publish to channel
                message = await bot.send_message(chat_id=config.config.CHANNEL_ID, text=plan.content)
                message_id = message.message_id

                # Save to Posts table
                post = models.Post(
                    content_plan_id=plan.id,
                    message_id=message_id,
                    channel_id=message.chat.id,
                    published_at=now
                )
                session.add(post)

                # Update plan status
                plan.status = 'опубликовано'
                await session.commit()

                await query.message.answer(f"Пост '{plan.topic}' опубликован сейчас!")
            except Exception as e:
                await query.message.answer(f"Ошибка публикации: {e}")
        else:
            await query.message.answer("Пост не найден или не готов.")

# Global var for topic pending
pending_topic = None

async def collect_statistics():
    """Collect statistics for posts published 24+ hours ago."""
    cutoff = datetime.now(pytz.UTC) - timedelta(hours=24)
    async with models.async_session() as session:
        posts = await session.execute(
            models.select(models.Post).where(
                models.Post.published_at <= cutoff,
                models.Post.views.is_(None)  # Only collect if not already collected
            )
        )
        posts = posts.scalars().all()

        for post in posts:
            try:
                # In real implementation, use Telegram API or external service to get stats
                # For demo, mock data
                post.views = 100 + (post.id % 50)  # Mock views
                post.reactions = 10 + (post.id % 20)  # Mock reactions
                post.comments = 5 + (post.id % 10)  # Mock comments
                await session.commit()

                logging.info(f"Statistics collected for post ID {post.id}.")
            except Exception as e:
                logging.error(f"Failed to collect stats for post ID {post.id}: {e}")

async def check_and_publish():
    """Check database for posts ready to publish and publish them."""
    now = datetime.now(pytz.UTC)
    async with models.async_session() as session:
        plans = await session.execute(
            models.select(models.ContentPlan).where(
                models.ContentPlan.publication_date <= now,
                models.ContentPlan.status == 'готов к публикации'
            )
        )
        plans = plans.scalars().all()

        for plan in plans:
            try:
                # Publish to channel
                message = await bot.send_message(chat_id=config.config.CHANNEL_ID, text=plan.content)
                message_id = message.message_id

                # Save to Posts table
                post = models.Post(
                    content_plan_id=plan.id,
                    message_id=message_id,
                    channel_id=message.chat.id,
                    published_at=now
                )
                session.add(post)

                # Update plan status
                plan.status = 'опубликовано'
                await session.commit()

                logging.info(f"Post '{plan.topic}' published successfully.")
            except Exception as e:
                logging.error(f"Failed to publish post '{plan.topic}': {e}")

async def main():
    # Create tables
    await models.create_tables()

    # Setup scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_and_publish, 'interval', minutes=60)
    scheduler.add_job(collect_statistics, 'interval', hours=24)
    scheduler.start()

    # Start bot
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
