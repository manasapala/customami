from __future__ import print_function
import boto3
import io
import subprocess
import re
from packerpy import PackerExecutable
from botocore.exceptions import ClientError

# Fetching the ami-id from Parameter store

BUCKET_NAME = 'demos3-lambdas1'
download_dir = '/tmp/'
def read_ssm_parameter(param):
    ssm = boto3.client('ssm')
    ssm_parameter = ssm.get_parameter(Name=param, WithDecryption=True)
    return ssm_parameter['Parameter']['Value']

def update_ssm_parameter(param, value):
    SSM_CLIENT = boto3.client('ssm')
    response = SSM_CLIENT.put_parameter(
        Name=param,        
        Value=value,
        Type='String',
        Overwrite=True
    )

    if type(response['Version']) is int:
        return True
    else:
        return False

#downloading the source code from s3 bucket

def lambda_handler(event, context):    
    s3 = boto3.resource('s3')
    s3Client = boto3.client('s3')
    try:
        my_bucket = s3.Bucket(BUCKET_NAME)
        for s3_object in my_bucket.objects.all():
           filename = s3_object.key
           s3Client.download_file(BUCKET_NAME, filename, f'{download_dir}{filename}')
    except ClientError as e:
        return False
    
    amiBaseImage = read_ssm_parameter('baseimage')  
    # Trigger packer from python + packer executable layer    
    pkr = PackerExecutable("/opt/python/lib/python3.8/site-packages/packerpy/packer")
    template = f'{download_dir}gold-ami.json'
    template_vars = {'baseimage': amiBaseImage}
    (ret, out, err) = pkr.build(template,var=template_vars)
    outDecoded = out.decode('ISO-8859-1')
    if ret == 0:
        ami = re.search(('ami-[0-9][a-zA-Z0-9_]{16}'), outDecoded)
        amivalue = ami.group(0)
        update_ssm_parameter('ami-latest', amivalue)
