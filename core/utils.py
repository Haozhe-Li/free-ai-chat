import httpx

async def fetch(url: str, headers: dict, payload: dict):
    """
    Fetch data from the given url with headers and payload
    Input: url, headers, payload
    Output: response
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=10)
    return response