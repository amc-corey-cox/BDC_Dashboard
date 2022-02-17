import os
from django.conf import settings
from django.core.mail import EmailMessage
from .models import STATUS_TYPES


# admin emails (add more here)
NO_REPLY_EMAIL = settings.SENDGRID_NO_REPLY_EMAIL
ADMIN_EMAIL = settings.SENDGRID_ADMIN_EMAIL


# sendgrid templates for users
SENDGRID_TICKET_CREATED_TEMPLATE_ID_USER = "d-d4c3414e680e415ba59c9fecc760ead4"
SENDGRID_TICKET_DELETED_TEMPLATE_ID_USER = "d-88ccfe3f976940e6ae8d5dd6c1d7ab65"
SENDGRID_TICKET_REJECTED_TEMPLATE_ID_USER = "d-3e07572d9d29445e8763aa7c8c98fc1d"
SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER = "d-c8b625239d834a3aac57d84e1b9ea340"
SENDGRID_BUCKET_CREATED_TEMPLATE_ID_USER = "d-f485f19f51ea48758ef41ba8b56a3c90"

# sendgrid templates for admins
SENDGRID_TICKET_CREATED_TEMPLATE_ID_ADMIN = "d-8150144b88434ccea5acda12857793d0"
SENDGRID_TICKET_DELETED_TEMPLATE_ID_ADMIN = "d-4429c4f8335d4185bc96cda80305055d"
SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN = "d-4305969f01f84d699d14da0bffa8dbd6"
SENDGRID_DATA_UPLOAD_COMPLETED_TEMPLATE_ID_ADMIN = "d-22bce004d5f94d7f9649cab2156e767c"


class Mail(EmailMessage):
    def __init__(self, ticket, status):
        ticket_url = os.environ.get("APP_ENGINE_URL")

        # general dynamic data for all emails
        dynamic_template_data = {
            "name": ticket.name,
            "study_name": ticket.study_name,
            "ticket_url": f"{ticket_url}{ticket.id}/update",
        }

        # create email message object and fill in the details
        # in tandem with the user's email
        self.admin_email = EmailMessage(from_email=NO_REPLY_EMAIL)

        # create message
        if status == "Created":
            self.template_id = SENDGRID_TICKET_CREATED_TEMPLATE_ID_USER

            self.admin_email.template_id = SENDGRID_TICKET_CREATED_TEMPLATE_ID_ADMIN
            self.admin_email.to = [ADMIN_EMAIL]

            # attach other data here

        # delete message
        elif status == "Deleted":
            self.template_id = SENDGRID_TICKET_DELETED_TEMPLATE_ID_USER

            self.admin_email.template_id = SENDGRID_TICKET_DELETED_TEMPLATE_ID_ADMIN
            self.admin_email.to = [ADMIN_EMAIL]

            # attach other data here

        # rejected message: Data Intake Form Rejected
        elif status == STATUS_TYPES[0]:
            self.template_id = SENDGRID_TICKET_REJECTED_TEMPLATE_ID_USER

            self.admin_email.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN
            self.admin_email.to = [ADMIN_EMAIL]

            # attach rejected_reason
            dynamic_template_data["rejected_reason"] = ticket.ticket_review_comment

        # bucket created message: Awaiting Data Custodian Upload Start
        elif status == STATUS_TYPES[3]:
            self.template_id = SENDGRID_BUCKET_CREATED_TEMPLATE_ID_USER

            self.admin_email.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN
            self.admin_email.to = [ADMIN_EMAIL]

            # attach other data here

        # data upload completed message: Awaiting Gen3 Acceptance
        elif status == STATUS_TYPES[5]:
            self.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER

            self.admin_email.template_id = (
                SENDGRID_DATA_UPLOAD_COMPLETED_TEMPLATE_ID_ADMIN
            )
            self.admin_email.to = [ADMIN_EMAIL]

            # attach other data here

        # update message
        else:
            self.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER

            self.admin_email.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN
            self.admin_email.to = [ADMIN_EMAIL]

            # attach ticket_status
            dynamic_template_data["ticket_status"] = status

        self.admin_email.dynamic_template_data = dynamic_template_data
        self.dynamic_template_data = dynamic_template_data

        super().__init__(
            from_email=NO_REPLY_EMAIL,
            to=[ticket.email],
        )

    def send(self, fail_silently=False):
        # send emails out to the admin
        self.admin_email.send(fail_silently)
        return super().send(fail_silently)
