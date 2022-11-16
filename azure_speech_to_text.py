# pip install azure-cognitiveservices-speech

import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
#import boto3
#import os



load_dotenv("secrets.env")

speech_key = os.environ.get('AZURE_SPEECH_KEY')
azure_region = os.environ.get('AZURE_SPEECH_REGION')

def recognize_from_file(file_name):
    print(f"azure key {speech_key}")
    print(f"azure region {azure_region}")
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=azure_region)
    speech_config.speech_recognition_language="es-MX"

    audio_config = speechsdk.AudioConfig(filename=file_name)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    return ""
