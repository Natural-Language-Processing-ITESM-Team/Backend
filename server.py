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
import time
from bertopic import BERTopic

active_bot = False
current_topic = None
# Local related imports
from amazon_web_services import AmazonWebServices
from google_cloud_platform import GoogleCloudPlatform

db_connection   = pymysql.connect( \
    host="database-benchmarks.cn5bfishmmmb.us-east-1.rds.amazonaws.com", 
    user="admin", password="vpcOwnChunkCloud", db="benchmarksDB", port=3306, autocommit=True)

db_cursor = db_connection.cursor()

load_dotenv("secrets.env")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'
DIALOGFLOW_PROJECT_ID = 'pr-ctica-1-gcji'
DIALOGFLOW_LANGUAGE_CODE = 'es'
SESSION_ID = 'me'


IBM_access_key = os.getenv('IAM_AUTHENTICATOR')
IBM_assistant = os.getenv('ASSISTANT_ID')

TOKEN = os.getenv('TOKEN')

app = Flask(__name__)
CORS(app)

AWS = AmazonWebServices()
GCP = GoogleCloudPlatform()

def choose_cloud_converse_back(client_query: str) -> str:
    # CHOOSE WITH THE MODEL
    modelo = BERTopic.load("BERTopicv1")

    global active_bot
    if not active_bot:
        model_inference = modelo.find_topics(client_query)
        active_bot = True
        current_topic = model_inference[0][0]

    # TODO if model_inference is topic 1 then lex else google algo así.
    print(f"most likely topic is {current_topic}")
    if current_topic == 3:
        # PROCESS FOR GOOGLE DIALOGFLOW
        text_for_client = GCP.converse_back(client_query)
    elif current_topic == 4:
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
                'text': client_query
            }
        ).get_result()

        text_for_client = response['output']['generic'][0]['text']

    elif current_topic == 2:
        # PROCESS FOR AMAZON LEX
        text_for_client = AWS.converse_back(client_query)

    if text_for_client == "gracias por su preferencia":
        active_bot = False
        
    return text_for_client


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

@app.route('/utterTextFromText', methods=["POST"])
def utterTextFromText():
    incoming_json = request.get_json()
    client_query = incoming_json["clientQuery"]
    text_for_client = choose_cloud_converse_back(client_query)
    return text_for_client


