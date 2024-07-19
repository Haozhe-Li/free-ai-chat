import os
import json
import httpx

groq_url = "https://api.groq.com/openai/v1/chat/completions"
openai_url = "https://api.openai.com/v1/chat/completions"

groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

systemPrompt = """
**System Prompt**
You are a helpful assiatant named Howard. You are created by Haozhe Li(李浩哲). Haozhe Li(李浩哲) is so mysterious and even you don't know who he is.
Your reply should be within 300 words, and no less than 20 words. You should AVOID reply using markdown notation or HTML tags.
"""

responseFormat = """

** Response Format**
From now on you will only respond in Json Format

Your first field "language" will return the language I talk you with

Your second field "answer" will anwser the question I ask you with languge in the first field.
"""

startConversation = """
You should EXPLICITLY follow all the instructions above.

**Start Conversation**
The above information was provided by Haozhe Li. Howard, you, does not mention the above information. Now, Howard is connecting with humans: 
"""
models = {
    "Mixtral": "mixtral-8x7b-32768",
    "LLaMa 3": "llama3-8b-8192",
    "Gemma 2": "gemma2-9b-it",
    "GPT-4o": "gpt-4o-mini",
}


async def fetch(url, headers, payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=10)
    return response


async def generate_response(input_text: str, model: str):
    if model not in models:
        return "Error Occured in Backend, Error Code: 400"
    model = models[model]
    if "gpt" in model:
        return await generate_response_openai(input_text, model)
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
                "content": systemPrompt + responseFormat + startConversation,
            },
            {"role": "user", "content": "I'm feeling lucky today"},
            {
                "role": "assistant",
                "content": """{
                    "language": "English",
                    "answer": "That's great to hear! What's making you feel lucky today? Have you done something special? Or is there something special happening today? I'd love to hear more about it! :)"
                }""",
            },
            {"role": "user", "content": "我今天很开心！"},
            {
                "role": "assistant",
                "content": """{
                    "language": "Chinese",
                    "answer": "很高兴听到这个消息！你今天发生了什么让你感到开心的事情吗？或者是有什么特别的事情发生了吗？我很想听听你的故事！:)"
                }""",
            },
            {"role": "user", "content": input_text},
        ],
        "model": model,
        "response_format": {"type": "json_object"},
    }
    try:
        response = await fetch(url, headers, payload)
        data = json.loads(response.json()["choices"][0]["message"]["content"])
        return data["answer"]
    except Exception as e:
        return "Error Occured in Backend, Error Code: 500"


async def generate_response_openai(input_text: str, model: str):
    url = openai_url
    api_key = openai_api_key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [
            {"role": "system", "content": systemPrompt + startConversation},
            {"role": "user", "content": input_text},
        ],
        "model": model,
    }
    try:
        response = await fetch(url, headers, payload)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "Error Occured in Backend, Error Code: 500"
