import os
from django.conf import settings
from django.core.mail import EmailMessage
from .models import STATUS_TYPES
from smtplib import SMTPException
from django.core.mail import BadHeaderError
from python_http_client import exceptions
import logging

logger = logging.getLogger("django")

# admin emails (add more here)
NO_REPLY_EMAIL = settings.SENDGRID_NO_REPLY_EMAIL
ADMIN_EMAIL = settings.SENDGRID_ADMIN_EMAIL

# sendgrid templates for users
SENDGRID_TICKET_CREATED_TEMPLATE_ID_USER = settings.SENDGRID_TICKET_CREATED_TEMPLATE_ID_USER
SENDGRID_TICKET_DELETED_TEMPLATE_ID_USER = settings.SENDGRID_TICKET_DELETED_TEMPLATE_ID_USER
SENDGRID_TICKET_REJECTED_TEMPLATE_ID_USER = settings.SENDGRID_TICKET_REJECTED_TEMPLATE_ID_USER
SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER = settings.SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER
SENDGRID_BUCKET_CREATED_TEMPLATE_ID_USER = settings.SENDGRID_BUCKET_CREATED_TEMPLATE_ID_USER
# sendgrid templates for admins
SENDGRID_TICKET_CREATED_TEMPLATE_ID_ADMIN = settings.SENDGRID_TICKET_CREATED_TEMPLATE_ID_ADMIN
SENDGRID_TICKET_DELETED_TEMPLATE_ID_ADMIN = settings.SENDGRID_TICKET_DELETED_TEMPLATE_ID_ADMIN
SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN = settings.SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN

class Mail(EmailMessage):
    def __init__(self, ticket, status):
        ticket_url = os.environ.get("AZURE_SITES_URL")
        logger.info("status = " + status)
        # general dynamic data for all emails
        dynamic_template_data = {
            "name": ticket.name,
            "study_name": ticket.study_name,
            "ticket_url": f"{ticket_url}/{ticket.id}/update",
            "ticket_status": status            
        }

        # create email message object and fill in the details
        # in tandem with the user's email
        self.admin_email = EmailMessage(from_email=NO_REPLY_EMAIL)
        self.admin_email.to = [ADMIN_EMAIL]
		
        # create message
        if status == "Created":
            self.template_id = SENDGRID_TICKET_CREATED_TEMPLATE_ID_USER
            self.admin_email.template_id = SENDGRID_TICKET_CREATED_TEMPLATE_ID_ADMIN
            # attach other data here

        # delete message
        elif status == "Deleted":
            self.template_id = SENDGRID_TICKET_DELETED_TEMPLATE_ID_USER
            self.admin_email.template_id = SENDGRID_TICKET_DELETED_TEMPLATE_ID_ADMIN
            # attach other data here

        # rejected message: Data Intake Form Rejected
        elif status == STATUS_TYPES[0]:
            self.template_id = SENDGRID_TICKET_REJECTED_TEMPLATE_ID_USER
            self.admin_email.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN
            # attach rejected_reason
            dynamic_template_data["rejected_reason"] = ticket.ticket_review_comment

        # bucket created message: Awaiting Data Custodian Upload Start
        elif status == STATUS_TYPES[3]:
            self.template_id = SENDGRID_BUCKET_CREATED_TEMPLATE_ID_USER
            self.admin_email.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN
            # attach other data here

        # data upload completed message: Awaiting Gen3 Acceptance
        elif status == STATUS_TYPES[5]:
            self.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER
            self.admin_email.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN
            # attach other data here

        # update message
        else:
            self.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER
            self.admin_email.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN
            # attach ticket_status


        self.admin_email.dynamic_template_data = dynamic_template_data
        self.dynamic_template_data = dynamic_template_data

        super().__init__(
            from_email=NO_REPLY_EMAIL,
            to=[ticket.email],
        )

    def send(self, fail_silently=False):
        result = 0	  
        # send emails out to the admin
        try:   
        	logger.info("Attempting to send admin email.")     
        	self.admin_email.send(fail_silently)
        	logger.info("Attempting to send email data custodian email.")             
        	result = super().send(fail_silently)
        # SendGrid email error handling: https://github.com/sendgrid/sendgrid-python/blob/main/use_cases/error_handling.md        	
        except BadHeaderError:             
	        logger.error('Invalid header found for email.')
        except SMTPException as e: 
	        logger.error('SMTP exception when sending email: ' + e)
        except exceptions.BadRequestsError as e:
	        logger.error('BadRequestsHeader for email.')
	        logger.error(e.body)        
        except:  
	        logger.error("Mail Sending Failed for email to")  
	            
        return result
