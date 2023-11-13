import json
import boto3
import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')


REGION = 'us-east-1'
HOST = 'search-photos-fv2gi6zwbxcko2nyqvdttkau7q.us-east-1.es.amazonaws.com'
INDEX = 'photos'

def lambda_handler(event, context):
     
    bucket = event['Records'][0]['s3']['bucket']['name']
    name = event['Records'][0]['s3']['object']['key']

    
     # 2. Retrieve S3 metadata
    s3_response = s3.head_object(Bucket=bucket, Key=name)
    custom_labels = s3_response.get('Metadata', {}).get('x-amz-meta-customlabels', "[]")
    custom_labels_array = json.loads(custom_labels)

    #call Rekognition detect_labels
    rekognition_response = rekognition.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':name}}, MaxLabels=10)
    rekognition_labels = [label['Name'] for label in rekognition_response['Labels']]

    all_labels = rekognition_labels + custom_labels_array
    
    # 3. Store JSON object in OpenSearch index
    doc = {
        "objectKey": name,
        "bucket": bucket,
        "createdTimestamp": datetime.datetime.now().isoformat(),
        "labels": all_labels
    }
    
    
    open_search = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)
    
    open_search.index(index="photos", body=doc)
   

    return {
        'statusCode': 200
        # 'body': json.dumps('labels')
    }

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)
