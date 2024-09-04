# -*- coding: utf-8 -*-
# filename: generateResponse.py
# author: Haozhe Li
# date: 2024-09-01
# description: Code for RAG search, and decision making for RAG search.

import os
import asyncio
import json
import logging
import random
from core.utils import fetch
from core.prompts import activateRagPrompt, ragPromptTemplate
from tavily import TavilyClient

def init_rag_client() -> TavilyClient:
    api_keys = [os.getenv("TAVILY_API_KEY_1"), os.getenv("TAVILY_API_KEY_2")]
    tavily_client = TavilyClient(api_key=random.choice(api_keys))
    return tavily_client


async def activate_rag(input_text: str, task_id: str = "") -> dict:
    groq_url = "https://api.groq.com/openai/v1/chat/completions"
    model = "llama-3.1-8b-instant"
    groq_api_key = os.getenv("GROQ_API_KEY")

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": activateRagPrompt,
            },
            {
                "role": "user",
                "content": input_text,
            },
        ],
        "response_format": {"type": "json_object"},
    }
    response = await fetch(groq_url, headers, payload)
    if response.status_code != 200:
        return {"enableSearch": False}
    result = json.loads(response.json()["choices"][0]["message"]["content"])
    return result


async def rag_search(input_text: str, task_id: str = "") -> dict:
    """
    Search Wikipedia for the input_text and return the result
    Input: input_text
    Output: ragPrompt"""
    logging.info(
        f"[rag.py] RAG search with input_text with task_id: {task_id}. {input_text}"
    )
    decision = await activate_rag(input_text=input_text, task_id=task_id)
    if decision["enableSearch"] == False:
        logging.info(
            f"[rag.py] RAG search with input_text with task_id: {task_id}. {input_text} - No search"
        )
        return {"ragprompt": ""}
    ragPrompt = ragPromptTemplate
    logging.info(
        f"[rag.py] RAG search with input_text with task_id: {task_id}. Query {decision['query']}"
    )
    ragPrompt += init_rag_client().qna_search(query=decision["query"])
    logging.info(
        f"[rag.py] RAG search with input_text with task_id: {task_id}. Search completed: {ragPrompt}"
    )
    return {"ragprompt": ragPrompt}


if __name__ == "__main__":
    print(asyncio.run(rag_search("What is the time now in New York?")))
