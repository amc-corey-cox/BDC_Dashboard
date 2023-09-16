from django.conf import settings
import requests

JIRA_FIELDS = {
  "parent": "parent",
  "labels": "labels",
  "summary": "Data Set Name",
  "assignee": "Current Assignee",
  "reporter": "Ticket Creator",
  "customfield_12004": "Target Start Date",
  "customfield_12005": "Target End Date",
  "description": "Data Set Information",
  "issuelinks": "issuelinks",
  "attachment": "attachment",
  "customfield_15000": "Additional Data Requirements",
  "customfield_15001": "blockers",
  "customfield_15200": "Award Identifier",
  "customfield_15201": "Award Entity",
  "customfield_15202": "contacts",
  "customfield_15203": "Study Name",
  "customfield_15204": "Dataset Name",
  "customfield_15205": "Version Update",
  "customfield_15206": "Accession Number",
  "customfield_15301": "Accession Version",
  "customfield_15207": "Bucket URL",
  "customfield_15208": "Gen(3) Project Name(s)",
  "customfield_15209": "Gen(3) Project Name",
  "customfield_15210": "Data Generator Message",
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
        self.fields = JIRA_FIELDS

    def get_data(self, api_endpoint):
        response = requests.get(self.base_url + api_endpoint, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_board_config(self):
        api_endpoint = f"/rest/agile/1.0/board/{self.board_id}/configuration"
        return self.get_data(api_endpoint)

    def get_fields_info(self):
        api_endpoint = f"/rest/api/2/field"
        field_info_list = self.get_data(api_endpoint)
        return {field["id"]: field for field in field_info_list if field["id"] in self.fields}

    def get_fields_string(self, fields=None):
        if fields is None:
            fields = self.fields.keys()
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
