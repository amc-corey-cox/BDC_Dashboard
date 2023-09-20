from django.conf import settings
import requests

# JIRA field names to descriptions
ISSUE_FIELDS = {
  "parent": "parent",
  "labels": "labels",
  "summary": "Data Set Name",
  "assignee": "Current Assignee",
  "reporter": "Ticket Creator",
  "customfield_12004": "Target Start Date",
  "customfield_12005": "Target End Date",
  "description": "Data Set Information",
  "issuelinks": "issuelinks",
  "subtasks": "subtasks",
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

# Lookup table for short field name to JIRA field names
FIELD_NAMES = {
    "parent": "parent",
    "labels": "labels",
    "summary": "summary",
    "assignee": "assignee",
    "reporter": "reporter",
    "start_date": "customfield_12004",
    "end_date": "customfield_12005",
    "description": "description",
    "issuelinks": "issuelinks",
    "subtasks": "subtasks",
    "attachment": "attachment",
    "requirements": "customfield_15000",
    "blockers": "customfield_15001",
    "award_id": "customfield_15200",
    "award_entity": "customfield_15201",
    "contacts": "customfield_15202",
    "study_name": "customfield_15203",
    "dataset_name": "customfield_15204",
    "version_update": "customfield_15205",
    "accession_number": "customfield_15206",
    "accession_version": "customfield_15301",
    "bucket_url": "customfield_15207",
    "gen3_names": "customfield_15208",
    "gen3_name": "customfield_15209",
    "message": "customfield_15210",
    "status": "status",
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
        self.fields = ISSUE_FIELDS
        self.field_names = FIELD_NAMES

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

    def get_dg_by_contact(self, contact, fields=None):
        project = "BDJW"
        issuetype = "12900"
        fields_string = self.get_fields_string(fields)
        api_search = f"rest/api/2/search?jql=project={project}+AND+issuetype={issuetype}"
        # f"/rest/api/2/search?jql=&{fields_string}"
        api_filter = ""
        if contact != "staff":
            api_filter = f"cf[15202]+~+{contact}"
        api_endpoint = api_search + "+" + api_filter + "&" + fields_string
        return self.get_data(api_endpoint)["issues"]

    def get_issue(self, issue_id, fields=None):
        fields_string = self.get_fields_string(fields)
        api_endpoint = f"/rest/api/2/issue/" + issue_id + "?" + fields_string
        return self.get_data(api_endpoint)
