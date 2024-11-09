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


from anthropic import Anthropic
import json

api_key = os.getenv('api-key')


class ContextualChatbot:
    def init(self, api_key):
        self.client = Anthropic(api_key=api_key)
        self.messages = []

    def add_context(self, context):
        """Dodaje sistemski kontekst na početak konverzacije"""
        system_message = {
            "role": "system",
            "content": context
        }
        self.messages = [system_message] + self.messages

    def add_knowledge(self, knowledge):
        """Dodaje znanje kao assistant poruku"""
        assistant_message = {
            "role": "assistant",
            "content": f"Zapamtiću sledeće informacije: {knowledge}"
        }
        self.messages.append(assistant_message)

    def ask_question(self, question):
        """Postavlja pitanje uzimajući u obzir prethodni kontekst"""
        self.messages.append({
            "role": "user",
            "content": question
        })

        response = self.client.messages.create(
            model="claude-3-opus-20240229",
            messages=self.messages,
            max_tokens=1000,
        )

        # Dodaj odgovor u istoriju
        self.messages.append({
            "role": "assistant",
            "content": response.content[0].text
        })

        return response.content[0].text


# Primer korišćenja
def main():
    chatbot = ContextualChatbot(api_key)

    # Dodaj osnovni kontekst
    chatbot.add_context("""
    Ti si asistent koji pomaže u prodaji nekretnina.
    Imaš pristup informacijama o stanovima u Beogradu.
    Uvek odgovaraš na srpskom jeziku.
    """)

    # Dodaj specifične informacije o nekretninama
    chatbot.add_knowledge("""
    Dostupni stanovi:
    1. Novi Beograd, Blok 63, 55m2, 2.0, 120000€
    2. Vračar, Njegoševa, 65m2, 2.5, 180000€
    3. Zemun, Glavna, 45m2, 1.5, 85000€
    """)

    # Postavi pitanje
    odgovor = chatbot.ask_question("Koji stanovi su dostupni na Novom Beogradu?")
    print("Odgovor:", odgovor)

    # Postavi follow-up pitanje
    odgovor = chatbot.ask_question("Koji je najjeftiniji stan?")
    print("Odgovor:", odgovor)


if __name__ == '__main__':
    main()