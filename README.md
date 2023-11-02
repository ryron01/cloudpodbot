# cloudpodbot

This project contains source code and supporting files for a serverless application that udates the CloudPod show notes.

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. 

## Deploy the sample application

```bash
sam build --use-container
sam deploy --guided
```
The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

## Dependancies
* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

## Use the SAM CLI to build and test locally

Build your application with the `sam build --use-container` command.

```bash
cloudpodbot$ sam build --use-container
```

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
cloudpodbot$ sam local invoke ${FUNCTION} --event events/event.json
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
cloudpodbot$ sam local start-api
cloudpodbot$ curl http://localhost:3000/
```

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
cloudpodbot$ sam logs -n ${FUNCTION} --stack-name cloudpodbot --tail
```

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```bash
cloudpodbot$ pip install pytest pytest-mock --user
cloudpodbot$ python -m pytest tests/ -v
```

## Cleanup

To delete, assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name cloudpodbot
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)