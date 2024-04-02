import asyncio

from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

from config_reader import config
from gpt import answer_requirements_prompt, question_prompt
from random_choice import tarot_deck

chat = GigaChat(credentials=config.gigachat_auth_data, verify_ssl_certs=False)


async def generate_prediction(question: str, cards: list[str]) -> str:
    messages = [
        SystemMessage(question_prompt(question, cards)),
        HumanMessage(answer_requirements_prompt())
    ]
    rs = chat(messages)
    return rs.content


def main():
    question = "Когда Эмир встретит свою суженную"
    prediction = asyncio.run(generate_prediction(question, tarot_deck.random_choice()))
    print(f"{question}?\n{prediction}")


if __name__ == "__main__":
    main()
