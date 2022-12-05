""" This file contains the google cloud platform class that represents nlp capabilities with google cloud

Author: Luis Ignacio Ferro Salinas A01378248
Last update: december 4th, 2022
"""

# Standard library
import io
import os
import random

# 3rd party related libraries
import dialogflow
import google.cloud.texttospeech as tts
from google.api_core.exceptions import InvalidArgument
from google.cloud import speech_v1 as speech


class GoogleCloudPlatform:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../private_key.json"
        self.DIALOGFLOW_PROJECT_ID = "pr-ctica-1-gcji"
        self.DIALOGFLOW_LANGUAGE_CODE = "es"
        self.SESSION_ID = "me"

    def transcribe_audio_file(self, file_key, AWS):
        # file_uri = "s3://buketa/" + file_key
        client = speech.SpeechClient()

        # Download audio file from s3.
        # print(f"in google stt, key is {file_key}")

        file_name = file_key[11:]
        AWS.s3_client.download_file("buketa", file_key, file_name)
        # convert to wav.
        # os.system('ffmpeg -i "client.webm" -vn "client.wav"')

        with io.open(file_name, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="es-MX",
        )

        response = client.recognize(config=config, audio=audio)

        for result in response.results:
            best_alternative = result.alternatives[0]
            transcript = best_alternative.transcript
            confidence = best_alternative.confidence
            print("-" * 80)
            print(f"Transcript: {transcript}")
            print(f"Confidence: {confidence:.0%}")

            return transcript, confidence
        return "", 0.5

    def converse_back(self, client_string, client_id):
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(self.DIALOGFLOW_PROJECT_ID, client_id)
        text_input = dialogflow.types.TextInput(
            text=client_string, language_code=self.DIALOGFLOW_LANGUAGE_CODE
        )
        query_input = dialogflow.types.QueryInput(text=text_input)
        try:
            response = session_client.detect_intent(
                session=session, query_input=query_input
            )
        except InvalidArgument:
            raise

        text_for_client = ""
        for json_msg in response.query_result.fulfillment_messages:
            # print(dir(json_msg.text))
            text_for_client += json_msg.text.text[0]
            # text_for_client += json_msg.text

        # text_for_client = response.query_result.fulfillment_text
        return text_for_client

    def vocalize(self, text_for_client, AWS):
        language_code = "-".join("es-US-Neural2-A".split("-")[:2])
        text_input = tts.SynthesisInput(text=text_for_client)
        voice_params = tts.VoiceSelectionParams(
            language_code=language_code, name="es-US-Neural2-A"
        )
        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

        client = tts.TextToSpeechClient()
        response = client.synthesize_speech(
            input=text_input, voice=voice_params, audio_config=audio_config
        )

        filename = str(random.random())[2:] + ".wav"

        with open(filename, "wb") as out:
            out.write(response.audio_content)
            # print(f'Generated speech saved to "{filename}"')
        output_key = "transcribe/" + filename
        AWS.s3_client.upload_file(filename, "buketa", output_key)

        os.system(f"rm -rf {filename}")

        return f"https://buketa.s3.amazonaws.com/{output_key}"


config = dict(language_code="es-MX")
audio = dict(uri="gs://cloud-samples-data/speech/brooklyn_bridge.flac")
