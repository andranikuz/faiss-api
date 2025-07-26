from openai import OpenAI
import os
from typing import Optional

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def enhance_search_query(original_query: str, chat_context: Optional[str] = None) -> str:
    """
    Улучшает поисковый запрос для векторного поиска
    
    Args:
        original_query: Оригинальный запрос пользователя
        chat_context: Контекст чата (опционально)
    
    Returns:
        Улучшенный запрос для поиска
    """
    
    system_prompt = """Ты помощник для улучшения поисковых запросов по сообщениям в русскоязычном чате.

КОНТЕКСТ: Ты работаешь с базой данных сообщений из Telegram-чата. Каждое сообщение содержит:
- Текст сообщения от пользователей
- Имена/псевдонимы участников чата
- Эмоции, мнения, обсуждения
- Разговорную речь и сленг
- Реакции на события и людей

Твоя задача: расширить поисковый запрос синонимами и связанными терминами для поиска в этой базе сообщений.

Правила:
1. Сохраняй основной смысл запроса
2. Добавляй синонимы и вариации слов
3. Учитывай русский интернет-сленг и жаргон
4. Добавляй эмоциональные вариации (как люди выражают чувства в чатах)
5. Включай разговорные формы и сокращения
6. Думай о том, как люди реально пишут в чатах
7. НЕ делай запрос слишком длинным (макс 2-3 строки)

Примеры для поиска в чате:
"токсичные пользователи" → "токсичные пользователи агрессивные грубые конфликтные хамы тролли неадекватные"
"обсуждение проекта" → "обсуждение проекта разработка планы идеи предложения код программирование работа"
"кто злится" → "кто злится бесится раздражается негодует недоволен расстроен бомбит"
"программист" → "программист разработчик девелопер кодер айтишник техарь"
"""

    user_prompt = f'Улучши этот поисковый запрос: "{original_query}"'
    
    if chat_context:
        user_prompt += f'\nКонтекст чата: {chat_context}'
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        enhanced_query = response.choices[0].message.content.strip()
        # Удаляем кавычки если есть
        if enhanced_query.startswith('"') and enhanced_query.endswith('"'):
            enhanced_query = enhanced_query[1:-1]
            
        return enhanced_query
        
    except Exception as e:
        # В случае ошибки возвращаем оригинальный запрос
        print(f"Query enhancement failed: {e}")
        return original_query

def should_enhance_query(query: str) -> bool:
    """
    Определяет, стоит ли улучшать запрос
    
    Args:
        query: Поисковый запрос
        
    Returns:
        True если запрос стоит улучшить
    """
    # Не улучшаем очень короткие или очень длинные запросы
    if len(query.split()) < 2 or len(query.split()) > 10:
        return False
    
    # Не улучшаем если запрос уже содержит много синонимов
    if len(query) > 100:
        return False
        
    return True