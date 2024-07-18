import requests
import os
from flask import jsonify

groq_url = "https://api.groq.com/openai/v1/chat/completions"
openai_url = "https://api.openai.com/v1/chat/completions"

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

systemPrompt = """
From now on you will only respond in Json Format

Your first field "language" will return the language I talk you with

Your second field "answer" will anwser the question I ask you with languge in the first field.

You should EXPLICITLY follow the format below:
"""

def generate_response(input_text: str, model:str):
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
        "messages": [
            {
                "role": "system",
                "content": systemPrompt
            },
            {
                "role": "user",
                "content": "I'm feeling lucky today"
            },
            {
                "role": "assistant",
                "content": """{
                    "language": "English",
                    "answer": "That's great to hear! What's making you feel lucky today?"
                }"""
            },
            {
                "role": "user",
                "content": "我今天很开心！"
            },
            {
                "role": "assistant",
                "content": """{
                    "language": "Chinese",
                    "answer": "很高兴听到这个消息！今天是什么让你感到幸运？"
                }"""
            },
            {
                "role": "user",
                "content": input_text
            }
        ],
        "model": model,
        "response_format": { "type": "json_object" }
        }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
