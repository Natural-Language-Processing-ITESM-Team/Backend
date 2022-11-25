import os
from dotenv import load_dotenv

from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import TextToSpeechV1

from amazon_web_services import AmazonWebServices

import random

load_dotenv("secrets.env")
AWS = AmazonWebServices()
def transcribe_audio_file(file_key):


    iam_authenticator = os.getenv("WATSON_STT_KEY")
    stt_url = os.getenv("WATSON_STT_URL")

    authenticator = IAMAuthenticator(iam_authenticator)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(stt_url)

    global AWS

    # Download audio file from s3.
    AWS.s3_client.download_file("buketa", file_key, "client.webm")

    with open("client.webm", 'rb') as f:
        res = stt.recognize(audio=f, content_type='audio/webm', model='es-MX_NarrowbandModel',
                            inactivity_timeout=-1).get_result()
    #print(F"THE WATSON SPEECH TO TEXT {res}")
    transcript = res['results'][0]['alternatives'][0]['transcript']
    confidence = res['results'][0]['alternatives'][0]['confidence']
    return transcript, confidence

def vocalize(text_for_client: str):
    tts_key = os.getenv("WATSON_TTS_KEY")
    tts_url = os.getenv("WATSON_TTS_URL")

    authenticator = IAMAuthenticator(tts_key)
    tts = TextToSpeechV1(authenticator=authenticator)
    tts.set_service_url(tts_url)



    with open("output.mp3", 'wb') as audio_file:
        res = tts.synthesize(text_for_client, accept='audio/mp3',
                             voice='es-ES_EnriqueV3Voice').get_result()
        audio_file.write(res.content)

    output_key = str(random.random())[2:] + ".mp3"
    global AWS
    AWS.s3_client.upload_file('output.mp3', 'buketa', output_key)
    return f"https://buketa.s3.amazonaws.com/{output_key}"