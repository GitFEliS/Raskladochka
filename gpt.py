import asyncio
from asyncio import sleep

import httpx

from config_reader import config
from random_choice import tarot_deck
import requests

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
        "modelUri": f"gpt://{config.cloud_id}/yandexgpt-lite/latest",
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

def download_file(url):
    local_filename = url.split('/')[-1]

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def get_did_video(text):
    url = "https://api.d-id.com/talks"

    payload = {
        "script": {
            "type": "text",
            "provider": {
                "type": "microsoft",
                "voice_id": "ru-RU-SvetlanaNeural",
                "language": "Russian"
            },
            "input": text,
        },
        "source_url": "https://pic.uma.media/pic/video/6c/32/6c328e73c47f5eccd26d778917bcf519.jpg",

    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {key}"
    }

    response = requests.post(url, json=payload, headers=headers).json()
    print(response)
    if id not in response:
        return None, False
    talk_id = response["id"]
    url = f"https://api.d-id.com/talks/{talk_id}"
    headers = {
        "accept": "application/json",
        "authorization": f"Basic {key}"
    }
    response = requests.get(url, headers=headers).json()
    result_url = None
    for i in range(5):
        if 'result_url' not in response:
            sleep(5)
        else:
            result_url = response["result_url"]
            break
    if result_url is None:
        return None, False
    filepath = download_file(result_url)
    return filepath, True

if __name__ == "__main__":
    asyncio.run(generate_prediction("Когда Эмир встретит свою суженную",
                                     tarot_deck.random_choice()))
