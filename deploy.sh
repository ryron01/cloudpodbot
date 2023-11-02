#!/bin/bash

BUCKET=$1
SLACK_TOKEN=$2
GDOC_ID=$3

sam package --template-file template.yaml --output-template-file packaged.yaml --s3-bucket ${BUCKET}

sam deploy \
    --template-file packaged.yaml \
    --parameter-overrides SlackToken=${SLACK_TOKEN} GDocID=${GDOC_ID} \
    --stack-name cloudpodbot \
    --capabilities CAPABILITY_IAM \

aws cloudformation describe-stacks --stack-name cloudpodbot --query 'Stacks[].Outputs'
