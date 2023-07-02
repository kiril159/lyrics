import csv
from fastapi import FastAPI
import boto3

lyrics_tsv = {}
with open("lyrics.tsv") as file:
    tsv_file = csv.reader(file, delimiter='	')
    for line in tsv_file:
        if not line[1].startswith("["):
            lyrics_tsv[line[0]] = line[1]

session = boto3.session.Session()
s3_client = session.client(service_name='s3',
    aws_access_key_id='SYR3VKLQ1X1W2GRPZJQS',
    aws_secret_access_key='e6t5A2IT2Yi208ppZxg9EC9CkQ0puZNQSZyvPzJ0',
    endpoint_url='https://obs.ru-moscow-1.hc.sbercloud.ru',)

Bucket = 'obs-ingest-lyrics-dataset'
app = FastAPI()

