import wikipedia
import os
import asyncio
import json
import logging
from core.utils import fetch
from core.prompts import keywordPrompt, ragPromptTemplate


async def search_wiki(query: list) -> dict:
    """
    Search Wikipedia for the query and return the summary, url and title
    Input: query
    Output: result
    """
    result = {}
    for q in query:
        try:
            searching_results = wikipedia.search(q)
            if len(searching_results) > 0:
                searching_result = searching_results[0]
                summary = (
                    wikipedia.summary(searching_result)[0:5000] + "..."
                    if len(wikipedia.summary(searching_result)) > 5000
                    else wikipedia.summary(searching_result)
                )
                url = wikipedia.page(searching_result).url
                title = wikipedia.page(searching_result).title
                result[q] = {"summary": summary, "url": url, "title": title}
        except Exception as e:
            continue
    return result


async def generate_keywords(input_text: str) -> list:
    """
    Generate keywords for the input_text
    Input: input_text
    Output: keywords
    """

    # Generate keywords for the input_text
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
                "content": keywordPrompt,
            },
            {
                "role": "user",
                "content": input_text,
            },
        ],
        "response_format": {"type": "json_object"},
    }

    # Fetch the response
    response = await fetch(groq_url, headers, payload)
    if response.status_code != 200:
        return []
    response = json.loads(response.json()["choices"][0]["message"]["content"])[
        "keywords"
    ]
    return response


async def rag_search(input_text: str, task_id: str = "") -> dict:
    """
    Search Wikipedia for the input_text and return the result
    Input: input_text
    Output: ragPrompt"""

    # Search Wikipedia for the input_text
    logging.info(
        f"[rag.py] RAG search with input_text with task_id: {task_id}. {input_text}"
    )
    ragPrompt = ragPromptTemplate
    reference = ""
    keywords = await generate_keywords(input_text)
    if keywords == []:
        logging.error(
            f"[rag.py] No keywords generated for input_text with task_id: {task_id}. {input_text}"
        )
        return ""
    search_result = await search_wiki(keywords)
    if len(search_result) == 0:
        logging.error(
            f"[rag.py] No search result found for keywords with task_id: {task_id}. {keywords}"
        )
        return ""
    for key, value in search_result.items():
        ragPrompt += f"\n\nResult for {key}: \n\nSummary: {value['summary']},\n\nURL: {value['url']},\n\n Title: {value['title']} - Wikipedia"
        reference += (
            f"""<br><i><a href="{value['url']}">{value['title']} - Wikipedia</a></i>"""
        )
    logging.info(
        f"[rag.py] RAG search result  with task_id: {task_id}. {str(ragPrompt)[0:50]}"
    )
    return {"ragprompt": ragPrompt, "reference": "<br><br><b>Reference</b>" + reference}


if __name__ == "__main__":
    print(asyncio.run(rag_search("What is seattle?")))
