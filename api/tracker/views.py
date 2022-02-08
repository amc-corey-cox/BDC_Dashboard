from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from datetime import datetime, timezone
from .models import Ticket, User, STATUS_TYPES
from .mail import Mail


class IndexView(TemplateView):
    template_name = "tracker/index.html"


class UserDocsView(TemplateView):
    template_name = "tracker/user_docs.html"


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
        Mail(ticket_obj, "Created").send()
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

        return context

    # handle ticket status logic
    def form_valid(self, form):
        status_update = self.request.POST.get("status_update")
        ticket = form.save(commit=False)

        # extract user data
        user = self.request.user
        email = user.email

        # check which status button was clicked
        if status_update == "Approve Ticket":
            # set status to "Awaiting NHLBI Cloud Bucket Creation"
            ticket.ticket_approved_dt = datetime.now(timezone.utc)
            ticket.ticket_approved_by = email
        if status_update == "Reject Ticket":
            # add rejected timestamp
            ticket.ticket_rejected_dt = datetime.now(timezone.utc)
            ticket.ticket_rejected_by = email
        if status_update == "Mark as Bucket Created":
            # set status to "Awaiting Data Custodian Upload Start"
            ticket.bucket_created_dt = datetime.now(timezone.utc)
            ticket.bucket_created_by = email
        if status_update == "Mark as Data Upload Started":
            # set status to "Awaiting Data Custodian Upload Complete"
            ticket.data_uploaded_started_dt = datetime.now(timezone.utc)
            ticket.data_uploaded_started_by = email
        if status_update == "Mark as Data Upload Completed":
            # set status to "Awaiting Gen3 Acceptance"
            ticket.data_uploaded_completed_dt = datetime.now(timezone.utc)
            ticket.data_uploaded_completed_by = email
        if status_update == "Mark as Gen3 Approved":
            # set status to "Gen3 Accepted"
            ticket.data_accepted_dt = datetime.now(timezone.utc)
            ticket.data_accepted_by = email
        if status_update == "Revive Ticket":
            # remove rejected timestamp
            ticket.ticket_rejected_dt = None
            ticket.ticket_rejected_by = email

        ticket.save()
        self.object = ticket

        # send email with status update
        Mail(ticket, ticket.get_ticket_status[1]).send()
        return super().form_valid(form)


class TicketDelete(PermissionRequiredMixin, DeleteView):
    permission_required = "is_staff"
    model = Ticket
    success_url = reverse_lazy("tracker:tickets-list")

    def delete(self, request, *args, **kwargs):
        ticket = self.get_object()

        # send email notification
        Mail(ticket, "Deleted").send()
        return super().delete(request, *args, **kwargs)


class TicketsList(LoginRequiredMixin, ListView):
    model = Ticket
    context_object_name = "tickets"

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        queryset = self.object_list
        user = self.request.user

        # generate a list of status types
        context["awaiting_review"] = []
        context["awaiting_bucket_creation"] = []
        context["awaiting_data_upload_start"] = []
        context["awaiting_data_upload_complete"] = []
        context["awaiting_gen3_approval"] = []
        context["gen3_accepted"] = []
        context["rejected"] = []

        # iterate through all tickets and sort accordingly
        for object in queryset:
            # only add object to list if user has perms
            if object.created_by.email != user.email and not user.is_staff:
                continue

            # calculate last updated and set colors
            object.last_updated = (
                datetime.now(timezone.utc) - object.get_ticket_status[0]
            ).days
            object.status_color = object.get_ticket_status[2]
            if object.last_updated > 14:
                object.last_updated_color = "text-red"
            elif object.last_updated > 7:
                object.last_updated_color = "text-yellow"

            # filter tickets by status
            status = object.get_ticket_status[1]
            if status == STATUS_TYPES[1]:
                # Awaiting Review
                context["awaiting_review"].append(object)
            elif status == STATUS_TYPES[2]:
                # Awaiting Bucket Creation
                context["awaiting_bucket_creation"].append(object)
            elif status == STATUS_TYPES[3]:
                # Awaiting Data Upload
                context["awaiting_data_upload_start"].append(object)
            elif status == STATUS_TYPES[4]:
                # Data Upload in Progress
                context["awaiting_data_upload_complete"].append(object)
            elif status == STATUS_TYPES[5]:
                # Awaiting Gen3 Approval
                context["awaiting_gen3_approval"].append(object)
            elif status == STATUS_TYPES[6]:
                # Gen3 Accepted
                context["gen3_accepted"].append(object)
            else:
                # Data Intake Form Rejected
                context["rejected"].append(object)

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
