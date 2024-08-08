import httpx
import random
import markdown


def gen_task_id():
    """
    Generate a random task id
    Input: None
    Output: task_id
    """
    return str(random.randint(100000, 999999))


async def fetch(url: str, headers: dict, payload: dict):
    """
    Fetch data from the given url with headers and payload
    Input: url, headers, payload
    Output: response
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=10)
    return response


def post_clean(response_text: str) -> str:
    """
    Clean the response_text
    Input: response_text
    Output: cleaned response_text
    """
    return markdown.markdown(response_text)