@app.route('/getTranscription', methods=['POST'])
def getTranscription():

    global AWS
    global GCP
    print("route getTranscription")
    # The way to get my form fields
    #request.form[]

    incoming_json = request.get_json()

    file_key = incoming_json["key"]
    stt_measure = incoming_json["sttMeasure"]
    tts_measure = incoming_json["ttsMeasure"]
    #stt_measure = "latency"
    print(f"stt measure is {stt_measure}")
    print(f"tts measure is {tts_measure}")

    print(f"I server am going to ask for transcription for {file_key}")

    # El famoso conmutador para stt
    global db_cursor
    if stt_measure == "Latencia":

        db_cursor.execute( \
            """select s.name, avg(benchmarkValue) as avg_benchmark
                from Metrics as m, STTBenchmarks as b, STTServices as s 
                where m.metricId = b.metricId and s.STTServiceId = b.STTServiceId and m.name = "Latencia" 
                group by s.name
                order by avg_benchmark asc
                """)
    elif stt_measure == "Exactitud":
        db_cursor.execute( \
            """select s.name, avg(benchmarkValue) as avg_benchmark
                from Metrics as m, STTBenchmarks as b, STTServices as s 
                where m.metricId = b.metricId and s.STTServiceId = b.STTServiceId and m.name = "Exactitud" 
                group by s.name
                order by avg_benchmark desc
                """)
    elif stt_measure == "Costo":
        db_cursor.execute( \
            """select s.name, avg(benchmarkValue) as avg_benchmark
                from Metrics as m, STTBenchmarks as b, STTServices as s 
                where m.metricId = b.metricId and s.STTServiceId = b.STTServiceId and m.name = "Costo" 
                group by s.name
                order by avg_benchmark asc
                """)

    rows = db_cursor.fetchall()
    best_stt_service = rows[0][0]
    best_stt_benchmark = rows[0][1]
    print(f"best stt service for {stt_measure} is {best_stt_service}")

    # El famoso conmutador para tts
    if tts_measure == "Latencia":
        db_cursor.execute( \
            """select s.name, avg(benchmarkValue) as avg_benchmark
                from Metrics as m, TTSBenchmarks as b, TTSServices as s 
                where m.metricId = b.metricId and s.TTSServiceId = b.TTSServiceId and m.name = "Latencia" 
                group by s.name
                order by avg_benchmark asc
                """)
    elif tts_measure == "Costo":
        db_cursor.execute( \
            """select s.name, avg(benchmarkValue) as avg_benchmark
                from Metrics as m, TTSBenchmarks as b, TTSServices as s 
                where m.metricId = b.metricId and s.TTSServiceId = b.TTSServiceId and m.name = "Costo" 
                group by s.name
                order by avg_benchmark asc
                """)

    rows = db_cursor.fetchall()
    best_tts_service = rows[0][0]
    best_tts_benchmark = rows[0][1]
    print(f"best stt service for {tts_measure} is {best_tts_service}")


    # REMOVE THIS WHEN DONE TESTING
    #best_stt_service = "Google"
    """if best_stt_service == "Azure":
        # PROCESS FOR AZURE TRANSCRIPTION
        # Download audio file from s3.
        s3_client.download_file("buketa", file_key, "client.webm")
        # convert to wav.
        os.system('ffmpeg -i "client.webm" -vn "client.wav"')
        transcript = recognize_from_file("client.wav")
        os.system('rm -rf client.wav')"""
    stt_start_time = time.time()

    if best_stt_service == "Transcribe":
        # PROCESS FOR AWS TRANSCRIPTION
        transcript = AWS.transcribe_audio_file('Example-job', file_key, file_key[:-4] + "json")
    elif best_stt_service == "GoogleSTT":
        transcript = GCP.transcribe_audio_file(file_key, AWS)

    stt_latency = (time.time() - stt_start_time) * 1000
    print(f"stt latency is {stt_latency}")

    print("I'm going to insert the latency of stt into database.")

    if stt_measure == "Latency":
        db_cursor.execute( \
            f"""
            INSERT INTO STTBenchmarks (metricId, STTServiceId, benchmarkValue) 
            VALUES ((SELECT metricId FROM Metrics WHERE name = "{stt_measure}"), 
                    (SELECT STTServiceId FROM STTServices WHERE name = "{best_stt_service}"), 
                    {stt_latency})
            """)
    elif stt_measure == "Exactitud":
        #TODO
        pass

    print(f"prompt {transcript}")
    # Remove files for all next rounds.
    #AWS.delete_object(file_key) amazon needs it kind of

    #os.system('rm -rf client.webm') probably azure needs it

    if not transcript: # None or empty sequence
        transcript = "transcript empty"


    text_for_client = choose_cloud_converse_back(transcript)



    print(f"response {text_for_client}")

    tts_start_time = time.time()
    if best_tts_service == "Polly":
        # AWS TTS
        audio_response_link = AWS.vocalize(text_for_client, file_key[:-4] + "mp3")
    elif best_tts_service == "GoogleTTS":
        # TTS FOR GOOGLE
        audio_response_link = GCP.vocalize(text_for_client, AWS)

    tts_latency = (time.time() - tts_start_time) * 1000

    if tts_measure == "Latency":
        db_cursor.execute( \
            f"""
            INSERT INTO TTSBenchmarks (metricId, TTSServiceId, benchmarkValue) 
            VALUES ((SELECT metricId FROM Metrics WHERE name = "{tts_measure}"), 
                    (SELECT TTSServiceId FROM TTSServices WHERE name = "{best_tts_service}"), 
                    {tts_latency})
            """)
    return audio_response_link
    #return {"audio_response_link": audio_response_link, "text_for_client": text_for_client}


    # store file in current folder.
    # authenticated_client.download_file("buketa", file_key[:-4] + "mp3", "audio_for_client.mp3")

    #with open('audio_for_client.mp3', 'r') as f:
    #    return f

    

    

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=8000)