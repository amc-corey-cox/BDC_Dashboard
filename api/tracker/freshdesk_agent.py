from django.conf import settings
import requests

# Freshdesk field names to descriptions
FRESHDESK_TICKET_FIELDS = {
    "subject": "Subject",
    "description": "Description",
    "status": "Status",
    "priority": "Priority",
    "type": "Type",
    "due_by": "Due By",
    "created_at": "Created At",
    "updated_at": "Updated At",
    "id": "Ticket ID",
    "requester_id": "Requester ID",
    "responder_id": "Responder ID",
    "group_id": "Group ID",
    "source": "Source",
    "company_id": "Company ID",
    "association_type": "Association Type",
    "support_email": "Support Email",
    "product_id": "Product ID",
    "is_escalated": "Is Escalated",
    "spam": "Spam",
    "email_config_id": "Email Config ID",
    "fr_due_by": "FR Due By",
    "fr_escalated": "FR Escalated",
    "nr_due_by": "NR Due By",
    "nr_escalated": "NR Escalated",
    "tags": "Tags",
    "cc_emails": "Copied Emails",
    "fwd_emails": "Forwarded Emails",
    "reply_cc_emails": "Reply Copied Emails",
    "ticket_cc_emails": "Ticket Copied Emails",
    "to_emails": "To Emails",
    "custom_fields": "Custom Fields",
}


class FreshdeskAgent:
    def __init__(self):
        self.base_url = settings.FRESHDESK_BASE_URL
        self.auth_user = settings.FRESHDESK_AUTH_USER
        self.auth_password = settings.FRESHDESK_AUTH_PASSWORD
        self.headers = {
            'Authorization': 'Basic d1hZVm5PdXd6T0VYWE5tUnhOd1c6WA==',
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.base_url = settings.FRESHDESK_BASE_URL
        self.fields = FRESHDESK_TICKET_FIELDS

    def get_data(self, api_endpoint, params=None):
        response = requests.get(self.base_url + api_endpoint, params=params, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_ticket_by_jira_issue_id(self, jira_id):
        params = {
            'query': f'\'custom_string:"{jira_id}"\'',
        }
        api_endpoint = f'/api/v2/search/tickets'
        return self.get_data(api_endpoint, params)["results"]
