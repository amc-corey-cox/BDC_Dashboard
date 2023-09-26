import json
import re

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django import forms
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.forms.utils import ErrorList
from django.urls import reverse_lazy
from datetime import datetime, timezone
from .models import Ticket, User, STATUS_TYPES
from .jira_agent import JiraAgent, ISSUE_FIELDS
import logging

logger = logging.getLogger("django")


LIST_FIELDS = {
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


class IndexView(TemplateView):
    template_name = "tracker/index.html"


class DocumentationView(TemplateView):
    template_name = "tracker/user_docs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class AboutView(TemplateView):
    template_name = "tracker/about.html"


class CustodianInfoView(TemplateView):
    template_name = "tracker/custodian_instructions.html"


class TicketCreate(LoginRequiredMixin, CreateView):
    model = Ticket
    fields = [
        "email",
        "name",
        "organization",
        "study_name",
        "dataset_description",
        "is_test_data",
        "google_email",
        "aws_iam",
        "data_size",
        "study_id",
        "consent_code",
    ]

    # send email if form is valid
    def form_valid(self, form):
        ticket_obj = form.save(commit=False)
        ticket_obj.created_by = self.request.user
        ticket_obj.save()
        # NOTE: Development: Mail
        # Commented out until we get mail/SendGrid working
        # Mail(ticket_obj, "Created").send()
        return super().form_valid(form)


class TicketUpdate(LoginRequiredMixin, UpdateView):
    model = Ticket
    fields = [
        "name",
        "email",
        "organization",
        "study_name",
        "dataset_description",
        "is_test_data",
        "google_email",
        "aws_iam",
        "data_size",
        "study_id",
        "consent_code",
        "ticket_review_comment",
    ]

    # add status to context
    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["status"] = self.object.get_ticket_status
        context["staff"] = self.request.user.is_staff

        return context

    # handle ticket status logic
    def form_valid(self, form):
        status_update = self.request.POST.get("status_update")
        ticket = form.save(commit=False)

        # extract user data
        user = self.request.user
        email = user.email
        staff = user.is_staff

        if staff:
            if status_update == "Approve Ticket":
                # set status to "Awaiting NHLBI Cloud Bucket Creation"
                ticket.ticket_approved_dt = datetime.now(timezone.utc)
                ticket.ticket_approved_by = email
            elif status_update == "Reject Ticket":
                # add rejected timestamp
                ticket.ticket_rejected_dt = datetime.now(timezone.utc)
                ticket.ticket_rejected_by = email
            elif status_update == "Mark as Bucket Created":
                # set status to "Awaiting Data Custodian Upload Start"
                ticket.bucket_created_dt = datetime.now(timezone.utc)
                ticket.bucket_created_by = email
            elif status_update == "Mark as Data Upload Started":
                # set status to "Awaiting Data Custodian Upload Complete"
                ticket.data_uploaded_started_dt = datetime.now(timezone.utc)
                ticket.data_uploaded_started_by = email
            elif status_update == "Mark as Data Upload Completed":
                # set status to "Awaiting Gen3 Acceptance"
                ticket.data_uploaded_completed_dt = datetime.now(timezone.utc)
                ticket.data_uploaded_completed_by = email
            elif status_update == "Mark as Gen3 Approved":
                # set status to "Gen3 Accepted"
                ticket.data_accepted_dt = datetime.now(timezone.utc)
                ticket.data_accepted_by = email
            elif status_update == "Revive Ticket":
                # remove rejected timestamp
                ticket.ticket_rejected_dt = None
                ticket.ticket_rejected_by = email
            elif status_update == None:
                # if staff edits ticket
                logger.info("Ticket Updated by " + email)
            else:
                form.errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Only Staff are allowed to perform this action"]
                )
        else:
            if status_update == "Mark as Data Upload Started":
                # set status to "Awaiting Data Custodian Upload Complete"
                ticket.data_uploaded_started_dt = datetime.now(timezone.utc)
                ticket.data_uploaded_started_by = email
            elif status_update == "Mark as Data Upload Completed":
                # set status to "Awaiting Gen3 Acceptance"
                ticket.data_uploaded_completed_dt = datetime.now(timezone.utc)
                ticket.data_uploaded_completed_by = email
            elif (
                    status_update == None and ticket.get_ticket_status[1] == STATUS_TYPES[1]
            ):
                # if user edits ticket
                logger.info("Ticket Updated by " + email)
            else:
                form.errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Only Data Custodians are allowed to perform this action"]
                )

        ticket.save()
        self.object = ticket

        # send email with status update
        # NOTE: Development: Mail
        # Commented out until we get mail/SendGrid working
        # Mail(ticket, ticket.get_ticket_status[1]).send()
        return super().form_valid(form)


