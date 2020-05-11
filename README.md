# avod

This project to build a workflow to create Captions and HLS files. This repository contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- source - Code for the application's Lambda function.
- events - Examples of invocation events that you can use to invoke the function.
- tests - #TODO
- template.yaml - A template that defines the application's AWS resources.
- cloudformations - Templates to create Roles and StepFunctions.

The application uses several AWS resources, including Lambda functions, Media Convert, Transcribe, and Step Functions. These resources are defined in the `template.yaml` or in the CloudFormation YAML files on this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project.

### Prerequisites

- git
- make
- python 3.7
- pip
- virtualenv
- vscode
- docker [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)
- SAM CLI [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

### Installing

First of all you need to clone this repository:

``` bash
git clone https://github.com/claick-oliveira/avod.git
```

After clone access the folder and you'll need to create a docker network and launch the dynamodb local:

```bash
cd avod
make dkn
```

## Running the unit tests

TODO

## Deploy/Test the application

To deploy this solution you need to execute three steps.

- Create a S3 Bucket;
- Create Media Convert and Transcribe roles;
- Create Lambdas functions;
- Create the Step Functions;
- Create a trigger when some object was stored on S3 to execute a Lmabda to start the Step Functions.

### S3

TODO

### Media Convert and Transcribe

To create these resources use the cloudformation templates in the folder `cloudformations`. You can execute these commands to deploy:

Media Convert:

```bash
aws cloudformation deploy --template-file cloudformations/MediaConvertRole.yaml --stack-name <stack-name> --capabilities CAPABILITY_IAM --parameter-overrides Bucket=<bucket-name>
```

Transcribe:

```bash
aws cloudformation deploy --template-file cloudformations/TranscribeRole.yaml --stack-name <stack-name> --capabilities CAPABILITY_IAM --parameter-overrides Bucket=<bucket-name>
```

Remenber to replace:

- \<stack-name\>
- \<bucket-name\>

After the deploy you need to get the Roles [ARN](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html). It's look like as `arn:partition:service:region:account-id:resource-type/resource-id`. Get the value to each stack (Media Convert and Transcribe), becaue we use in the next step.

Media Convert:

```bash
aws cloudformation describe-stacks --stack-name <stack-name> --query 'Stacks[*].Outputs[?OutputKey==`MediaConvertRoleArn`].OutputValue' --output text
```

Transcribe:

```bash
aws cloudformation describe-stacks --stack-name <stack-name> --query 'Stacks[*].Outputs[?OutputKey==`TranscribeRoleArn`].OutputValue' --output text
```

### Lambdas

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

Lmabdas:

- **StartExtractAudioFunction**
- **GetExtractAudioFunction**
- **StartTranscribeFunction**
- **GetTranscribeFunction**
- **StartWebCaptionsFunction**
- **StartSRTFunction**
- **StartHLSFunction**
- **GetHLSFunction**
- **OrganizeStepFunctionsFunction**

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

- **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
- **AWS Region**: The AWS region you want to deploy your app to.
- **Parameters**:
  - **SFARN**: Step Functions ARN.
  - **MCROLE**: Media Convert Role ARN. (See the previous step)
  - **TCROLE**: Transcribe Role ARN. (See the previous step)
  - **LANGCODE**: Video Language code, example pt-BR.
  - **SOURCELANGCODE**: Caption Langauge code, example pt-BR.
  - **TARGETLANGCODE**: Media Convert caption langauge code, example pt-BR.
  - **Region**: AWS Region code.
  - **AWSEnv**: To run tests locally use AWS_SAM_LOCAL.
  - **s3bucket**: S3 bucket that the files will be stored.
- **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
- **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modified IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
- **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

After the deploy you need to get the lambda ARN to use in the next step. Execute the command and store the ARNs:

```bash
aws cloudformation describe-stacks --stack-name avod --query 'Stacks[*].Outputs[?contains(OutputValue, `lambda`)].[OutputKey, OutputValue]' --output text
```

### Step Functions

To create this resource use the cloudformation templates in the folder `cloudformations`. You can execute these commands to deploy:

```bash
aws cloudformation deploy --template-file cloudformations/StepFunctions.yaml --stack-name <stack-name> --capabilities CAPABILITY_IAM --parameter-overrides StateMachine=<statemachine-name> StartExtractAudioFunction=<lambda-arn> GetExtractAudioFunction=<lambda-arn> StartTranscribeFunction=<lambda-arn> GetTranscribeFunction=<lambda-arn> StartWebCaptionsFunction=<lambda-arn> StartSRTFunction=<lambda-arn> StartHLSFunction=<lambda-arn> GetHLSFunction=<lambda-arn> OrganizeStepFunctionsFunction=<lambda-arn>
```

Remenber to replace:

- \<stack-name\>
- \<lambda-arn\>, use the ARN that you got on the previous step.

## S3 Trigger

TODO

## Use the SAM CLI to build and test locally

TODO

## Add a resource to your application

The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
sam logs -n <Function> --stack-name lambda-python-api-example --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name <stack-name>
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

## Contributing

Please read [CONTRIBUTING.md](https://github.com/claick-oliveira/avod/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

- **Claick Oliveira** - *Initial work* - [claick-oliveira](https://github.com/claick-oliveira)

See also the list of [contributors](https://github.com/claick-oliveira/avod/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
