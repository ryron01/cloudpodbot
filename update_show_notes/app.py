from google.oauth2 import service_account
import googleapiclient.discovery

import os
import boto3
import json
import tempfile

def get_range(header, document):
    heading = None
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
    service = googleapiclient.discovery.build('docs', 'v1', credentials=creds)
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

def lambda_handler(event, context):
    #TODO These need to be fetched from config
    DOCUMENT_ID = '1lZxVnMHxU00oDcbgXNRm_tj-VztPilDU1OqA1Qix52Q'
    SERVICE_ACCOUNT_FILE = 'cloudpodbot/cloudpodtest_credentials.json'
    
    SCOPES = ['https://www.googleapis.com/auth/documents']

    url = event['url']
    linktext = event['linktext']
    header = event['header']
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    update_doc(creds, DOCUMENT_ID, header, linktext, url)

def main(event, context):
    lambda_handler(event, context)

if __name__ == '__main__':
    
    event = {
        "url": "http://miserableunicorn.com",
        "linktext": "Your MOM\n",
        "header": "AWS"
    }

    main(event, None)
