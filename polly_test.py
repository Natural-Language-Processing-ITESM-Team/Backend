from asyncore import poll
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

"""with open('polly_res.txt', encoding='utf-8') as f:
  response = f.read()
  f.close()"""

def get_polly_audio(polly_client, output_key, text):
    synthesis_job = polly_client.start_speech_synthesis_task(
        Text=text,
        OutputFormat='mp3',
        LanguageCode='en-US',
        VoiceId='Aditi',
        OutputS3BucketName = "buketa",
        OutputS3KeyPrefix = output_key
    )
    print(synthesis_job)
    
    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        synthesis_job = polly_client.get_speech_synthesis_task(TaskId=synthesis_job['SynthesisTask']["TaskId"])
        job_status = synthesis_job['SynthesisTask']['TaskStatus']
        #print(job_status)
        if job_status in ['completed', 'failed']:
            #print(f"Job is {job_status}.")
            if job_status == 'completed':
                print(f"audio ready to be downloaded\n")
                print(f"\t{synthesis_job['SynthesisTask']['OutputUri']}.")  # This is d
                return synthesis_job['SynthesisTask']['OutputUri']
        else:
            print(f"Waiting for. Current status is {job_status}.")
        time.sleep(10)
    #return(result)

#get_polly_audio(polly_client, "hello.mp3")





