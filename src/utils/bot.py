from anthropic import Anthropic
import json


class ContextualChatbot:
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)
        self.messages = []
        self.system_prompt = ""

    def set_system_prompt(self, context):
        """Postavlja system prompt"""
        self.system_prompt = context

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
            system=self.system_prompt,  # System prompt kao zaseban parametar
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
    chatbot = ContextualChatbot("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")

    # Postavi system prompt
    chatbot.set_system_prompt("""
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


if __name__ == "__main__":
    main()
