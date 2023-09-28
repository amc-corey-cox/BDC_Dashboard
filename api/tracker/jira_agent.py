from django.conf import settings
import requests

# JIRA field names to descriptions
ISSUE_FIELDS = {
  "customfield_10005": "Epic Link",
  "parent": "Parent",
  "labels": "Labels",
  "summary": "Data Set Name",
  "assignee": "Current Assignee",
  "reporter": "Ticket Creator",
  "customfield_12004": "Target Start Date",
  "customfield_12005": "Target End Date",
  "description": "Data Set Information",
  "issuelinks": "Issuelinks",
  "subtasks": "Subtasks",
  "attachment": "Attachment",
  "customfield_15000": "Additional Data Requirements",
  "customfield_15001": "Blockers",
  "customfield_15200": "Award Identifier",
  "customfield_15201": "Award Entity",
  "customfield_15202": "Contacts",
  "customfield_15203": "Study Name",
  "customfield_15204": "Dataset Name",
  "customfield_15205": "Version Update",
  "customfield_15206": "Accession Number",
  "customfield_15301": "Accession Version",
  "customfield_15207": "Bucket URL",
  "customfield_15208": "Gen(3) Project Name(s)",
  "customfield_15209": "Gen(3) Project Name",
  "customfield_15210": "Data Generator Message",
  "status": "Status"
}

# Lookup table for short field name to JIRA field names
FIELD_NAMES = {
    "epic_link": "customfield_10005",
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
        self.project = settings.JIRA_PROJECT
        self.epic_issuetype = settings.JIRA_EPIC_ISSUETYPE
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

    def get_board_statuses(self, remove_statuses=None, selected_status=""):
        all_statuses = self.board_config["columnConfig"]["columns"]
        statuses = [status for status in all_statuses if status["name"] not in remove_statuses]

        if selected_status == "Data Available":
            selected_status = "BDC RELEASED"
        for status in statuses:
            status["selected"] = status["name"] == selected_status.upper()

        return statuses

    def get_fields_info(self):
        api_endpoint = f"/rest/api/latest/field"
        field_info_list = self.get_data(api_endpoint)
        return {field["id"]: field for field in field_info_list if field["id"] in self.fields}

    def get_fields_string(self, fields=None):
        if fields is None:
            fields = self.fields.keys()
        return "fields=" + ",".join(fields)

    def get_board_issues(self, fields=None):
        board_filter = self.board_config["filter"]
        fields_string = self.get_fields_string(fields)
        api_endpoint = f"/rest/api/latest/search?jql=filter={board_filter['id']}&{fields_string}"
        return self.get_data(api_endpoint)

    def get_epics_by_contact(self, contact, fields=None):
        search_string = f"/rest/api/latest/search?jql=project={self.project}+AND+issuetype={self.epic_issuetype}"
        filter_string = "" if contact == "staff" else f"+AND+cf[15202]+~+'{contact}'"
        fields_string = self.get_fields_string(fields)
        api_endpoint = f"{search_string}{filter_string}&{fields_string}"
        return self.get_data(api_endpoint)["issues"]

    def get_issues_by_contact(self, contact, fields=None):
        epic_issues = self.get_epics_by_contact(contact, [FIELD_NAMES["contacts"], FIELD_NAMES["summary"]])
        epic_keys_string = ",".join([epic["key"] for epic in epic_issues])
        fields_string = self.get_fields_string(fields)
        api_endpoint = f"/rest/api/latest/search?jql=cf[10005]+in+({epic_keys_string})&{fields_string}"
        issues = self.get_data(api_endpoint)["issues"]
        for issue in issues:
            for epic in epic_issues:
                if issue["fields"]["customfield_10005"] == epic["key"]:
                    issue["fields"]["parent"] = epic
        return issues

    def get_issue(self, issue_id, fields=None):
        fields_string = self.get_fields_string(fields)
        api_endpoint = f"/rest/api/latest/issue/{issue_id}?{fields_string}"
        return self.get_data(api_endpoint)
