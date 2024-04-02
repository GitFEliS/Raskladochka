import httpx
import os


API_KEY = os.getenv("API_KEY", "")


class GenerationException(Exception):
    ...


async def generate_prediction(question: str, cards: list[str]) -> str:
    if not question.endswith("?"):
        question += "?"

    url = r"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    header = {"Authorization": f"Api-Key {API_KEY}"}
    body = {
        "modelUri": "gpt://b1g4e6ia9qvtoa4l2f0c/yandexgpt-lite/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.5,
            "maxTokens": 1000
        },
        "messages": [
            {
                "role": "system",
                "text": f"""
                Ты — гадалка, которая делает предсказания на картах таро.
                Тебе задали вопрос: "{question}"
                Тебе выпали карты таро: {", ".join(cards)}
                Объясни свое гадание, опираясь на выпавшие карты.
                """
            },
            {
                "role": "system",
                "text": """
                Ответ дай в формате:
                Выпали карты: "названия карт".
                Толкование каждой из карт.
                Вывод.
                """
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
            raise GenerationException("YandexGPT failed to generate answer")
    return "\n".join(res)
