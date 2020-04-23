import os
import boto3
import urllib.request
from datetime import datetime


language_code = os.environ.get("LANG", "pt-BR")
region = os.environ.get("REGION", "us-east-1")
transcribe = boto3.client("transcribe", region_name=region)
s3 = boto3.client("s3", region_name=region)


def lambda_handler(event, context):
    """Get Transcribe job to extract text from audio Lambda function

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
            file_name = event["metadata"]["file_name"]
            _id = event["metadata"]["uuid"]
            job_id = f"{file_name}-{_id}"
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }

    payload = event
    payload["Outputs"]["Transcribe"] = {}

    try:
        response = transcribe.get_transcription_job(
            TranscriptionJobName=job_id
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
            transcribe_uri = response["TranscriptionJob"][
                                      "Transcript"]["TranscriptFileUri"]
            # http = urllib3.PoolManager()
            # transcription = http.request('GET', transcribe_uri)
            temp_file = "/tmp/Transcript.json"
            os.mknod(temp_file)
            urllib.request.urlretrieve(transcribe_uri, temp_file)

            # with open(temp_file, "wb") as f:
            #    f.write(r.content)

            destination_key = f"outputs/{_id}/Transcript.json"
            s3.upload_file(temp_file, bucket, destination_key)

            payload["metadata"]["status"] = "COMPLETE"
            payload["metadata"]["last_update"] = (
                datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            )
            payload["Outputs"]["Transcribe"] = {
                "job_id": job_id,
                "bucket": bucket,
                "key": f"{destination_key}/Transcript.json"
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
