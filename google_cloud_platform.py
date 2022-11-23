""" This file contains the google cloud platform class that represents nlp capabilities with google cloud

Author: Luis Ignacio Ferro Salinas A01378248
Last update: november 21st, 2022
"""
# Standard library
import os
import random
import io
# 3rd party related libraries
import dialogflow
from google.api_core.exceptions import InvalidArgument
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech

class GoogleCloudPlatform:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'
        self.DIALOGFLOW_PROJECT_ID = 'pr-ctica-1-gcji'
        self.DIALOGFLOW_LANGUAGE_CODE = 'es'
        self.SESSION_ID = 'me'

    def transcribe_audio_file(self, file_key, AWS):
        file_uri = "s3://buketa/" + file_key
        client = speech.SpeechClient()

        # Download audio file from s3.
        AWS.s3_client.download_file("buketa", file_key, "client.webm")
        # convert to wav.
        #os.system('ffmpeg -i "client.webm" -vn "client.wav"')

        with io.open("client.webm", "rb") as audio_file:
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

            return transcript

    def converse_back(self, client_string):
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(self.DIALOGFLOW_PROJECT_ID, self.SESSION_ID)
        text_input = dialogflow.types.TextInput(text=client_string, language_code=self.DIALOGFLOW_LANGUAGE_CODE)
        query_input = dialogflow.types.QueryInput(text=text_input)
        try:
            response = session_client.detect_intent(session=session, query_input=query_input)
        except InvalidArgument:
            raise
        print(response.query_result.fulfillment_messages)
        text_for_client = response.query_result.fulfillment_text
        return text_for_client

    def synthesize_text(self, input_text, client, AWS, output_key):
        voice = texttospeech.VoiceSelectionParams(language_code="es-US", name="es-ES-Standard-A ",
                                                  ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(request={"input": input_text, "voice": voice, "audio_config": audio_config})
        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
            #out_file_key = file_key[:-5] + str(contador) + ".mp3"
            AWS.s3_client.upload_file('output.mp3', 'buketa', output_key)


        # print('Audio content written to file "output.mp3"')

    def vocalize(self, text_for_client, AWS):
        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=text_for_client)

        output_key = str(random.random())[2:] + ".mp3"

        self.synthesize_text(input_text, client, AWS, output_key)
        return f"https://buketa.s3.amazonaws.com/{output_key}"







config = dict(language_code="es-MX")
audio = dict(uri="gs://cloud-samples-data/speech/brooklyn_bridge.flac")