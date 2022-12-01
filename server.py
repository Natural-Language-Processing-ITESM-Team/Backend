import os
import time
import requests

import pymysql
from bertopic import BERTopic
from dotenv import load_dotenv
from flask import Flask
from flask import request
from flask_cors import CORS
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2

import meta_api
from watson_stt import transcribe_audio_file, vocalize
from azure_services import transcribe_audio_file as azure_transcribe_audio_file

#active_bot = False
#current_topic = None
# Local related imports
from amazon_web_services import AmazonWebServices
from google_cloud_platform import GoogleCloudPlatform
from azure_services import vocalize as azure_vocalize

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
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')

app = Flask(__name__)
CORS(app)

AWS = AmazonWebServices()
GCP = GoogleCloudPlatform()

from enum import Enum

class Topics(Enum):
    ESPORTS = 0
    SUPPORT = 1
    CAREERS = 2
    GRADUATES = 3
    ADMISSIONS = 4
    UNCLASSIFIED = -1


"""
class DBQueryHandler:
    def __init__(self):
        self._db_cursor #

    def get_latencia(self, stt_..):
         # holds query
        retur
"""
def choose_cloud_converse_back(client_query: str, client_id, current_topic, from_social_media: bool) -> str:
    # CHOOSE WITH THE MODEL
    modelo = BERTopic.load("BERTopicv1")
    print("-------------------------------")
    print(f"Received topic {current_topic}")
    print("-------------------------------")


    if current_topic == -2 or client_query == "":
        model_inference = modelo.find_topics(client_query)
        #active_bot = True
        current_topic = model_inference[0][0]

    # TODO if model_inference is topic 1 then lex else google algo así.
    print(f"most likely topic is {current_topic}")
    if current_topic == 3:
        # PROCESS FOR GOOGLE DIALOGFLOW
        print("-------------------------------")
        print("Calling for chatbot Dialogflow")
        print("-------------------------------")
        text_for_client = GCP.converse_back(client_query, client_id)
    elif current_topic == 4:  # admissions
        text_for_client = handle_admissions(client_query)
        print("-------------------------------")
        print("Calling for chatbot Watson Assistant")
        print("-------------------------------")
        #text_for_client = response['output']['generic'][0]['text']
    elif current_topic == 2:
        # PROCESS FOR AMAZON LEX
        print("-------------------------------")
        print("Calling for chatbot Amazon Lex")
        print("-------------------------------")
        text_for_client = AWS.converse_back(client_query, client_id)
        print("chat response is ", text_for_client)

    elif current_topic == -1 or current_topic == 1 or current_topic == 0:

        text_for_client = "No he entendido, por favor repite tu petición."
        current_topic = -2

    if "muchas gracias por tu preferencia" in text_for_client:
        active_bot = False
        print("termina conversacion")
        current_topic = -2
    #global AWS
    if from_social_media:
        AWS.insert_topic(client_id, str(current_topic))

    print("-------------------------------")
    print(f"Sending out topic {current_topic}")
    print("-------------------------------")
    return text_for_client, current_topic


def handle_admissions(client_query):
    # PROCESS FOR IBM WATSON
    authenticator = IAMAuthenticator(IBM_access_key)
    assistant = AssistantV2(
        version='2021-06-14',
        authenticator=authenticator
    )
    assistant.set_service_url(
        'https://api.us-south.assistant.watson.cloud.ibm.com/instances/e0d095a7-17e0-4a51-b9e9-03b6552dd042')
    response = assistant.message_stateless(
        assistant_id=IBM_assistant,
        input={
            'message_type': 'text',
            'text': client_query
        }
    ).get_result()
    print(response['output']['generic'])
    text_for_client = ""
    for json_msg in response['output']['generic']:
        if "text" in json_msg and "response_type" in json_msg:
            text_for_client += json_msg["text"]
    return text_for_client


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route("/sendWhatsappTest", methods=['GET'])
# def sendWhatsappTest():
#     target_number = request.args.get('target_number')
#     message = request.args.get('message')
#     meta_api.respondWhatsapp(target_number,message)
#     return 'success', 200

# @app.route("/sendMessengerTest", methods=['GET'])
# def sendMessengerTest():
#     target_PSID = request.args.get('PSID')
#     message = request.args.get('message')
#     meta_api.respondMessenger(target_PSID, message)
#     return 'success', 200

