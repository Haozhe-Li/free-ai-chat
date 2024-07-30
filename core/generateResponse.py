import os
import asyncio
import logging

from core.utils import fetch, post_clean, is_valid
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
        logging.error(f"[generateResponse.py] Invalid input_text: {input_text}, model: {model}")
        return "Error Occured in Backend, Error Code: 400"

    try:
        ragPrompt = ""
        reference = ""
        if rag:
            logging.info(f"[generateResponse.py] RAG search with input_text: {input_text}")
            response = await rag_search(input_text)
            if response != "":
                ragPrompt = response['ragprompt']
                reference = response['reference']
    except Exception as e:
        logging.error(f"[generateResponse.py] Error in RAG search: {e}, continue without RAG")
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
        logging.info(f"[generateResponse.py] Auto model selection: {model}")

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
    logging.info(f"[generateResponse.py] Prepare for request.")
    try:
        response = await fetch(url, headers, payload)
        if response.status_code != 200:
            logging.error(f"[generateResponse.py] Error in response: {response.status_code}, {response.json()}")
            return "Error Occured in Backend, Error Code: 500"
        logging.info(f"[generateResponse.py] Response received.")
        return post_clean(response.json()["choices"][0]["message"]["content"]) + reference
    except Exception as e:
        logging.error(f"[generateResponse.py] Error in request: {str(e)}")
        return "Error Occured in Backend, Error Code: 500"


if __name__ == "__main__":
    print(asyncio.run(generate_response("What is seattle?", "LLaMa 3.1", rag=True)))
