import io
import grpc
import pydub


import yandex.cloud.ai.tts.v3.tts_pb2 as tts_pb2
import yandex.cloud.ai.tts.v3.tts_service_pb2_grpc as tts_service_pb2_grpc


from config_reader import config


def synthesize(text, voice = 'marina', speed = 1, role = '') -> pydub.AudioSegment:
    request = tts_pb2.UtteranceSynthesisRequest(
        text=text,
        output_audio_spec=tts_pb2.AudioFormatOptions(
            container_audio=tts_pb2.ContainerAudio(
                container_audio_type=tts_pb2.ContainerAudio.WAV
            )
        ),
        # Параметры синтеза
        hints=[
          tts_pb2.Hints(voice= voice), # (Опционально) Задайте голос. Значение по умолчанию marina
          tts_pb2.Hints(role = role), # (Опционально) Укажите амплуа, только если голос их имеет
          tts_pb2.Hints(speed=speed) # (Опционально) Задайте скорость синтеза
        ],

        loudness_normalization_type=tts_pb2.UtteranceSynthesisRequest.LUFS
    )

    # Установите соединение с сервером.
    cred = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel('tts.api.cloud.yandex.net:443', cred)
    stub = tts_service_pb2_grpc.SynthesizerStub(channel)

    # Отправьте данные для синтеза.
    it = stub.UtteranceSynthesis(request, metadata=(

        ('authorization', f'Api-Key {config.api_tts}'),
    ))

    # Соберите аудиозапись по порциям.
    try:
        audio = io.BytesIO()
        for response in it:
            audio.write(response.audio_chunk.data)
        audio.seek(0)
        return pydub.AudioSegment.from_wav(audio)
    except grpc._channel._Rendezvous as err:
        print(f'Error code {err._state.code}, message: {err._state.details}')
        raise err




if __name__ == '__main__':\

    audio = synthesize("Привет, я - долбаеб, все хуйня, давай по новой")
    with open("output.wav", 'wb') as fp:
        audio.export(fp, format='wav')