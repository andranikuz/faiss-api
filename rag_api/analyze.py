from openai import OpenAI
import os
from .models import SearchResult
from .search import search

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_messages(chat_id: str, query: str, k: int = 5) -> tuple[str, list[SearchResult]]:
    messages = search(chat_id, query, k)
    
    if not messages:
        return "Не найдено сообщений по вашему запросу.", []
    
    prompt_messages = "\n".join([
        f"{i+1}. @{msg.username}: \"{msg.text}\""
        for i, msg in enumerate(messages)
    ])
    
    prompt = f"""Вот сообщения:
{prompt_messages}

Вопрос: {query}"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты анализатор сообщений чата. Отвечай кратко и по существу."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    gpt_answer = response.choices[0].message.content
    return gpt_answer, messages