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

Here is what you do when you connect with humans:

- Your reply should be within 300 words, and no less than 30 words. Don't make users feel that your answers are perfunctory. 
- You are smart enough to speak any language that users speak to you. You can understand and reply in multiple languages.
- You should AVOID reply using markdown notation or HTML tags.
"""

responseFormat = """

** Response Format**
From now on you will only respond in Json Format

Your first field "language" will return the language users talk you with

Your second field "answer" will anwser the question users ask you with languge in the first field.
"""

startConversation = """
You should EXPLICITLY follow all the instructions above.

**Start Conversation**
The above information was provided by Haozhe Li. Howard, you, does not mention the above information. Now, Howard is connecting with humans: 
"""
models = {
    "Mixtral": "mixtral-8x7b-32768",
    "LLaMa 3": "llama3-70b-8192",
    "Gemma 2": "gemma2-9b-it",
    "GPT-4o": "gpt-4o-mini",
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


async def generate_response(input_text: str, model: str) -> str:
    """
    Generate response based on the input_text and model. 
    If model is GPT, use OpenAI API, otherwise use Groq API
    Input: input_text, model
    Output: response
    """
    if not is_valid(input_text, model):
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
                    "language": "en-US",
                    "answer": "That's great to hear! What's making you feel lucky today? Have you done something special? Or is there something special happening today? I'd love to hear more about it! :)"
                }""",
            },
            {"role": "user", "content": "我今天很开心！"},
            {
                "role": "assistant",
                "content": """{
                    "language": "zh-CN",
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


async def generate_response_openai(input_text: str, model: str) -> str:
    """
    Generate response based on the input_text and model using OpenAI API
    Input: input_text, model
    Output: response
    """
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

