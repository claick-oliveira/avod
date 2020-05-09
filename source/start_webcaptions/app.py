import os
import boto3
import json
from datetime import datetime


source_language_code = os.environ.get("SOURCELANGCODE", "pt-BR")
region = os.environ.get("REGION", "us-east-1")
s3 = boto3.client("s3", region_name=region)


def lambda_handler(event, context):
    """Start Web Captions job to generate captions from transcribe function

    Parameters
    ----------
    event: dict, required
        StepFunctions Input event

    context: object, required
        Lambda Context runtime methods and attributes


    Returns
    ------
    Web Captions file path: dict

    """

    try:
        if ("Transcribe" in event["Outputs"]):
            bucket = event["Outputs"]["Transcribe"]["bucket"]
            key = event["Outputs"]["Transcribe"]["key"]
            _id = event["metadata"]["uuid"]
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }

    payload = event
    payload["Outputs"]["WebVTT"] = {}

    try:
        transcribe_file = s3.get_object(Bucket=bucket, Key=key)
        transcribe_metadata = json.loads(
            transcribe_file["Body"].read().decode("utf-8")
        )
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }

    end_time = 0.0
    max_length = 50
    word_count = 0
    max_words = 12
    max_silence = 1.5

    captions = []
    caption = None

    for item in transcribe_metadata["results"]["items"]:
        is_punctuation = item["type"] == "punctuation"

        if caption is None:
            # Start of a line with punctuation, just skip it
            if is_punctuation:
                continue

            # Create a new caption line
            caption = {
                "start": float(item["start_time"]),
                "caption": "",
                "wordConfidence": []
            }

        if not is_punctuation:
            start_time = float(item["start_time"])

            # Check to see if there has been a long silence
            # between the last recorded word and start a new
            # caption if this is the case, ending the last time
            # as this one starts.
            if (len(caption["caption"]) > 0 and
               (end_time + max_silence) < start_time):
                caption["end"] = start_time
                captions.append(caption)

                caption = {
                    "start": float(start_time),
                    "caption": "",
                    "wordConfidence": []
                }

                word_count = 0

            end_time = float(item["end_time"])

        requires_space = (not is_punctuation) and (len(caption["caption"]) > 0)

        if requires_space:
            caption["caption"] += " "

        # Process tweaks
        text = item["alternatives"][0]["content"]
        confidence = item["alternatives"][0]["confidence"]
        text_lower = text.lower()

        caption["caption"] += text

        # Track raw word confidence
        if not is_punctuation:
            caption["wordConfidence"].append(
                {
                    "w": text_lower,
                    "c": float(confidence)
                }
            )
            # Count words
            word_count += 1

        # If we have reached a good amount of text finalize the caption
        if (word_count >= max_words or len(caption["caption"]) >= max_length):
            caption["end"] = end_time
            captions.append(caption)
            word_count = 0
            caption = None

    # Close the last caption if required
    if caption is not None:
        caption["end"] = end_time
        captions.append(caption)

    webcaptions_name = f"WebCaptions_{source_language_code}"
    destination_key = f"outputs/{_id}/{webcaptions_name}"

    temp_file = f"/tmp/{webcaptions_name}"
    os.mknod(temp_file)

    with open(temp_file, "w") as f:
        print(captions, file=f)

    try:
        s3.upload_file(temp_file, bucket, destination_key)

        payload["metadata"]["status"] = "COMPLETED"
        payload["metadata"]["last_update"] = (
            datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
        )
        payload["Outputs"]["WebCaptions"] = {
            "bucket": bucket,
            "key": f"{destination_key}"
        }
        return payload
    except KeyError as e:
        payload["metadata"]["status"] = "FAILED"
        payload["metadata"]["last_update"] = (
            datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
        )
        payload["Outputs"]["WebCaptions"] = {
            "message": f"{e}"
        }
        raise payload
