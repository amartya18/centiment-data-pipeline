import boto3

ssm = boto3.client("ssm", "ap-southeast-1")

def ssm_get_parameters(key):
    response = ssm.get_parameters(Names=[key], WithDecryption=True)

    for params in response["Parameters"]:
        return params["Value"]
