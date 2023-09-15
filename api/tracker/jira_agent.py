from django.conf import settings
import requests

JIRA_FIELDS = {
  "parent": "parent",
  "labels": "labels",
  "summary": "summary",
  "components": "components",
  "priority": "priority",
  "assignee": "assignee",
  "reporter": "reporter",
  "customfield_12004": "customfield_12004",
  "customfield_12005": "customfield_12005",
  "description": "description",
  "issuelinks": "issuelinks",
  "attachment": "attachment",
  "comment": "comment",
  "customfield_15000": "customfield_15000",
  "customfield_15001": "customfield_15001",
  "customfield_15002": "customfield_15002",
  "customfield_15200": "customfield_15200",
  "customfield_15201": "customfield_15201",
  "customfield_15202": "customfield_15202",
  "customfield_15203": "customfield_15203",
  "customfield_15205": "customfield_15205",
  "customfield_15206": "customfield_15206",
  "customfield_15207": "customfield_15207",
  "customfield_15208": "customfield_15208",
  "customfield_15209": "customfield_15209",
  "customfield_15210": "customfield_15210",
  "status": "status"
}


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

        self.fields_data = JIRA_FIELDS
        self.fields = self.fields_data.keys()

    def get_data(self, api_endpoint):
        response = requests.get(self.base_url + api_endpoint, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_board_config(self):
        api_endpoint = f"/rest/agile/1.0/board/{self.board_id}/configuration"
        return self.get_data(api_endpoint)

    def get_fields_string(self, fields=None):
        if fields is None:
            fields = self.fields
        return "fields=" + ",".join(fields)

    def get_board_issues(self, fields=None):
        board_filter = self.board_config["filter"]
        fields_string = self.get_fields_string(fields)
        api_endpoint = f"/rest/api/2/search?jql=filter={board_filter['id']}&{fields_string}"
        return self.get_data(api_endpoint)

    def get_issue(self, issue_id, fields=None):
        fields_string = self.get_fields_string(fields)
        api_endpoint = f"/rest/api/2/issue/" + issue_id + "/" + fields_string
        return self.get_data(api_endpoint)
