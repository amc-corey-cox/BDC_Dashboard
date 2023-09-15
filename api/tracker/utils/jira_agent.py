from django.conf import settings
import requests
import json


class JiraAgent:
    def __init__(self):
        self.jira_token = settings.JIRA_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.jira_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.base_url = settings.JIRA_BASE_URL
        self.board_id = settings.JIRA_BOARD_ID
        self.board_config = self.get_board_config()

        with open('tracker/utils/jira_fields.json', 'r') as file:
            jira_fields_data = json.load(file)
        self.fields = jira_fields_data
        self.fields_string = self.get_fields_string()

    def get_data(self, api_endpoint):
        response = requests.get(self.base_url + api_endpoint, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_board_config(self):
        api_endpoint = f"/rest/agile/1.0/board/{self.board_id}/configuration"
        return self.get_data(api_endpoint)

    def get_fields_string(self):
        return "fields=" + ",".join(self.fields["issue_fields"])

    def get_board_issues(self):
        board_filter = self.board_config["filter"]
        api_endpoint = f"/rest/api/2/search?jql=filter={board_filter['id']}&{self.fields_string}"
        return self.get_data(api_endpoint)

    def get_issue(self, issue_id):
        api_endpoint = f"/rest/api/2/issue/" + issue_id + "/" + self.fields_string
        return self.get_data(api_endpoint)
