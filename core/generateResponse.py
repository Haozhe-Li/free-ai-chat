import os
import asyncio

from core.utils import fetch
from core.prompts import *
from core.rag import rag_search

groq_url = "https://api.groq.com/openai/v1/chat/completions"
openai_url = "https://api.openai.com/v1/chat/completions"

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

models = {
    "Mixtral": "mixtral-8x7b-32768",
    "LLaMa 3.1": "llama-3.1-8b-instant",
    "Gemma 2": "gemma2-9b-it",
    "GPT-4o": "gpt-4o-mini",
    "Auto": "auto",
}

role = {
    "translator": translatorPrompt,
}


async def generate_response(
    input_text: str, model: str, role: str = "", context: list = None, rag: bool = False
) -> str:
    """
    Generate response based on the input_text and model.
    If model is GPT, use OpenAI API, otherwise use Groq API
    Input: input_text, model
    Output: response
    """
    if not is_valid(input_text, model):
        return "Error Occured in Backend, Error Code: 400"

    try:
        ragPrompt = ""
        reference = ""
        if rag:
            response = await rag_search(input_text)
            if response != "":
                ragPrompt = response['ragprompt']
                reference = response['reference']
    except Exception as e:
        ragPrompt = ""
        reference = ""

    messages = [
        {
            "role": "system",
            "content": systemPrompt + ragPrompt + startConversation,
        }
    ]

    messages = messages + context if context else messages

    messages.append(
        {
            "role": "user",
            "content": input_text,
        }
    )

    model = models[model]
    if model == "auto":
        model = "gpt-4o-mini" if len(messages) < 4 else "llama-3.1-8b-instant"

    if "gpt" in model:
        url = openai_url
        api_key = openai_api_key
    else:
        url = groq_url
        api_key = groq_api_key

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": messages,
        "model": model,
        "temperature": 1,
        "max_tokens": 2048,
        "top_p": 1,
    }
    try:
        response = await fetch(url, headers, payload)
        if response.status_code != 200:
            return "Error Occured in Backend, Error Code: 500"
        return response.json()["choices"][0]["message"]["content"] + reference
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


if __name__ == "__main__":
    print(asyncio.run(generate_response("What is seattle?", "LLaMa 3.1", rag=True)))
