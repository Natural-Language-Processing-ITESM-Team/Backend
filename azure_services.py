import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv("secrets.env")



def transcribe_audio_file(file_key, AWS):
    azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
    azure_region = os.getenv("AZURE_SPEECH_REGION")

    AWS.s3_client.download_file("buketa", file_key, "client.webm")

    os.system('ffmpeg -i "client.webm" -vn "client.wav"')


    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=azure_speech_key,
                                           region=azure_region)
    speech_config.speech_recognition_language = "es-MX"

    audio_config = speechsdk.audio.AudioConfig(filename="client.wav")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    print(F"AZURE SPEECH TO TEXT RESPONSE {speech_recognition_result}")
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return speech_recognition_result.text, 0.5
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    return









"""


# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription=azure_speech_key,
                                       region=azure_region)
# audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
audio_config = speechsdk.audio.AudioOutputConfig(filename="client.wav")

# The language of the voice that speaks.
speech_config.speech_synthesis_voice_name = 'es-MX-JorgeNeural'

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

# Get text from the console and synthesize to the default speaker.
text = 'Inserte su texto'

speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")"""