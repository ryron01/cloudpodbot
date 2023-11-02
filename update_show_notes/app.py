from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import os
import boto3
import pickle
import json
import tempfile

def get_creds(credentials_json, scopes):
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                #TODO replace this with creds from parameterstore
                '/Users/ryanlucas/Downloads/credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_range(header, document):
    for content in document['body']['content']:
        paragragh = content.get("paragraph")
        if paragragh:
            for v in paragragh.values():
                if isinstance(v, list):
                    # Only find the headers with heading links
                    for obj in v:
                        if header in obj['textRun']['content']:
                            if obj['textRun']['textStyle'].get('link'):
                                heading = obj['textRun']['textStyle']['link']
                            if heading.get('headingId'):
                                print(heading.get('headingId'))
                                #print("start: %s end: %s for %s" % (obj['startIndex'], obj['endIndex'], obj['textRun']['content']))
                                end_index = obj['endIndex']
                                start_index = obj['startIndex']
                                return { 'start_index': start_index, 'end_index': end_index }
    return False                    
    


def update_doc(creds, doc_id, header, linktext, url):
    service = build('docs', 'v1', credentials=creds)
    document = service.documents().get(documentId = doc_id).execute()

    index_range = get_range(header, document)

    if index_range:
        location = index_range['end_index'] + 1
        end_index = location + len(linktext) + 1

        requests = [
                        {
                            'insertText': {
                                'location': {
                                    'index': location,
                                },
                                'text': linktext
                            }
                        },
                        {
                            "updateTextStyle": {
                                "textStyle": {
                                    "link": {
                                        "url": url  
                                    }
                                },
                                "range": {
                                    "startIndex": location,
                                    "endIndex": end_index
                                },
                                "fields": "link"
                            }
                        }
                    ]

        result = service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()
        return result
    else:
        print("something went wrong")
    return None

def main(event, context):
    DOCUMENT_ID = os.environ.get('DOC_ID')
    CREDS = os.environ.get('CREDS')

    scopes = ['https://www.googleapis.com/auth/documents']

    url = event['url']
    linktext = event['linktext']
    header = event['header']

    f = tempfile.NamedTemporaryFile()

    tmp = open(f.name, 'w')
    tmp.write(CREDS)
    tmp.close()
    creds = get_creds(f.name, scopes)

    update_doc(creds, DOCUMENT_ID, header, linktext, url)
    os.unlink(f.name)

if __name__ == '__main__':
    
    event = {
        'url': 'http://miserableunicorn.com',
        'linktext': 'This is a test5 \n',
        'header': 'AWS'
    }

    main(event, None)

# client = boto3.client('sqs')

# response = client.receive_message(
#     QueueUrl='string',
#     AttributeNames=[
#         'All'|'Policy'|'VisibilityTimeout'|'MaximumMessageSize'|'MessageRetentionPeriod'|'ApproximateNumberOfMessages'|'ApproximateNumberOfMessagesNotVisible'|'CreatedTimestamp'|'LastModifiedTimestamp'|'QueueArn'|'ApproximateNumberOfMessagesDelayed'|'DelaySeconds'|'ReceiveMessageWaitTimeSeconds'|'RedrivePolicy'|'FifoQueue'|'ContentBasedDeduplication'|'KmsMasterKeyId'|'KmsDataKeyReusePeriodSeconds',
#     ],
#     MessageAttributeNames=[
#         'string',
#     ],
#     MaxNumberOfMessages=123,
#     VisibilityTimeout=123,
#     WaitTimeSeconds=123,
#     ReceiveRequestAttemptId='string'
# )