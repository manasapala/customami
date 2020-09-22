from __future__ import print_function
import boto3
import io
import json
import subprocess
import os 
import sys
from botocore.exceptions import ClientError

BUCKET_NAME = 'demos3-lambdas1'
download_dir = '/tmp/'
save_parameter = ''

def download_file(filename):   
    s3 = boto3.resource('s3')
    s3Client = boto3.client('s3')
    try:
        my_bucket = s3.Bucket(BUCKET_NAME)
        s3Client.download_file(BUCKET_NAME, filename, f'{download_dir}{filename}')
           
        print('file downloaded')           
    except ClientError as e:
        return False
#    subprocess.call("ls -lrt /tmp", shell=True) 
def update_file_with_ami(filename, save_parameter):
    s3 = boto3.resource('s3')
    s3Client = boto3.client('s3')
    try:
       json_object = save_parameter            
       a_file = open(f'{download_dir}{filename}', "r")
       json_object = json.load(a_file)
       a_file.close()
       print(json_object)
       json_object["id"] = save_parameter
       a_file = open(f'{download_dir}{filename}', "w")
       json.dump(json_object, a_file)
       a_file.close()
       s3Client.upload_file(f'{download_dir}{filename}', BUCKET_NAME, f'{filename}')
       print ('successfully updated')
    except ClientError as e:
        return False 

def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    ssm_parameter = ssm.get_parameter(Name='id', WithDecryption=True)
    save_parameter = (ssm_parameter['Parameter']['Value'])
    print (save_parameter) 
    download_file('variables.json')
    update_file_with_ami('variables.json',save_parameter)
    print(os.environ)
