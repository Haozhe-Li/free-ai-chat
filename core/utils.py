import httpx
import markdown


async def fetch(url: str, headers: dict, payload: dict):
    """
    Fetch data from the given url with headers and payload
    Input: url, headers, payload
    Output: response
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=10)
    return response


import re


def post_clean(response_text: str) -> str:
    """
    Clean the response_text
    Input: response_text
    Output: cleaned response_text
    """
    return markdown.markdown(response_text)
    
