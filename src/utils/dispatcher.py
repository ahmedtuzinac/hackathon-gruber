import os

import httpx
import anthropic

data_source_api_base_url: str = os.getenv('data_source_api_base_url')


async def get_data_from_base(endpoint: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            data_source_api_base_url + endpoint
        )

    return response.json()


async def get_available_cities():
    url = '/Helper/GetAvailableCities'
    return await get_data_from_base(
        endpoint=url
    )


async def get_partners():
    url = '/Supplier/GetAllSuppliers'
    return await get_data_from_base(
        endpoint=url
    )


async def get_transport_history():
    url = '/Transport/GetTransportHistory'
    return await get_data_from_base(
        endpoint=url
    )


async def set_task(message: str):
    client = anthropic.Anthropic(
        api_key=os.getenv('api-key'),
    )

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
        ]
    )
    return message.content


async def set_task_gemini(message: str):
    import google.generativeai as genai

    genai.configure(api_key="AIzaSyBYIy72IoIjPg276b2zihYy6dcJ_ZgACOs")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(message)

    return response.text

