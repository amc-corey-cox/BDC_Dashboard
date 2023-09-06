import jira

import requests
from django.conf import settings


class JiraInteraction:
    def __init__(self):
        self.api_url = settings.JIRA_API_URL
        self.headers = {
            "Authorization": f"Bearer {settings.JIRA_BEARER_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_data(self, api_endpoint):
        response = requests.get(self.api_url + api_endpoint, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_ticket(self, ticket_id):
        api_endpoint = f"/rest/api/2/issue/{ticket_id}"
        return self.get_data(api_endpoint)