class TicketDelete(PermissionRequiredMixin, DeleteView):
    model = Ticket
    success_url = reverse_lazy("tracker:tickets-list")

    def has_permission(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        ticket = self.get_object()

        # send email notification
        # NOTE: Development: Mail
        # Commented out until we get mail/SendGrid working
        # Mail(ticket, "Deleted").send()
        return super().form_valid(form)


class TicketsList(LoginRequiredMixin, ListView):
    model = Ticket
    context_object_name = "tickets"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        jira_agent = JiraAgent()
        jira_board_config = jira_agent.get_board_config()
        data_generators = jira_agent.get_dg_by_contact('staff', GENERATOR_FIELDS)

        link_keys = []
        issues = []
        for data_generator in data_generators:
            for link in data_generator["fields"]["issuelinks"]:
                if link["outwardIssue"]["key"] not in link_keys:
                    link_keys.append(link["outwardIssue"]["key"])
                    issue = jira_agent.get_issue(link["outwardIssue"]["key"], LIST_FIELDS)
                    issue["fields"]["parent"] = data_generator
                    issues.append(issue)

        statuses = {}
        for idx, column in enumerate(jira_board_config["columnConfig"]["columns"]):
            if column["name"] == "Backlog" or column["name"] == "BLOCKED":
                continue
            statuses[idx] = {}
            statuses[idx]["name"] = column["name"]
            statuses[idx]["ids"] = [status['id'] for status in column["statuses"]]
            statuses[idx]["issues"] = []
            if column["name"] in SUBTASK_NAMES:
                column_regex = re.compile('|'.join(SUBTASK_NAMES[column["name"]]))
            else:
                column_regex = re.compile(r'^$')
            for issue in issues:
                if issue['fields']['status']['id'] in statuses[idx]["ids"]:
                    sub_tasks = []
                    for sub_task in issue['fields']['subtasks']:
                        if column_regex.search(sub_task['fields']['summary']):
                            sub_tasks.append(sub_task)
                    issue['fields']['subtasks'] = sub_tasks
                    statuses[idx]["issues"].append(issue)
            statuses[idx]["issues_count"] = len(statuses[idx]["issues"])

        context["statuses"] = statuses

        return context


class TicketDetail(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/ticket_detail.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     ticket_id = kwargs['pk']  # Assuming 'pk' is the primary key of the ticket
    #
    #     # Fetch ticket data from Jira using your library or API calls
    #     # Replace this with actual code to fetch ticket data from Jira
    #     # jira_ticket_data = jira_api_library.fetch_ticket_data(ticket_id)
    #
    #     # Pass the ticket data to the template
    #     context['jira_ticket_data'] = ticket_id
    #
    #     return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket_id = kwargs['pk']

        jira_agent = JiraAgent()
        issue = jira_agent.get_issue(ticket_id)

        # Group the fields into sections
        sections = {
            "Study": ["summary", "description", "status"],
            "Assignee and Reporter": ["assignee", "reporter"],
            "Dates": ["customfield_12004", "customfield_12005"],
            "Custom Fields": ["customfield_15000", "customfield_15001", "customfield_15200", "customfield_15201",
                              "customfield_15202", "customfield_15203", "customfield_15204", #"customfield_15205",
                              "customfield_15206", "customfield_15301", "customfield_15207", "customfield_15208",
                              "customfield_15209", "customfield_15210"],
            "Others": [# "customfield_10005", #"parent",
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

        context["issue"] = issue
        context["issue_content"] = issue_content
        return context


class RejectedTicketsList(PermissionRequiredMixin, ListView):
    permission_required = "is_staff"
    template_name = "tracker/ticket_rejected_list.html"
    model = Ticket

    context_object_name = "tickets"

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        queryset = self.object_list

        # generate a list of status types
        context["rejected"] = []

        # iterate through all tickets and sort rejected tickets
        for object in queryset:
            # Data Intake Form Rejected
            status = object.get_ticket_status[1]
            if status == STATUS_TYPES[0]:
                object.last_updated = (
                        datetime.now(timezone.utc) - object.get_ticket_status[0]
                ).days
                object.status_color = object.get_ticket_status[2]

                # filter tickets by status
                context["rejected"].append(object)

        return context


class UserProfile(TemplateView):
    template_name = "tracker/profile.html"
    model = User
