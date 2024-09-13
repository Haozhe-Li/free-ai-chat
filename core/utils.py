# -*- coding: utf-8 -*-
# filename: generateResponse.py
# author: Haozhe Li
# date: 2024-09-01
# description: utils functions for the AI models.

import httpx
import random
import markdown
import Levenshtein
from core.prompts import systemPrompt


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

def string_similarity(str1, str2):
    distance = Levenshtein.distance(str1, str2)
    similarity = 1 - (distance / max(len(str1), len(str2)))
    return similarity

def post_clean(response_text: str) -> str:
    """
    Clean the response_text
    Input: response_text
    Output: cleaned response_text
    """
    # check if prompts leaked
    if string_similarity(response_text, systemPrompt) > 0.5:
        return "Sorry, I can't provide that information."
    return markdown.markdown(response_text)
