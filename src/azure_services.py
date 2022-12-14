import os

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv("secrets.env")
import random

from src.amazon_web_services import AmazonWebServices


def transcribe_audio_file(file_key):
    azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
    azure_region = os.getenv("AZURE_SPEECH_REGION")
    AWS = AmazonWebServices()
    file_name = file_key[11:]
    print("------------------------- ")
    print(f"attempting to download file into: {file_name}")
    print("------------------------- ")
    AWS.s3_client.download_file("buketa", file_key, file_name)

    os.system(f'ffmpeg -i "{file_name}" -vn "{file_name[:-5] + ".wav"}"')

    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=azure_speech_key, region=azure_region
    )
    speech_config.speech_recognition_language = "es-MX"

    audio_config = speechsdk.audio.AudioConfig(filename=file_name[:-5] + ".wav")
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )

    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    os.system(f'rm -rf "{file_name}')
    os.system(f'rm -rf "{file_name[:-5] + ".wav"}"')
    print("AZURE TRANSCRIPTION COMPLETE")
    print(f"AZURE SPEECH TO TEXT RESPONSE {speech_recognition_result}")
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return speech_recognition_result.text, 0.5
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print(
            "No speech could be recognized: {}".format(
                speech_recognition_result.no_match_details
            )
        )
        return "", 0.5
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    return


def vocalize(text_for_client, AWS):
    azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
    azure_region = os.getenv("AZURE_SPEECH_REGION")

    # AWS.s3_client.download_file("buketa", file_key, "client.webm")

    # os.system('ffmpeg -i "client.webm" -vn "client.wav"')
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=azure_speech_key, region=azure_region
    )

    filename = str(random.random())[2:] + ".wav"

    # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = "es-MX-JorgeNeural"

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )

    speech_synthesis_result = speech_synthesizer.speak_text_async(text_for_client).get()

    AWS.s3_client.upload_file(filename, "buketa", f"transcribe/{filename}")

    os.system(f"rm -rf {filename}")

    return f"https://buketa.s3.amazonaws.com/{'transcribe/' + filename}"
