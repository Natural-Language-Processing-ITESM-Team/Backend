from asyncore import poll
from flask import request
from flask import Flask
import boto3
import json
from flask_cors import CORS
from transcribe_test import transcribe_file
from dotenv import load_dotenv
import os
from polly_test import get_polly_audio
from azure_speech_to_text import recognize_from_file


load_dotenv("secrets.env")

acces_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
session_token = os.getenv("AWS_SESSION_TOKEN")
region = os.getenv("REGION_NAME")

authenticated_client = boto3.client(
        "s3",
        aws_access_key_id=acces_key,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name=region
)

transcribe_client = boto3.client('transcribe',
        aws_access_key_id=acces_key,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name=region)

# LexV2 client uses 'lexv2-runtime'
lex_client = boto3.client('lexv2-runtime',
        aws_access_key_id=acces_key,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name=region)

polly_client = boto3.client('polly',
        aws_access_key_id=acces_key,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name=region)

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/getTranscription', methods=['POST'])
def getTranscription():
    global authenticated_client
    
    # The way to get my form fields
    #request.form[]

    file_key_json = request.get_json()

    file_key = file_key_json["key"]

    print(f"I server am going to ask for transcription for {file_key}")
    
    
    # PROCESS FOR AWS TRANSCRIPTION
    """
    file_uri = "s3://buketa/" + file_key
    print("I will place transcript in " + file_key[:-4] + "json")
    transcribe_file('Example-job', file_uri, transcribe_client, file_key[:-4] + "json")
    # store file in current folder.
    authenticated_client.download_file("buketa", file_key[:-4] + "json", "helloback.json")
    with open('helloback.json', 'r') as f:
        json_data = json.load(f)
    transcript = json_data["results"]["transcripts"][0]["transcript"]
    # Delete transcript object for next round.
    authenticated_client.delete_object(Bucket='buketa', Key=file_key)
    """

    # PROCESS FOR AZURE TRANSCRIPTION
     # Download audio file from s3.
    authenticated_client.download_file("buketa", file_key, "client.webm")
    # convert to wav.
    os.system('ffmpeg -i "client.webm" -vn "client.wav"')
    transcript = recognize_from_file("client.wav")
 
    authenticated_client.delete_object(Bucket='buketa', Key=file_key)

    # Remove files generated in previous steps (Azure).
    os.system('rm -rf client.wav')
    os.system('rm -rf client.webm')

    if len(transcript) == 0:
        transcript = "transcript empty"
    
    response = lex_client.recognize_text(
        botId='40JABLDQYI',
        botAliasId='TSTALIASID',
        localeId='en_US',
        sessionId="test_session2",
        text=transcript)
    print(f"prompt {transcript}")
    print(f"response {response}")

    if( 'messages' in response):
        polly_text = response['messages'][0]['content']
    else:
        polly_text = 'I didnt understand'

    print("message for polly", polly_text)

    link = get_polly_audio(polly_client, file_key[:-4] + "mp3", polly_text)
    return link
    # store file in current folder.
    # authenticated_client.download_file("buketa", file_key[:-4] + "mp3", "audio_for_client.mp3")

    #with open('audio_for_client.mp3', 'r') as f:
    #    return f

    

    

    

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=8000)