from __future__ import print_function
import boto3
import io
import subprocess
from packerpy import PackerExecutable
from botocore.exceptions import ClientError

BUCKET_NAME = 'demos3-lambdas1'
download_dir = '/tmp/'
def read_ssm_parameter(param):
    ssm = boto3.client('ssm')
    ssm_parameter = ssm.get_parameter(Name=param, WithDecryption=True)
    return ssm_parameter['Parameter']['Value']

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
    
    amiVersion = read_ssm_parameter('baseimage')  
    
    p = PackerExecutable("/opt/python/lib/python3.8/site-packages/packerpy/packer")
    #(ret, out, err)=p.build -var-file=variables.json f'{download_dir}ami-packer.json'

    template = f'{download_dir}gold-ami.json'
    template_vars = {'baseimage': amiVersion}
    (ret, out, err) = p.build(template,var=template_vars)
    print(out)
