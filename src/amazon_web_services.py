"""Class to represent the capabilities of AWS

Author: Luis Ignacio Ferro Salinas A01378248
Last update: december 4th, 2022
"""

import json

# Standard library
import os
import time

import boto3

# 3rd party related libraries.
from dotenv import load_dotenv


class AmazonWebServices:
    def __init__(self):
        load_dotenv("../secrets.env")

        # Read credentials.
        self.__access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.__secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.__session_token = os.getenv("AWS_SESSION_TOKEN")
        self.__region = os.getenv("REGION_NAME")
        # print("-----------------------")
        # print(self.__access_key)
        # print("-----------------------")
        # print(self.__secret_access_key)
        # print("-----------------------")
        # print(self.__session_token)

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.__access_key,
            aws_secret_access_key=self.__secret_access_key,
            aws_session_token=self.__session_token,
            region_name=self.__region,
        )

        self.transcribe_client = boto3.client(
            "transcribe",
            aws_access_key_id=self.__access_key,
            aws_secret_access_key=self.__secret_access_key,
            aws_session_token=self.__session_token,
            region_name=self.__region,
        )

        # LexV2 client uses 'lexv2-runtime'
        self.lex_client = boto3.client(
            "lexv2-runtime",
            aws_access_key_id=self.__access_key,
            aws_secret_access_key=self.__secret_access_key,
            aws_session_token=self.__session_token,
            region_name=self.__region,
        )

        self.polly_client = boto3.client(
            "polly",
            aws_access_key_id=self.__access_key,
            aws_secret_access_key=self.__secret_access_key,
            aws_session_token=self.__session_token,
            region_name=self.__region,
        )

        self.dynamo_client = boto3.client(
            "dynamodb",
            aws_access_key_id=self.__access_key,
            aws_secret_access_key=self.__secret_access_key,
            aws_session_token=self.__session_token,
            region_name=self.__region,
        )

    def transcribe_audio_file(self, job_name, file_key, output_key):

        file_uri = "s3://buketa/" + file_key

        self.transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": file_uri},
            MediaFormat="webm",
            LanguageCode="es-ES",
            OutputBucketName="buketa",
            OutputKey=output_key,
        )

        max_tries = 60
        while max_tries > 0:
            max_tries -= 1
            job = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            job_status = job["TranscriptionJob"]["TranscriptionJobStatus"]
            if job_status in ["COMPLETED", "FAILED"]:
                print(f"Job {job_name} is {job_status}.")
                if job_status == "COMPLETED":
                    # print(f"Amazon Transcript ready to be downloaded\n")
                    # print(f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
                    response = self.transcribe_client.delete_transcription_job(
                        TranscriptionJobName=job_name
                    )
                break
            else:
                print(f"Waiting for {job_name}. Current status is {job_status}.")
            time.sleep(10)

        # print("I will place transcript in " + file_key[:-4] + "json")
        # store file in current folder.
        self.s3_client.download_file("buketa", file_key[:-4] + "json", "helloback.json")
        with open("../helloback.json", "r") as f:
            json_data = json.load(f)
        # print(F"AWS TRANSCRIBE SPEECH TO TEXT {json_data}")
        avg_confidence = 0

        n_items = 0
        for item_no, transcript_item in enumerate(json_data["results"]["items"]):
            n_items += 1
            # print(f"confidence is {transcript_item['alternatives'][0]['confidence']}")
            avg_confidence += float(transcript_item["alternatives"][0]["confidence"])

        try:
            avg_confidence /= n_items
        except:  # Division by 0
            avg_confidence = 0.5
        transcript = json_data["results"]["transcripts"][0]["transcript"]

        # delete current transcript from memory
        os.system("rm -rf helloback.json")

        print("AMAZON TRANSCRIPTION COMPLETE")
        return transcript, avg_confidence

    def converse_back(self, client_string, client_id):
        bot_response = self.lex_client.recognize_text(
            botId="P5LSOCLGUI",
            botAliasId="TSTALIASID",
            localeId="es_419",
            sessionId=client_id,
            text=client_string,
        )

        print("bot response")
        print(bot_response)

        if "messages" in bot_response:
            print("messages ")
            print(bot_response["messages"])
            text_for_client = ""
            for json_msg in bot_response["messages"]:
                text_for_client += json_msg["content"]
        else:
            text_for_client = "No he entendido"

        return text_for_client

    def vocalize(self, text_for_client, output_key):
        synthesis_job = self.polly_client.start_speech_synthesis_task(
            Text=text_for_client,
            OutputFormat="mp3",
            LanguageCode="es-US",
            VoiceId="Penelope",
            OutputS3BucketName="buketa",
            OutputS3KeyPrefix=output_key,
        )
        print(synthesis_job)

        max_tries = 60
        while max_tries > 0:
            max_tries -= 1
            synthesis_job = self.polly_client.get_speech_synthesis_task(
                TaskId=synthesis_job["SynthesisTask"]["TaskId"]
            )
            job_status = synthesis_job["SynthesisTask"]["TaskStatus"]
            # print(job_status)
            if job_status in ["completed", "failed"]:
                # print(f"Job is {job_status}.")
                if job_status == "completed":
                    print(f"audio ready to be downloaded\n")
                    print(f"\t{synthesis_job['SynthesisTask']['OutputUri']}.")
                    return synthesis_job["SynthesisTask"]["OutputUri"]
            else:
                print(f"Waiting for. Current status is {job_status}.")
            time.sleep(10)

    def delete_object(self, file_key):
        self.s3_client.delete_object(Bucket="buketa", Key=file_key)

    def insert_topic(self, clientID: str, topic: str) -> None:
        self.dynamo_client.put_item(
            TableName="topicsForSocialMedia",
            Item={"clientID": {"S": clientID}, "topic": {"S": topic}},
        )
