import json
import logging
import os
import subprocess
import time

import httpx
import jwt
import requests

from config_reader import config

SAMPLE_RATE = 48_000
TOO_FEW_TIME_BEFORE_INVALIDATION = 60_000
SYNTH_RES_DIR = "synth_result"
if not os.path.exists(SYNTH_RES_DIR):
    os.makedirs(SYNTH_RES_DIR)


class TTSProvider:

    def __init__(self):
        self.access_token = None
        self.access_token_expiration = None

    def is_token_valid(self):
        if self.access_token is None:
            return False
        time_before_invalidation = time.time() - self.access_token_expiration
        return time_before_invalidation > TOO_FEW_TIME_BEFORE_INVALIDATION

    def get_access_token(self):
        if not self.is_token_valid():
            self.update_token()

        return self.access_token

    def update_token(self):
        service_account_id = config.yandex_service_account_id
        key_id = config.yandex_service_account_key_id

        with open(".creds/authorized_key.json", 'r') as authorized_key:
            private_key = json.load(authorized_key)["private_key"]

        now = int(time.time())
        payload = {
            'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            'iss': service_account_id,
            'iat': now,
            'exp': now + 360}

        # Формирование JWT.
        encoded_token = jwt.encode(
            payload,
            private_key,
            algorithm='PS256',
            headers={'kid': key_id})

        url = r"https://iam.api.cloud.yandex.net/iam/v1/tokens"
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "jwt": encoded_token
        }

        token_data = httpx.post(url=url,
                                headers=headers,
                                json=body,
                                timeout=30).json()

        self.access_token = token_data["iamToken"]
        self.access_token_expiration = token_data["expiresAt"]

    def synthesize(self, text, request_id="test"):
        url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
        iam_token = self.get_access_token()
        headers = {
            'Authorization': 'Bearer ' + iam_token,
        }

        data = {
            'text': text,
            'lang': 'ru-RU',
            'voice': 'filipp',
            'folderId': config.yandex_folder_id,
            'format': 'lpcm',
            'sampleRateHertz': SAMPLE_RATE,
        }

        with requests.post(url, headers=headers, data=data, stream=True) as resp:
            if resp.status_code != 200:
                raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

            raw_output = f"{SYNTH_RES_DIR}/{request_id}.raw"
            with open(raw_output, "wb") as out:
                for chunk in resp.iter_content(chunk_size=None):
                    out.write(chunk)

        gen_start = time.time()
        logging.info("Начали генерировать говорящую голову")

        # Превращаем хрень в wav
        wav_output = f"{SYNTH_RES_DIR}/{request_id}.wav"
        subprocess.call(f"sox -r 48000 -b 16 -e signed-integer -c 1 {raw_output} {wav_output}", shell=True)
        # subprocess.call(f"pwd && cd ../SadTalker && pwd "
        #                 + "&& conda env list "
        #                 + "&& conda activate sadtalker "  # TODO: я хз, можно ли как-то в отдельном потоке стартануть
        #                 + f"&& python inference.py --driven_audio ../Raskladochka/{wav_output} "
        #                 + "--source_image samples/facegen.mp4 "
        #                 + "--still --preprocess full --enhancer gfpgan",
        #                 shell=True)
        logging.info(f"Закончили генерировать говорящую голову за {(time.time() - gen_start) // 1_000} секунд")


tts_provider = TTSProvider()

if __name__ == "__main__":
    text_to_speech = """
            Колода дала мне карты: Пятерка Кубков, Паж Пентаклей, Туз Мечей.
            Карты говорят мне, что Эмир встретит свою суженную, когда он будет готов отпустить прошлое и принять перемены.
            Паж Пентаклей символизирует новые начинания и возможности, а Туз Мечей указывает на ясность и решительность.
            Однако, Пятерка Кубков напоминает о том, что нужно быть готовым к трудностям и потерям,
            прежде чем встретить свою любовь.
            """
    tts_provider.synthesize(text_to_speech)
