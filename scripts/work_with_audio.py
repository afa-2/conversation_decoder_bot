from openai import OpenAI


def get_text_from_audio(open_ai_key, path_to_file):
    """
    Функция принимает аудиофайл и возвращает текст
    """
    client = OpenAI(api_key=open_ai_key)

    audio_file= open(path_to_file, "rb")
    transcription = client.audio.transcriptions.create(
      model="whisper-1",
      file=audio_file
    )

    return transcription.text

