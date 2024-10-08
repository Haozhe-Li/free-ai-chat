# -*- coding: utf-8 -*-
# filename: generateResponse.py
# author: Haozhe Li
# date: 2024-09-01
# description: core code for generating response based on the input text and model.

import os
import asyncio
import logging

from core.utils import fetch, sysPrompt_leak_response, get_champaign_time
from core.prompt_leak_detector import PromptLeakDetector
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

pm_detector = PromptLeakDetector()
activate_pm_detector = True


async def generate_response(
    input_text: str,
    model: str,
    role: str = "",
    context: list = None,
    rag: bool = False,
    task_id: str = "",
) -> str:
    """
    Generate response based on the input_text and model.
    If model is GPT, use OpenAI API, otherwise use Groq API
    Input: input_text, model
    Output: response
    """

    # Check if rag, and get ragPrompt and reference
    try:
        ragPrompt = ""
        if rag:
            logging.info(
                f"[generateResponse.py] RAG search with task_id: {task_id}. input_text: {input_text}"
            )
            response = await rag_search(input_text=input_text, task_id=task_id)
            if response != "":
                ragPrompt = response["ragprompt"]
                # reference = response["reference"]
    except Exception as e:
        logging.error(
            f"[generateResponse.py] Error in RAG search with task_id: {task_id}. {e}, continue without RAG"
        )
        ragPrompt = ""
    # Prepare messages
    messages = [
        {
            "role": "system",
            "content": get_champaign_time(systemPrompt) + ragPrompt + startConversation,
        }
    ]
    messages = messages + context if context else messages
    messages.append(
        {
            "role": "user",
            "content": input_text,
        }
    )

    # Prepare model, url and headers, payload
    model = models[model]

    # If model is auto, select model based on number of messages
    if model == "auto":
        # model = "gpt-4o-mini" if len(messages) < 4 else "llama-3.1-8b-instant"
        model = "gpt-4o-mini"
        logging.info(
            f"[generateResponse.py] Auto model selection with task_id: {task_id}. {model}"
        )
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
        # "stream": True
    }

    # Send request to API
    logging.info(f"[generateResponse.py] Prepare for request with task_id: {task_id}")
    try:
        response = await fetch(url, headers, payload)
        if response.status_code != 200:
            logging.error(
                f"[generateResponse.py] Error in response with task_id: {task_id}. {response.status_code}, {response.json()}"
            )
            return "Error Occured in Backend, Error Code: 500"
        logging.info(f"[generateResponse.py] Response received.")
        tr = response.json()["choices"][0]["message"]["content"]
        if model == "gpt-4o-mini":
            return tr
        logging.info(
            f"[generateResponse.py] Detecting prompt manipulation, with task_id: {task_id}"
        )
        if activate_pm_detector and pm_detector.detect(tr):
            logging.error(
                f"[generateResponse.py] Detected prompt manipulation with task_id: {task_id}. {tr}"
            )
            return sysPrompt_leak_response()
        return tr
    except Exception as e:
        logging.error(
            f"[generateResponse.py] Error in request with task_id: {task_id}. {str(e)}"
        )
        return "Error Occured in Backend, Error Code: 500"


if __name__ == "__main__":
    print(asyncio.run(generate_response("What is seattle?", "LLaMa 3.1", rag=True)))
