import os
import boto3
from datetime import datetime


transcribe_role = os.environ.get(
    "TCROLE",
    "arn:aws:iam::012345678901:role/DummyRole"
)
language_code = os.environ.get("LANGCODE", "pt-BR")
file_type = os.environ.get("MEDIATYPE", "mp4")
region = os.environ.get("REGION", "us-east-1")
transcribe = boto3.client("transcribe", region_name=region)


def lambda_handler(event, context):
    """Start Transcribe job to extract text from audio Lambda function

    Parameters
    ----------
    event: dict, required
        StepFunctions Input event

    context: object, required
        Lambda Context runtime methods and attributes


    Returns
    ------
    Transcribe job id for text extract: dict

    """

    try:
        if ("Audio" in event["Outputs"]):
            bucket = event["Outputs"]["Audio"]["bucket"]
            key = event["Outputs"]["Audio"]["key"]
            file_name = event["metadata"]["file_name"]
            _id = event["metadata"]["uuid"]
            job_id = f"{file_name}-{_id}"
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }

    payload = event
    payload["Outputs"]["Transcribe"] = {}

    file_input = f"s3://{bucket}/{key}"

    try:
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_id,
            LanguageCode=language_code,
            Media={
                "MediaFileUri": file_input
            },
            MediaFormat=file_type,
            JobExecutionSettings={
                "DataAccessRoleArn": transcribe_role
            }
        )
        print(response)
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }
    else:
        if response["TranscriptionJob"][
                    "TranscriptionJobStatus"] == "IN_PROGRESS":
            payload["metadata"]["status"] = "IN PROGRESS"
            payload["metadata"]["last_update"] = (
                datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            )
            payload["Outputs"]["Transcribe"] = {
                "job_id": job_id
            }
            return payload
        elif response["TranscriptionJob"][
                      "TranscriptionJobStatus"] == "FAILED":
            payload["metadata"]["status"] = "FAILED"
            payload["metadata"]["last_update"] = (
                datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            )
            payload["Outputs"]["Transcribe"] = {
                "job_id": job_id,
                "message": response["TranscriptionJob"]["FailureReason"]
            }
            raise payload
        elif response["TranscriptionJob"][
                      "TranscriptionJobStatus"] == "COMPLETED":
            payload["metadata"]["status"] = "COMPLETE"
            payload["metadata"]["last_update"] = (
                datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            )
            payload["Outputs"]["Transcribe"] = {
                "job_id": job_id
            }
            return payload
        else:
            payload["metadata"]["status"] = "FAILED"
            payload["metadata"]["last_update"] = (
                datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            )
            payload["Outputs"]["Transcribe"] = {
                "job_id": job_id,
                "message": f"Unhandled error for this job: {job_id}"
            }
            raise payload
