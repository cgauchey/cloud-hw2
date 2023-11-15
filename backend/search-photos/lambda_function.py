import json
import os
import boto3
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import random

REGION = 'us-east-1'
HOST = 'search-photos-fv2gi6zwbxcko2nyqvdttkau7q.us-east-1.es.amazonaws.com'
INDEX = 'photos'


# opensearch query
def query(keyword):
    q = {
        'size': 1000,
        'query': {
            'term': {
                'labels': {
                    'value': keyword
                }
            }
        }
    }

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
        http_auth=get_awsauth(REGION, 'es'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection)

    res = client.search(index=INDEX, body=q)
    hits = res['hits']['hits']

    results = []
    for hit in hits:
        results.append(hit['_source']['objectKey'])

    return results


def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)


def lambda_handler(event, context):
    print("IN LAMDA HANDLER")
    client = boto3.client('lexv2-runtime')

    msg_from_user = event['queryStringParameters']['q']
    msg_from_user.replace('{', '')
    msg_from_user.replace('}', '')

    # text submitted from frontend searchbar #modify this

    # Initiate conversation with Lex
    response = client.recognize_text(
        botId='BUQZ2LIDMC',  # MODIFY HERE
        botAliasId='3HFAS2T1AY',  # MODIFY HERE
        localeId='en_US',
        sessionId='testuser',
        text=msg_from_user)

    slots = response.get('sessionState', {}).get('intent', {}).get('slots', {})

    search_keywords = []

    # if len(slots) == 0:
    #     return {
    #         'statusCode': 200,
    #         'headers': {
    #             'Content-Type': 'application/json'
    #         },
    #         'body': "no search"
    #     }

    # elif

    if 'search-keyword' in slots:
        if 'value' in slots['search-keyword']:
            search_keywords.append(
                slots['search-keyword']['value'].get('interpretedValue'))
    if slots['search-keyword-2']:
        if 'value' in slots['search-keyword-2']:
            search_keywords.append(
                slots['search-keyword-2']['value'].get('interpretedValue'))
    results = []

    for keyword in search_keywords:
        if keyword[-1] == 's':
            keyword = keyword[:-1]
        results += query(keyword)

    for i in range(len(results)):
        results[i] = "https://b2photostorage.s3.us-east-1.amazonaws.com/" + results[i]

    # for result in results:
    #     result = "https://b2photostorage.s3.us-east-1.amazonaws.com/" + result

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(results)
    }
