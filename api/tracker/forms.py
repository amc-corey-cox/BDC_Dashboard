# application/forms.py

from django import forms
from .models import Ticket

TRUE_FALSE_CHOICES = ((True, "Yes"), (False, "No"))


class TicketCreateForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Ticket
        exclude = ["created_dt"]


# class SubmissionForm(forms.Form):
# 	email = forms.EmailField(label = 'Email')
# 	name = forms.CharField(max_length=100, label = 'Name of primary contact')
# 	organization = forms.CharField(max_length=250, label = 'Name of requesting organization')
# 	study_name = forms.CharField(max_length=250, label = 'Name of Study or Dataset (if applicable)', required = False)
# 	# FIXME - look for multiple email field
# 	additional_emails = forms.CharField(max_length=1000, label = 'Email addresses for additional persons who need access', required = False)
# 	dataset_description = forms.CharField(max_length=1000, label = 'Describe the dataset you are uploading', required = False)
# 	test_data = forms.BooleanField(label = "Check this box if this is test data: ", required = False)
# 	google_email = forms.EmailField(label = "If you're uploading to Google please provide your google email for access", required = False)
# 	aws_iam = forms.CharField(max_length=100, label = "If you're uploading to Amazon please provide your AWS IAM", required = False)
# 	studyid_consent_code_list = forms.CharField(max_length = 1000, label = 'Please list your study_id + consent codes comma separated below. Study_id and consent codes may ONLY include lowercase letters and periods. No capitals, dashes, underscores, or spaces in the study_id or consent_code. For example "phs12345.1..c123, phs23932.1..dc45"')
# 	data_size = forms.CharField(max_length = 100, label = 'Please provide an estimated size of your data set(s)')
#
# 	# FIXME validate...
# 	def clean_additional_emails(self):
# 		additional_emails =  self.cleaned_data['additional_emails']
# 		return additional_emails
#
# 	def clean_studyid_consent_code_list(self):
# 		studyid_consent_code_list = self.cleaned_data['studyid_consent_code_list']
# 		return studyid_consent_code_list
#
# 	def clean(self):
# 		cleaned_data = super().clean()
# 		google_email = cleaned_data.get('google_email')
# 		aws_iam = cleaned_data.get('aws_iam')
# 		if (google_email is None and aws_iam is None):
# 			raise forms.ValidationError('Either Google Email or AWS IAM are required')
# 		return cleaned_data
#