@app.route("/webhook",methods=['POST'])
def webhook():
    try:
        content = request.get_json()
        clientPhone = content['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
        messageBody = content['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        if len(clientPhone) == 13:
            clientPhone = clientPhone[:2] + clientPhone[3:]

        print(clientPhone, messageBody)

        global AWS
        topic_for_client = AWS.dynamo_client.get_item(TableName="topicsForSocialMedia", Key={"clientID": {"S": f"{clientPhone}"}})


        if "Item" not in topic_for_client:

            AWS.insert_topic(clientPhone, f"-2")
            current_topic = -2
        else:
            current_topic = int(topic_for_client["Item"]["topic"]["S"])
        print(f"current_topic is {current_topic}")
        text_for_client = choose_cloud_converse_back(messageBody, clientPhone, current_topic, from_social_media=True)
        meta_api.respondWhatsapp(clientPhone, text_for_client)
        return 'success', 200
    except Exception as e:
        if('object' in request.get_json() and 'entry' in request.get_json()):
            return 'success', 200
        else:
            print(request.get_json())
            return 'error', 404

@app.route("/messengerWebhook",methods=['POST'])
def messengerWebhook():
    try:
        content = request.get_json()
        PSID = 1234
        messageBody = "Hello"
        print(content)

        #print(PSID, messageBody)

        # global AWS
        # topic_for_client = AWS.dynamo_client.get_item(TableName="topicsForSocialMedia", Key={"clientID": {"S": f"{PSID}"}})

        # if "Item" not in topic_for_client:

        #     AWS.insert_topic(PSID, f"-2")
        #     current_topic = -2
        # else:
        #     current_topic = int(topic_for_client["Item"]["topic"]["S"])
        # print(f"current_topic is {current_topic}")
        # text_for_client = choose_cloud_converse_back(messageBody, PSID, current_topic, from_social_media=True)
        # meta_api.respondMessenger(PSID, text_for_client)
        return 'success', 200
    except Exception as e:
        # if('object' in request.get_json() and 'entry' in request.get_json()):
        #     return 'success', 200
        # else:
        #     print(request.get_json())
        #     return 'error', 404
        return 'error', 404


    

@app.route("/webhook",methods=["GET"])
def webhookVerification():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.token')
    if(not token):
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
    if(mode and token):
        if(mode == 'subscribe' and token == WHATSAPP_TOKEN):
            print('Webhook verified')
            return challenge
    return 'error', 403

@app.route("/messengerWebhook", methods=['GET'])
def messengerWebhookVerification():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.token')
    if(not token):
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
    if(mode and token):
        if(mode == 'subscribe' and token == TOKEN):
            print('Webhook verified')
            return challenge
    return 'error', 403

@app.route('/utterTextFromText', methods=["POST"])
def utterTextFromText():
    incoming_json = request.get_json()
    client_id = incoming_json["clientID"]
    client_query = incoming_json["clientQuery"]
    current_topic = incoming_json["topic"]
    print(f"id is {client_id}, topic is {current_topic}, query is {client_query}")
    text_for_client, current_topic = choose_cloud_converse_back(client_query, client_id, current_topic, from_social_media=False)
    #global current_topic
    return {"text_for_client": text_for_client, "topic": current_topic}

@app.route('/uploadFile', methods=["POST"],)
def uploadFile():
    file = request.files["file"]
    print(file)
    #print(dir(file))
    print(f"received file {file.filename}")

    key = "transcribe/" + file.filename
    file.save(file.filename)
    # convert to webm
    os.system(f'ffmpeg -y -i "{file.filename}" -ar 48000 -vn "{"xd" + file.filename}"')
    os.system(f"rm -rf {file.filename}")
    os.system(f"mv {'xd' + file.filename} {file.filename}")
    global AWS
    AWS.s3_client.upload_file(file.filename, 'buketa', key)
    os.system(f"rm -rf {file.filename}")
    return "success", 200


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
    current_topic = incoming_json["topic"]
    client_id = incoming_json["clientID"]
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
        rows = db_cursor.fetchall()
        best_stt_service = rows[0][0]
        best_stt_benchmark = rows[0][1]
    elif stt_measure == "Exactitud":
        db_cursor.execute( \
            """select s.name, avg(benchmarkValue) as avg_benchmark
                from Metrics as m, STTBenchmarks as b, STTServices as s 
                where m.metricId = b.metricId and s.STTServiceId = b.STTServiceId and m.name = "Exactitud" 
                group by s.name
                order by avg_benchmark desc
                """)
        rows = db_cursor.fetchall()
        best_stt_service = rows[0][0]
        best_stt_benchmark = rows[0][1]
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
    else:
        best_stt_service = stt_measure


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
        rows = db_cursor.fetchall()
        best_tts_service = rows[0][0]
        best_tts_benchmark = rows[0][1]
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
    else:
        best_tts_service = tts_measure


    print(f"best stt service for {tts_measure} is {best_tts_service}")


    # REMOVE THIS WHEN DONE TESTING
    #best_stt_service = "AzureSTT"
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
        transcript, confidence = AWS.transcribe_audio_file('Example-job', file_key, file_key[:-4] + "json")
    elif best_stt_service == "GoogleSTT":
        transcript, confidence = GCP.transcribe_audio_file(file_key, AWS)

    elif best_stt_service == "WatsonSTT":
        transcript, confidence = transcribe_audio_file(file_key)
    elif best_stt_service == "AzureSTT":
        transcript, confidence = azure_transcribe_audio_file(file_key)
    elif best_stt_service == "NvidiaSTT":
        url = 'https://709f-148-241-64-15.ngrok.io/Nvidia'
        headers = {'Content-Type': 'application/json'}
        json = {"data": {"audio_response_link": f"https://buketa.s3.amazonaws.com/{file_key}"}}
        req = requests.post(url, headers=headers, json=json)
        transcript, confidence = req.text["transcripcion"], 0.5

    print("--------------------------------------------")
    print(f"prompt {transcript} confidence {confidence}")
    print("--------------------------------------------")

    stt_latency = (time.time() - stt_start_time) * 1000

    print("--------------------------------------------")
    print(f"stt latency is {stt_latency}")
    print("--------------------------------------------")

    print("--------------------------------------------")
    print("I'm going to insert the latency of stt into database.")
    print("--------------------------------------------")

    LATENCIA_QUERY_STRING = "Insert kksjadhfkj {stt_measure}"
    if stt_measure == "Latencia":
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


    # Remove files for all next rounds.
    #AWS.delete_object(file_key) amazon needs it kind of

    #os.system('rm -rf client.webm') probably azure needs it

    if not transcript: # None or empty sequence
        transcript = "transcript empty"


    text_for_client, current_topic = choose_cloud_converse_back(transcript, client_id, current_topic, from_social_media=False)

    print("--------------------------------------------")
    print(f"chatbot reponse for client {text_for_client}")
    print("--------------------------------------------")

    #best_tts_service = "WatsonTTS"
    tts_start_time = time.time()
    if best_tts_service == "Polly":
        # AWS TTS
        audio_response_link = AWS.vocalize(text_for_client, file_key[:-4] + "mp3")
    elif best_tts_service == "GoogleTTS":
        # TTS FOR GOOGLE
        audio_response_link = GCP.vocalize(text_for_client, AWS)
    elif best_tts_service == "WatsonTTS":
        audio_response_link = vocalize(text_for_client)
    elif best_tts_service == "AzureTTS":
        print("---------------------------")
        print("Calling Azure TTS")
        print("---------------------------")
        audio_response_link = azure_vocalize(text_for_client, AWS)



    tts_latency = (time.time() - tts_start_time) * 1000

    print("--------------------------------------------")
    print("I'm going to insert the latency of stt into database.")
    print("--------------------------------------------")

    if tts_measure == "Latencia":
        db_cursor.execute( \
            f"""
            INSERT INTO TTSBenchmarks (metricId, TTSServiceId, benchmarkValue) 
            VALUES ((SELECT metricId FROM Metrics WHERE name = "{tts_measure}"), 
                    (SELECT TTSServiceId FROM TTSServices WHERE name = "{best_tts_service}"), 
                    {tts_latency})
            """)
    #return audio_response_link

    return {"audio_response_link": audio_response_link, "text_for_client": text_for_client, "topic": current_topic}


    # store file in current folder.
    # authenticated_client.download_file("buketa", file_key[:-4] + "mp3", "audio_for_client.mp3")

    #with open('audio_for_client.mp3', 'r') as f:
    #    return f


    

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=8000)