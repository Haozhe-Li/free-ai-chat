import httpx
import re

models = {
    "Mixtral": "mixtral-8x7b-32768",
    "LLaMa 3.1": "llama-3.1-8b-instant",
    "Gemma 2": "gemma2-9b-it",
    "GPT-4o": "gpt-4o-mini",
    "Auto": "auto",
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


def post_clean(response_text: str):
    """
    Clean the response_text
    Input: response_text
    Output: cleaned response_text
    """
    response_text = response_text.replace("\n", "<br>")
    response_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", response_text)
    response_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", response_text)
    response_text = re.sub(r"__(.*?)__", r"<u>\1</u>", response_text)
    return response_text


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
