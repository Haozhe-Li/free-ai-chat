import os
import httpx

from core.prompts import *

groq_url = "https://api.groq.com/openai/v1/chat/completions"
openai_url = "https://api.openai.com/v1/chat/completions"

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

models = {
    "Mixtral": "mixtral-8x7b-32768",
    "LLaMa 3.1": "llama-3.1-8b-instant",
    "Gemma 2": "gemma2-9b-it",
    "GPT-4o": "gpt-4o-mini",
}

role = {
    "translator": translatorPrompt,
}


async def fetch(url: str, headers: dict, payload: dict):
    """
    Fetch data from the given url with headers and payload
    Input: url, headers, payload
    Output: response
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=10)
    return response


async def generate_response(
    input_text: str, model: str, role: str = "", context: list = None
) -> str:
    """
    Generate response based on the input_text and model.
    If model is GPT, use OpenAI API, otherwise use Groq API
    Input: input_text, model
    Output: response
    """
    if not is_valid(input_text, model):
        return "Error Occured in Backend, Error Code: 400"
    model = models[model]
    if "gpt" in model:
        url = openai_url
        api_key = openai_api_key
    else:
        url = groq_url
        api_key = groq_api_key

    if role != "":
        rolePrompt = role[role]
    else:
        rolePrompt = systemPrompt

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    messages = [
        {
            "role": "system",
            "content": rolePrompt + startConversation,
        }
    ]

    # add context which a list behind the message list
    messages = messages + context if context else messages

    messages.append(
        {
            "role": "user",
            "content": input_text,
        }
    )

    payload = {
        "messages": messages,
        "model": model,
        "temperature": 1,
        "max_tokens": 2048,
        "top_p": 1,
    }
    try:
        response = await fetch(url, headers, payload)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "Error Occured in Backend, Error Code: 500"


def is_valid(input_text: str, model: str) -> bool:
    """
    Check if the input_text and model are valid
    Input: input_text, model
    Output: True if valid, False otherwise
    """
    if not input_text or not model:
        return False
    if model not in models:
        return False
    return True
