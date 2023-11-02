import json
import boto3
from botocore.exceptions import ClientError
import os
from urllib.parse import parse_qs
import base64

def post_sn_to_queue(t, link, user):
    print("Posting show note to queue")
    status = True

    sqs_queue_name = None
    queue = None
    if user == 'someuser':
        print("Test condition detected, skipping posting")
    else:
        print(user)
        if 'QUEUE_NAME' in os.environ:
            sqs_queue_name = os.environ['QUEUE_NAME']
                
            sqs = boto3.resource('sqs')
            try:
                queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)
            except ClientError as ex:
                if ex.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                    print("ERROR: SQS queue " + sqs_queue_name + " was not found")
                    status = False

            if queue:

                message_json = {
                    "type" : t,
                    "link" : link,
                    "user" : user
                }

                # Must be a base64 encoded string
                # This gets it as a bytes type...
                base64_message = base64.b64encode(json.dumps(message_json).encode('utf-8'))

                # And this gets it as a b64 encoded string
                base64_message = base64_message.decode('utf-8')
                print("base64 " + base64_message)

                # Create a new message
                try:
                    response = queue.send_message(
                        MessageBody=base64_message,
                        MessageGroupId='CloudPodShowNote'
                    )
                except ClientError as ex:
                    print("ERROR writing to SQS queue " + ex.response['Error']['Code'])
                    status = False

                if status:
                    print("Successfully sent message to queue")
                    print("SQS Message ID: " + response.get('MessageId'))
                    print("SQS MD5: " + response.get('MD5OfMessageBody'))

    return status

def validate_slack_token(incoming_token):
    print("Validating slack auth token")
    valid = False

    # Now see if we have the allowable token in the env
    if incoming_token and 'SLACK_TOKEN' in os.environ:
        valid_slack_token = os.environ['SLACK_TOKEN']

        if valid_slack_token == incoming_token:
            valid = True

    return valid

def command_handler(command, link, user):
    print("Handling command")
    commands = ['aws', 'gcp', 'azure', 'general', 'other', 'help']
    slack_dict = {}
    post = True

    if command == 'help':
        post = False

        slack_dict['text'] = 'Add links to shownotes in to appropriate section of the Google Doc:\n'
        slack_dict['text'] += 'I know the following sections:\n'
        slack_dict['text'] += '*aws* - *gcp* - *azure* - *general* - *other*\n'
        slack_dict['text'] += 'eg: shownotes aws https://exmaple.com/somehottake\n'

    else:
        if command not in commands:
            post = False
            slack_dict['text'] = 'ERROR: ' + command + ' not in :' + commands
        else:
            if post:
                status = post_sn_to_queue(command, link, user)
                if status:
                    slack_dict['text'] = 'Successfully added the link to the shownotes'
                else:
                    slack_dict['text'] = 'ERROR: Failed to write to queue'

    return slack_dict

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    statusCode = 200
    valid_trigger_word = 'shownotes'
    slack_return_content = []
    if 'body' in event:
        parsed_body = parse_qs(event['body'])
        print(parsed_body)
        # The parsed body looks like:
        # {'channel_id': ['channel id'],
        # 'channel_name': ['slack channel name'],
        # 'service_id': ['slack bot id'],
        # 'team_domain': ['slack domain prefix'],
        # 'team_id': ['slack team id'],
        # 'text': ['AWS: https://exmaple.com'],
        # 'timestamp': ['1540930044.021500'],
        # 'token': ['slacktoken'],
        # 'trigger_word': ['/shownotes'],
        # 'user_id': ['slack user id'],
        # 'user_name': ['slack username']}

        if 'token' in parsed_body:
            if validate_slack_token(parsed_body['token'][0]):
                print("Valid slack token provided")

                # Check the trigger word is correct
                if parsed_body['trigger_word'][0] == valid_trigger_word:
                    print("Valid trigger word detected")

                    # Get the command first...
                    words = parsed_body['text'][0].split(" ")
                    command = words[1]
                    print("Received command: " + command)

                    # Now get the argument if it is there
                    # If there is no extra argument, arg will remain blank
                    arg = ' '.join(words[2:])
                    if arg:
                        print("Received argument [" + arg + "]")

                    # This will return a dict in the format slack expects....
                    # We json encode it before sending it along to slack
                    slack_return_content = command_handler(command, arg, parsed_body['user_name'][0])
                    if 'ERROR' in slack_return_content['text']:
                        statusCode = 400
                else:
                    statusCode = 500
                    print("ERROR: Invalid trigger word. Wanted " + valid_trigger_word + " received " + parsed_body['trigger_word'][0])
            else:
                statusCode = 401
                print("ERROR: Invalid slack token was provided")
        else:
            statusCode = 401
            print("ERROR: No slack token was provided in the body")
    else:
        statusCode = 500
        print("ERROR: No body was provided in the event")

    return {
        "statusCode": statusCode,
        "body": json.dumps(slack_return_content)
    }