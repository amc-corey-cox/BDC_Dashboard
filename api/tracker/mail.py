import os
from django.conf import settings
from django.core.mail import EmailMessage


# admin emails (add more here)
NO_REPLY_EMAIL = "ann@nimbusinformatics.com"
ADMIN_EMAIL = settings.SENDGRID_ADMIN_EMAIL


# sendgrid templates for users
SENDGRID_TICKET_CREATED_TEMPLATE_ID_USER = "d-d4c3414e680e415ba59c9fecc760ead4"
SENDGRID_TICKET_DELETED_TEMPLATE_ID_USER = "d-88ccfe3f976940e6ae8d5dd6c1d7ab65"
SENDGRID_TICKET_REJECTED_TEMPLATE_ID_USER = "d-3e07572d9d29445e8763aa7c8c98fc1d"
SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER = "d-c8b625239d834a3aac57d84e1b9ea340"

# sendgrid templates for admins (TODO: replace these)
SENDGRID_TICKET_CREATED_TEMPLATE_ID_ADMIN = "d-d4c3414e680e415ba59c9fecc760ead4"
SENDGRID_TICKET_DELETED_TEMPLATE_ID_ADMIN = "d-88ccfe3f976940e6ae8d5dd6c1d7ab65"
SENDGRID_TICKET_REJECTED_TEMPLATE_ID_ADMIN = "d-3e07572d9d29445e8763aa7c8c98fc1d"
SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN = "d-c8b625239d834a3aac57d84e1b9ea340"


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

            # TODO: these are just placeholders
            self.admin_email.template_id = SENDGRID_TICKET_CREATED_TEMPLATE_ID_ADMIN
            self.admin_email.to = [ADMIN_EMAIL]

            # attach other data here

        # delete message
        elif status == "Deleted":
            self.template_id = SENDGRID_TICKET_DELETED_TEMPLATE_ID_USER

            # TODO: these are just placeholders
            self.admin_email.template_id = SENDGRID_TICKET_DELETED_TEMPLATE_ID_ADMIN
            self.admin_email.to = [ADMIN_EMAIL]

            # attach other data here

        # rejected message
        elif status == "Data Intake Form Rejected":
            self.template_id = SENDGRID_TICKET_REJECTED_TEMPLATE_ID_USER

            # TODO: these are just placeholders
            self.admin_email.template_id = SENDGRID_TICKET_REJECTED_TEMPLATE_ID_ADMIN
            self.admin_email.to = [ADMIN_EMAIL]

            # attach rejected_reason
            dynamic_template_data["rejected_reason"] = ticket.ticket_review_comment

        # update message
        else:
            self.template_id = SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER

            # TODO: these are just placeholders
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
