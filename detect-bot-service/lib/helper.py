import boto3
import re
from subprocess import check_output


ssm = boto3.client("ssm", "ap-southeast-1")

def ssm_get_parameters(key):
    response = ssm.get_parameters(Names=[key], WithDecryption=True)

    for params in response["Parameters"]:
        return params["Value"]

def get_ip_addr():
    try:
        # linux only, remove newline and whitespace
        ip_addr = check_output(['hostname', '--all-ip-addresses']) 
        return re.sub("\s+", "", ip_addr.decode("UTF-8"))
    except:
        return "127.0.0.1"
