import asyncio

from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

from config_reader import config
from random_choice import tarot_deck

chat = GigaChat(credentials=config.gigachat_auth_data, verify_ssl_certs=False)


def question_prompt(question: str, cards: list[str]) -> str:
    if not question.endswith("?"):
        question += "?"

    return f"""
                Ты — гадалка, которая делает предсказания на картах таро.
                Тебе задали вопрос: "{question}"
                Тебе выпали карты таро: {", ".join(cards)}
                Объясни свое гадание, опираясь на выпавшие карты.
                Не забудь дать толкование каждой карты в контексте поставленного вопроса.
                Не пиши ничего, что может заставить сомневаться в предсказании
                Твое гадание - абсолютная истина и ты не ошибаешься
                """


def answer_requirements_prompt() -> str:
    return """ 
                В ответе сначала перечисли карты, которые выпали в колоде таро. 
                Для каждой карты одним предложением скажи её значение.
                Закончи свой ответ предсказанием, которое начинается с фразы "Карты сказали мне, что".
                В ответе должно быть не больше 500 символов.
                """


async def generate_prediction(question: str, cards: list[str]) -> str:
    messages = [
        SystemMessage(question_prompt(question, cards)),
        HumanMessage(answer_requirements_prompt())
    ]
    rs = chat(messages)
    return rs.content


def main():
    question = "Когда Эмир найдет свою суженую?"
    prediction = asyncio.run(generate_prediction(question, [c.name for c in tarot_deck.random_choice()]))
    print(f"{question}?\n{prediction}")


if __name__ == "__main__":
    main()
