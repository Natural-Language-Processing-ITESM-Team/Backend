from flask import request
from flask import Flask
import boto3
import json
from flask_cors import CORS
from transcribe_test import transcribe_file
from dotenv import load_dotenv
import os

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
    
    file_uri = "s3://buketa/" + file_key

    print("I will place transcript in " + file_key[:-4] + "json")
    transcribe_file('Example-job', file_uri, transcribe_client, file_key[:-4] + "json")

    # store file in current folder.
    authenticated_client.download_file("buketa", file_key[:-4] + "json", "helloback.json")

    with open('helloback.json', 'r') as f:
        json_data = json.load(f)

    # boom bam bop, badabop boom POW return transcript
    return json_data["results"]["transcripts"][0]["transcript"]

    

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=8000)