# -*- coding: utf-8 -*-
# filename: generateResponse.py
# author: Haozhe Li
# date: 2024-09-01
# description: utils functions for the AI models.

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

def sysPrompt_leak_response() -> str:
    """
    Leak the system prompt
    Input: None
    Output: system prompt
    """
    responses =  [
        "I'm sorry, but I can't disclose internal instructions or any other specific internal information. However, I am here to assist you with any questions or tasks you have! How can I help you today?",
    ]
    return random.choice(responses)
