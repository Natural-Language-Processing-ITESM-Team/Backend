import os
from dotenv import load_dotenv

from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from amazon_web_services import AmazonWebServices



def transcribe_audio_file(file_key):
    load_dotenv("secrets.env")

    iam_authenticator = os.getenv("IAM_AUTHENTICATOR")
    stt_url = os.getenv("WATSON_STT_URL")

    authenticator = IAMAuthenticator(iam_authenticator)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(stt_url)

    AWS = AmazonWebServices()

    # Download audio file from s3.
    AWS.s3_client.download_file("buketa", file_key, "client.webm")

    with open("client.webm", 'rb') as f:
        res = stt.recognize(audio=f, content_type='audio/webm', model='es-MX_NarrowbandModel',
                            inactivity_timeout=-1).get_result()

    transcript = res['results'][0]['alternatives'][0]['transcript']
    return transcript