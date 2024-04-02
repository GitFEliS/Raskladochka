import asyncio

import httpx

from config_reader import config
from random_choice import tarot_deck


class GenerationException(Exception):
    ...


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
                Ответ дай в формате:
                Вам выпали карты: "названия карт".
                Толкование каждой из карт в контексте поставленного вопроса.
                Вывод.
                """


async def generate_prediction(question: str, cards: list[str]) -> str:
    url = r"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    header = {"Authorization": f"Api-Key {config.api_key}"}
    body = {
        "modelUri": "gpt://b1g4e6ia9qvtoa4l2f0c/yandexgpt-lite/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.9,
            "maxTokens": 1000
        },
        "messages": [
            {
                "role": "system",
                "text": question_prompt(question, cards)
            },
            {
                "role": "system",
                "text": answer_requirements_prompt()
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        res_dict = (await client.post(url=url, headers=header, json=body, timeout=30)).raise_for_status().json()
    messages = res_dict['result']['alternatives']
    res = []
    for message in messages:
        info, status = message["message"], message["status"]
        if status in ("ALTERNATIVE_STATUS_PARTIAL", "ALTERNATIVE_STATUS_FINAL"):
            res.append(info['text'])
        else:
            print(info)
            raise GenerationException("YandexGPT failed to generate answer")

    return "\n".join(res)


if __name__ == "__main__":
    asyncio.run(generate_prediction("Когда Эмир встретит свою суженную",
                                    tarot_deck.random_choice()))
