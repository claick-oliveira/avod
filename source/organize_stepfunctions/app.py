def lambda_handler(event, context):
    """Organize StepFunctions Lambda function

    Parameters
    ----------
    event: dict, required
        Organize StepFunctions Input event

    context: object, required
        Lambda Context runtime methods and attributes


    Returns
    ------
    Organize StepFunctions: dict

    """

    payload = {
        "metadata": {},
        "Outputs": {}
    }

    try:
        if (event != []):
            for x in range(0, len(event)):
                payload["metadata"].update(event[x]["metadata"])
                payload["Outputs"].update(event[x]["Outputs"])
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }

    return payload
