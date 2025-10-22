import os

import openai

import config

_openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
_referer = os.getenv("OPENROUTER_SITE_URL")
_app_title = os.getenv("OPENROUTER_APP_NAME")

_default_headers = {}
if _referer:
    _default_headers["HTTP-Referer"] = _referer
if _app_title:
    _default_headers["X-Title"] = _app_title

openai_client = openai.OpenAI(
    api_key=config.config.LLM_API_KEY,
    base_url=_openrouter_base_url,
    default_headers=_default_headers or None,
)

async def generate_ideas(topic: str, goals: str = "обучающий, развлекающий, вовлекающий") -> list[str]:
    prompt = f"Предложи 10 идей для постов в Telegram-канале на тему '{topic}'. Учти, что цели постов: {goals}. Формат идей: список с кратким описанием каждой идеи."

    try:
        response = openai_client.chat.completions.create(
            model="deepseek/deepseek-chat"
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        ideas_text = response.choices[0].message.content
        # Parse the list (assuming it's a numbered list)
        ideas = ideas_text.split('\n')
        ideas = [idea.strip() for idea in ideas if idea.strip()]
        return ideas
    except Exception as e:
        return [f"Ошибка генерации идей: {str(e)}"]

async def generate_post_template(topic: str, format: str) -> str:
    prompt = f"Создай шаблон для поста в Telegram на тему '{topic}'. Шаблон должен включать: [яркий заголовок], [вводный абзац], [основная часть] и [призыв к действию (CTA)]. Формат: {format if format else 'стандартный'}."

    try:
        response = openai_client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка генерации шаблона: {str(e)}"

async def generate_report(analytics_data: dict) -> str:
    prompt = f"Проанализируй данные аналитики Telegram-канала за неделю: {analytics_data}. Сгенерируй краткий отчет с общими показателями, наиболее популярными темами и рекомендациями для улучшения контента."

    try:
        response = openai_client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Обшая статистика:\n- Опубликовано постов: {analytics_data.get('total_posts', 0)}\n- Среднее просмотров: {analytics_data.get('avg_views', 0):.1f}\nОшибка ИИ отчета: {str(e)}"
