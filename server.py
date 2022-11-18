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
import dialogflow
from google.api_core.exceptions import InvalidArgument
from flask import jsonify
import time
import pymysql
import json
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from google.cloud import texttospeech
import google.cloud.texttospeech as tts
import meta_api

db_connection = pymysql.connect( \
    host="benchmarksdb.cn5bfishmmmb.us-east-1.rds.amazonaws.com", 
    user="admin", password="vpcOwnChunkCloud", db="Ultron", port=3306, autocommit=True)

db_cursor = db_connection.cursor()

load_dotenv("secrets.env")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'
DIALOGFLOW_PROJECT_ID = 'pr-ctica-1-gcji'
DIALOGFLOW_LANGUAGE_CODE = 'es'
SESSION_ID = 'me'


acces_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
session_token = os.getenv("AWS_SESSION_TOKEN")
region = os.getenv("REGION_NAME")

IBM_access_key = os.getenv('IAM_AUTHENTICATOR')
IBM_assistant = os.getenv('ASSISTANT_ID')

TOKEN = os.getenv('TOKEN')

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

@app.route("/sendWhatsappTest", methods=['GET'])
def sendWhatsappTest():
    target_number = request.args.get('target_number')
    message = request.args.get('message')
    meta_api.respondWhatsapp(target_number,message)
    return 'success', 200

@app.route("/sendMessengerTest", methods=['GET'])
def sendMessengerTest():
    target_PSID = request.args.get('PSID')
    message = request.args.get('message')
    meta_api.respondMessenger(target_PSID, message)
    return 'success', 200

@app.route("/webhook",methods=['POST'])
def webhook():
    content = request.get_json()
    print(content)
    return 'success',200

@app.route("/webhook",methods=['GET'])
def webhookVerification():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.token')
    if(not token):
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
    if(mode and token):
        if(mode == 'subscribe' and token == TOKEN):
            print('Webhook verified')
            return 'success', 200
    return 'error', 403

@app.route('/getTranscription', methods=['POST'])
def getTranscription():
    global authenticated_client
    print("route getTranscription")
    # The way to get my form fields
    #request.form[]

    incoming_json = request.get_json()

    file_key = incoming_json["key"]
    stt_measure = incoming_json["sttMeasure"]
    print(f"stt measure is {stt_measure}")

    print(f"I server am going to ask for transcription for {file_key}")
    
    global db_cursor

    # El famoso conmutador para stt
    db_cursor.execute( \
    """select s.name, avg(benchmarkValue) as avg_benchmark
        from Metrics as m, STTBenchmarks as b, STTServices as s 
        where m.metricId = b.metricId and s.STTServiceId = b.STTServiceId and m.name = "Latencia" 
        group by s.name
        order by avg_benchmark asc
        """)

    rows = db_cursor.fetchall()
    best_stt_service = rows[0][0]
    best_stt_benchmark = rows[0][1]
    # REMOVE THIS WHEN DONE TESTING
    #best_stt_service = "Transcribe" test
    if best_stt_service == "Azure":
        # PROCESS FOR AZURE TRANSCRIPTION
        # Download audio file from s3.
        authenticated_client.download_file("buketa", file_key, "client.webm")
        # convert to wav.
        os.system('ffmpeg -i "client.webm" -vn "client.wav"')
        transcript = recognize_from_file("client.wav")
        os.system('rm -rf client.wav')

    elif best_stt_service == "Transcribe":
        # PROCESS FOR AWS TRANSCRIPTION
        file_uri = "s3://buketa/" + file_key
        print("I will place transcript in " + file_key[:-4] + "json")
        transcribe_file('Example-job', file_uri, transcribe_client, file_key[:-4] + "json")
        # store file in current folder.
        authenticated_client.download_file("buketa", file_key[:-4] + "json", "helloback.json")
        with open('helloback.json', 'r') as f:
            json_data = json.load(f)
        transcript = json_data["results"]["transcripts"][0]["transcript"]
        
    
    # Remove files for all next rounds.
    authenticated_client.delete_object(Bucket='buketa', Key=file_key)
    os.system('rm -rf client.webm')

    if len(transcript) == 0:
        transcript = "transcript empty"
    
    # PROCESS FOR AMAZON LEX
    """response = lex_client.recognize_text(
        botId='40JABLDQYI',
        botAliasId='TSTALIASID',
        localeId='en_US',
        sessionId="test_session2",
        text=transcript)"""

    # PROCESS FOR GOOGLE DIALOGFLOW
    """print("Using Google Text to speech")
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
    text_input = dialogflow.types.TextInput(text=transcript, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise

    text_for_client = response.query_result.fulfillment_text"""


    # PROCESS FOR IBM WATSON
    authenticator = IAMAuthenticator(IBM_access_key)
    assistant = AssistantV2(
        version='2021-06-14',
        authenticator = authenticator
    )

    assistant.set_service_url('https://api.us-south.assistant.watson.cloud.ibm.com/instances/e0d095a7-17e0-4a51-b9e9-03b6552dd042')

    response = assistant.message_stateless(
        assistant_id=IBM_assistant,
        input={
            'message_type': 'text',
            'text': transcript
        }
    ).get_result()

    text_for_client = response['output']['generic'][0]['text']


    print(f"prompt {transcript}")
    print(f"response {text_for_client}")


    
    # AWS SPECIFIC
    """if( 'messages' in response):
        polly_text = response['messages'][0]['content']
    else:
        polly_text = 'I didnt understand'"""

    """print("message for polly", text_for_client)

    link = get_polly_audio(polly_client, file_key[:-4] + "mp3", text_for_client)
    #return jsonify({"link": link, "text": polly_text})"""



    # TTS FOR GOOGLE
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text_for_client)
    contador = 0
    def synthesize_text(text, contador):
        voice = texttospeech.VoiceSelectionParams(language_code="es-US",name="es-ES-Standard-A ",ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(request={"input": input_text, "voice": voice, "audio_config": audio_config})
        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
            out_file_key = file_key[:-5] + str(contador) + ".mp3"
            authenticated_client.upload_file('output.mp3', 'buketa', out_file_key)
            contador += 1
        return contador + 1, out_file_key
            #print('Audio content written to file "output.mp3"')

    contador, out_file_key = synthesize_text(input_text, contador)

    return f"http://us-east-1.amazonaws.com/buketa/{out_file_key}"


    # store file in current folder.
    # authenticated_client.download_file("buketa", file_key[:-4] + "mp3", "audio_for_client.mp3")

    #with open('audio_for_client.mp3', 'r') as f:
    #    return f

    

    

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=8000)