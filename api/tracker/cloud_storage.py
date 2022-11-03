from google.cloud import storage
# for aws s3
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("django")

"""Returns whether bucket exists

@type bucket_name: str
@param bucket_name: name of bucket to check in google cloud
@rtype: bool
@returns: True if bucket exists, False if not 

"""
def get_default_bucket_name(study_id, consent_group):
	return 'nih-nhlbi-bdc-' + study_id.replace(".", "-") + '-' + consent_group

"""Returns whether bucket exists

@type bucket_name: str
@param bucket_name: name of bucket to check in google cloud
@rtype: bool
@returns: True if bucket exists, False if not 

"""	
def google_cloud_bucket_exists(bucket_name):
	logger.info("checking google_cloud_bucket_exists: " + bucket_name)
	client = storage.Client()    
	bucket = client.bucket(bucket_name)
	return bucket.exists()

def google_cloud_create_bucket_with_user_permissions(bucket_name, user_email):
	client = storage.Client()
	bucket = _google_cloud_create_bucket(client, bucket_name)
	if (user_email):
		_google_cloud_add_bucket_upload_permissions(client, bucket, user_email)			
	return bucket

def _google_cloud_create_bucket(client, bucket_name):
	logger.info("creating bucket: gs://" + bucket_name)
	client = storage.Client()
	bucket = client.create_bucket(bucket_name)	
	return bucket

def _google_cloud_add_bucket_upload_permissions(client, bucket, user_email):
	# see https://gcloud.readthedocs.io/en/latest/storage-acl.html
	acl = bucket.acl
	acl.user(user_email).grant_read()	
	acl.user(user_email).grant_write()

def aws_cloud_bucket_exists(bucket_name):
	logger.info("checking aws_cloud_bucket_exists: " + bucket_name)
	exists = False
	try:
		session = boto3.session.Session()
		# User can pass customized access key, secret_key and token as well
		s3_resource = session.resource('s3')
		s3_resource.meta.client.head_bucket(Bucket=bucket_name)
		exists = True
	except ClientError as error:
		error_code = int(error.response['Error']['Code'])
		if error_code == 403:
			# bucket exists but is private      
			exists = True
		elif error_code == 404:
			exists = False
	return exists
	
def aws_cloud_create_bucket_with_user_permissions(bucket_name, aws_iam):
	logger.info("creating bucket: s3://" + bucket_name)
	try:
		s3_client = boto3.client('s3')
		_aws_cloud_create_bucket(s3_client, bucket_name)
		s3_resource = boto3.resource('s3')
		bucket = s3_resource.Bucket(bucket_name)
		if (aws_iam):
			_aws_cloud_add_bucket_upload_permissions(s3_client, bucket, aws_iam)
		return bucket		
	except ClientError as e:
		logging.error(e)
		return None

	
def _aws_cloud_create_bucket(s3_client, bucket_name):
	s3_client.create_bucket(Bucket=bucket_name)
	return True

def _aws_cloud_add_bucket_upload_permissions(s3_client, bucket, aws_iam):
	# see https://www.learnaws.org/2021/05/12/aws-iam-boto3-guide/#how-to-create-an-iam-policy
	return

def main():
	print("running tests on cloud_storage.py") 
	bucket_name = 'nimbus-clavalle-test-bucket7'
	result = google_cloud_bucket_exists(bucket_name)
	print("gs://", bucket_name, ":", result)
	result = aws_cloud_bucket_exists(bucket_name)
	print("s3://", bucket_name, ":", result)
	bucket = google_cloud_create_bucket_with_user_permissions(bucket_name, 'christopher@nimbusinformatics.com')
	if (bucket):
		print("successfully created google bucket")	
	bucket = aws_cloud_create_bucket_with_user_permissions(bucket_name, None)
	if (bucket):
		print("successfully created aws bucket")	
	return	
if __name__ == "__main__":
    main()
