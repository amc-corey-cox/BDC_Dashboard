import re
# from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin, )
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .freshdesk_agent import FreshdeskAgent
# from .models import Ticket, User, STATUS_TYPES
from .models import User
from .jira_agent import JiraAgent, ISSUE_FIELDS
import logging

logger = logging.getLogger("django")


LIST_FIELDS = {
    "customfield_10005": "epic_link",
    "description": "description",
    "issuelinks": "issuelinks",
    "issuetype": "issuetype",
    "labels": "labels",
    "status": "status",
    "subtasks": "subtasks",
    "summary": "summary",
    "customfield_15203": "study_name",
    "customfield_15204": "study_dataset",
}


GENERATOR_FIELDS = {
    # "description": "description",
    "issuelinks": "issuelinks",
    # "issuetype": "issuetype",
    # "labels": "labels",
    # "status": "status",
    # "subtasks": "subtasks",
    "summary": "summary",
}

SUBTASK_NAMES = {
    "PRE-INGESTION": [
        "PRE-REG",
        "DBGAP-REG",
        "BDC-BUCKET-GEN",
        "DBGAP-SUB",
        "DATA PREP",
        "DATA-UPLOAD",
        "DATA-QC",
    ],
    "BDC DATA RELEASE": [
        "SB-DATA-RELEASE",
        "PS-DATA-RELEASE",
        "COMM-RELEASE",
    ],
}

SUBTASK_NAMES["BDC RELEASED"] = SUBTASK_NAMES["PRE-INGESTION"] + SUBTASK_NAMES["BDC DATA RELEASE"]

SUBTASK_REGEX = {status: re.compile('|'.join(SUBTASK_NAMES[status])) for status in SUBTASK_NAMES}
NO_MATCH_REGEX = re.compile(r'^$')


class DocumentationView(TemplateView):
    template_name = "tracker/user_docs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class AboutView(TemplateView):
    template_name = "tracker/about.html"


def filter_subtasks(issue, status_regex=re.compile(r'^$')):
    subtasks = []
    for subtask in issue['fields']['subtasks']:
        if status_regex.search(subtask['fields']['summary']):
            subtasks.append(subtask)
    issue['fields']['subtasks'] = subtasks


class TicketsList(LoginRequiredMixin, TemplateView):
    template_name = "tracker/ticket_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        jira_agent = JiraAgent()
        jira_board_statuses = jira_agent.get_board_statuses(remove_statuses=["Backlog", "BLOCKED"])
        context["workflow"] = jira_board_statuses

        # issues = jira_agent.get_issues_by_contact('corey@tislab.org', LIST_FIELDS)
        issues = jira_agent.get_issues_by_contact('staff', LIST_FIELDS)

        statuses = {}
        for idx, column in enumerate(jira_board_statuses):
            statuses[idx] = {}
            statuses[idx]["name"] = column["name"]
            statuses[idx]["ids"] = [status['id'] for status in column["statuses"]]
            statuses[idx]["issues"] = []
            column_regex = SUBTASK_REGEX.get(column["name"], NO_MATCH_REGEX)
            for issue in issues:
                if issue['fields']['status']['id'] in statuses[idx]["ids"]:
                    filter_subtasks(issue, column_regex)
                    statuses[idx]["issues"].append(issue)
            statuses[idx]["issues_count"] = len(statuses[idx]["issues"])

        context["statuses"] = statuses
        return context


class TicketDetail(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/ticket_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket_id = kwargs['pk']

        jira_agent = JiraAgent()
        freshdesk_agent = FreshdeskAgent()

        issue = jira_agent.get_issue(ticket_id)
        issue_status = issue['fields']['status']['name']
        issue_status = issue_status.upper() if issue_status != "Data Available" else "BDC RELEASED"

        status_regex = SUBTASK_REGEX.get(issue_status, NO_MATCH_REGEX)
        filter_subtasks(issue, status_regex)
        context["issue"] = issue

        jira_board_statuses = jira_agent.get_board_statuses(["Backlog", "BLOCKED"], issue['fields']['status']['name'])
        context["workflow"] = jira_board_statuses

        # Group the fields into sections
        sections = {
            "Study": ["summary", "description", "status"],
            "Assignee and Reporter": ["assignee", "reporter"],
            "Dates": ["customfield_12004", "customfield_12005"],
            "Custom Fields": ["customfield_15000",  # "customfield_15001",
                              "customfield_15200", "customfield_15201",
                              "customfield_15202", "customfield_15203",  # "customfield_15205", "customfield_15301",
                              "customfield_15206", "customfield_15204", "customfield_15208",  # "customfield_15207",
                              "customfield_15209", "customfield_15210"],
            "Others": [  # "customfield_10005", #"parent",
                       "labels",  # "issuelinks", "subtasks",
                       "attachment"],
        }

        issue_content = {}
        for title, fields in sections.items():
            issue_content[title] = {}
            issue_content[title]["title"] = title
            issue_content[title]["fields"] = {}
            for field in fields:
                issue_content[title]['fields'][field] = {
                    "name": ISSUE_FIELDS[field],
                    "value": issue["fields"][field],
                }
                # if type(issue["fields"][field]) is list:
                #     issue_content[title]["fields"][field]["value"] = ", ".join(issue["fields"][field])
                if type(issue["fields"][field]) is dict:
                    issue_content[title]["fields"][field]["value"] = issue["fields"][field]["name"]
                # else:
                #     issue_content[title]["fields"][field]["value"] = issue["fields"][field]

        context["issue_content"] = issue_content

        context["freshdesk_issues"] = freshdesk_agent.get_data()
        return context


class CreateSubmission(TemplateView):
    template_name = "tracker/create_submission.html"

    freshdesk_agent = FreshdeskAgent()


class UserProfile(TemplateView):
    template_name = "tracker/profile.html"
    model = User
