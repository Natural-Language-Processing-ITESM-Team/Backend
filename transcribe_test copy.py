from cgitb import text
import time
import boto3
import urllib

from dotenv import load_dotenv
import os

load_dotenv("secrets.env")

acces_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
session_token = os.getenv("AWS_SESSION_TOKEN")
region = os.getenv("REGION_NAME")


polly_client = boto3.client('polly',
        aws_access_key_id=acces_key,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name=region)

with open('polly_res.txt', encoding='utf-8') as f:
  response = f.read()
  f.close()

def polly_file(polly_client,output_key):
    result = polly_client.StartSpeechSynthesisTask(
        Text=response,
        OutputFormat='mp3',
        LanguageCode='ES-MX',
        VoiceId='Aditi',
        OutputS3BucketName = "Buketa",
        OutputS3KeyPrefix = output_key
    )
    return(result)





