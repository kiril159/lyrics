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
s3_client = session.client()

Bucket = 'obs-ingest-lyrics-dataset'
app = FastAPI()

