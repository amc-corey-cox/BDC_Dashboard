import os
from django.core.mail import EmailMultiAlternatives

ADMIN_EMAIL = "ltran@asymmetrik.com"
CREATED_EMAIL_TEMPLATE_ID = "d-53af24658b434635bbdaf80a03bc1375"


class Mail(EmailMultiAlternatives):
    def __init__(self, ticket, status):
        ticket_url = os.environ.get("APP_ENGINE_URL")

        # create message
        if status == "Created":
            self.template_id = CREATED_EMAIL_TEMPLATE_ID
            self.substitutions = {
                "name": ticket.name,
                "study_name": ticket.study_name,
                "ticket_url": f"{ticket_url}/{ticket.id}/update",
            }

        elif status == "Deleted":
            subject = "BDCAT TRACKER: Ticket Deleted"
            body = f"{ticket.name} has deleted a ticket.\n\n"
            to = [ADMIN_EMAIL, ticket.email]
        else:
            subject = "BDCAT TRACKER: Ticket Updated"
            body = f"{ticket.study_name} has been moved to {ticket.get_ticket_status[1]}\n\n"
            to = [ADMIN_EMAIL, ticket.email]

        super().__init__(
            from_email=ADMIN_EMAIL,
            to=[ADMIN_EMAIL, ticket.email],
        )

    def send(self, fail_silently=False):
        return super().send(fail_silently)
