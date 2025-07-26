from openai import OpenAI
import os
from .models import AnalyzeSourceMessage
from .search import search

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_messages(chat_id: str, query: str, user_id: str = None, max_messages: int = 100, k: int = 1000) -> tuple[str, int, list[AnalyzeSourceMessage]]:
    # Search for many messages to filter later
    messages = search(chat_id, query, k)
    
    # Filter by user_id if specified
    if user_id:
        messages = [msg for msg in messages if 
                   (msg.user_id and msg.user_id == user_id) or 
                   (not msg.user_id and msg.username == user_id)]
    
    # Limit to max_messages
    messages = messages[:max_messages]
    
    if not messages:
        return "Не найдено сообщений по вашему запросу.", 0, []
    
    # Prepare source messages for response
    source_messages = [
        AnalyzeSourceMessage(
            text=msg.text,
            alias=msg.alias,
            user_id=msg.user_id or msg.username
        )
        for msg in messages
    ]
    
    # Build prompt
    if user_id:
        user_info = f"пользователя {user_id}"
        if messages and messages[0].alias:
            user_info += f" ({messages[0].alias})"
    else:
        user_info = "из чата"
    
    prompt_messages = "\n".join([
        f"{i+1}. {msg.alias}: \"{msg.text}\""
        for i, msg in enumerate(source_messages)
    ])
    
    prompt = f"""Вот список сообщений {user_info}:
{prompt_messages}

Вопрос: {query}"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты анализатор сообщений чата. Отвечай кратко и по существу, описывая характер и поведение на основе сообщений."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    summary = response.choices[0].message.content
    return summary, len(messages), source_messages