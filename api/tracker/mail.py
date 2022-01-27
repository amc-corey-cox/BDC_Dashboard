import os
from django.conf import settings
from django.core.mail import EmailMessage

ADMIN_EMAIL = settings.SENDGRID_ADMIN_EMAIL
SENDGRID_TICKET_CREATED_TEMPLATE_ID = "d-d4c3414e680e415ba59c9fecc760ead4"
SENDGRID_TICKET_UPDATED_TEMPLATE_ID = "d-c8b625239d834a3aac57d84e1b9ea340"
SENDGRID_TICKET_DELETED_TEMPLATE_ID = "d-88ccfe3f976940e6ae8d5dd6c1d7ab65"


class Mail(EmailMessage):
    def __init__(self, ticket, status):
        ticket_url = os.environ.get("APP_ENGINE_URL")

        # create message
        if status == "Created":
            self.template_id = SENDGRID_TICKET_CREATED_TEMPLATE_ID
            self.dynamic_template_data = {
                "name": ticket.name,
                "study_name": ticket.study_name,
                "ticket_url": f"{ticket_url}{ticket.id}/update",
            }

        # delete message
        elif status == "Deleted":
            self.template_id = SENDGRID_TICKET_DELETED_TEMPLATE_ID
            self.dynamic_template_data = {
                "name": ticket.name,
                "study_name": ticket.study_name,
            }

        # update message
        else:
            self.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID
            self.dynamic_template_data = {
                "name": ticket.name,
                "ticket_status": status,
                "study_name": ticket.study_name,
                "ticket_url": f"{ticket_url}{ticket.id}/update",
            }

        super().__init__(
            from_email=ADMIN_EMAIL,
            to=[ADMIN_EMAIL, ticket.email],
        )
