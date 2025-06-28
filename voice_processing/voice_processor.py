import speech_recognition as sr
from google.cloud import speech
import io

def clean_command(command):
    unwanted = ['@', '#', 'as', 'at', 'the', 'rate']
    for word in unwanted:
        command = command.replace(word, '')
    return command.strip()

def process_voice_command():
    client = speech.SpeechClient()
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    audio_content = audio.get_wav_data()
    audio_file = io.BytesIO(audio_content)
    audio_file.seek(0)

    audio = speech.RecognitionAudio(content=audio_file.read())
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        command = result.alternatives[0].transcript
        return clean_command(command)
