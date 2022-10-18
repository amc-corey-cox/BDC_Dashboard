# from google.cloud import storage
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from google.api_core.exceptions import BadRequest, Forbidden
# from google.cloud.exceptions import NotFound
# from google.cloud.storage.retry import DEFAULT_RETRY

def get_default_bucket_name(study_id, consent_group):
	return 'nih-nhlbi-bdc-' + study_id.replace(".", "-") + '-' + consent_group
	
def google_cloud_bucket_exists(bucket_name):
	return True
	
def google_cloud_bucket_create(bucket_name):
	return True
	
def aws_cloud_bucket_exists(bucket_name):
	return True

def aws_cloud_bucket_create(bucket_name):
	return True
