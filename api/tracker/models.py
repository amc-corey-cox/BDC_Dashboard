from django.db import models
from django.urls import reverse

# Ticket
# ------
# email
# name
# organization
# study_name
# dataset_desription
# is_test_data
# google_email
# aws_iam
# data_size
# study_id
# consent_code
# created_dt
#
# Status
# ------
# status_type
# status_dt


class Ticket(models.Model):
    email = models.EmailField(verbose_name="Email", default="")
    name = models.CharField(
        max_length=100,
        verbose_name="Name",
        help_text="Name of primary contact",
        default="",
    )
    organization = models.CharField(
        max_length=250,
        verbose_name="Organization",
        help_text="Name of requesting organization",
        default="",
    )
    study_name = models.CharField(
        max_length=250,
        verbose_name="Study Name",
        help_text="Name of Study or Dataset (if applicable)",
        blank=True,
        default="",
    )
    dataset_description = models.CharField(
        max_length=2500,
        verbose_name="Dataset Description",
        help_text="Describe the dataset you are uploading",
        blank=True,
        default="",
    )
    is_test_data = models.BooleanField(
        verbose_name="Is Test Data",
        help_text="Check this box if this is test data",
        blank=True,
        default=False,
    )
    google_email = models.EmailField(
        verbose_name="Google Email",
        help_text="If you're uploading to Google please provide your google email for access",
        blank=True,
        default="",
    )
    aws_iam = models.CharField(
        max_length=100,
        verbose_name="AWS IAM",
        help_text="If you're uploading to Amazon please provide your AWS IAM",
        blank=True,
        default="",
    )
    data_size = models.CharField(
        max_length=100,
        verbose_name="Data Size",
        help_text="Please provide an estimated size of your data set(s)",
        blank=True,
        default="",
    )
    study_id = models.CharField(
        max_length=100,
        verbose_name="Study ID",
        default="",
    )
    consent_code = models.CharField(
        max_length=100,
        verbose_name="Consent Code",
        default="",
    )

    created_dt = models.DateTimeField(verbose_name="Created Date", auto_now_add=True)
    ticket_approved_dt = models.DateTimeField(
        verbose_name="Intake Form Approved Date",
        null=True,
        blank=True,
    )
    ticket_rejected_dt = models.DateTimeField(
        verbose_name="Intake Form Rejected Date",
        null=True,
        blank=True,
    )
    bucket_created_dt = models.DateTimeField(
        verbose_name="Bucket Created Date",
        null=True,
        blank=True,
    )
    data_uploaded_started_dt = models.DateTimeField(
        verbose_name="Data Uploaded Started Date",
        null=True,
        blank=True,
    )
    data_uploaded_completed_dt = models.DateTimeField(
        verbose_name="Data Uploaded Completed Date",
        null=True,
        blank=True,
    )
    data_accepted_dt = models.DateTimeField(
        verbose_name="Gen3 Accepted Date",
        null=True,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("tracker:ticket-detail", kwargs={"pk": self.pk})

    def get_fields(self):
        return [
            (field.verbose_name, field.value_from_object(self))
            for field in self.__class__._meta.fields
        ]

    # get the ticket status based on the date time history
    @property
    def get_ticket_status(self):
        if self.ticket_rejected_dt:
            return (self.ticket_rejected_dt, STATUS_TYPES[0])
        elif self.data_accepted_dt:
            return (self.data_accepted_dt, STATUS_TYPES[6])
        elif self.data_uploaded_completed_dt:
            return (self.data_uploaded_completed_dt, STATUS_TYPES[5])
        elif self.data_uploaded_started_dt:
            return (self.data_uploaded_started_dt, STATUS_TYPES[4])
        elif self.bucket_created_dt:
            return (self.bucket_created_dt, STATUS_TYPES[3])
        elif self.ticket_approved_dt:
            return (self.ticket_approved_dt, STATUS_TYPES[2])
        else:
            return (self.created_dt, STATUS_TYPES[1])


STATUS_TYPES = {
    0: "Data Intake Form Rejected",
    1: "Ready for Bucket Creation",
    2: "Bucket Created; Ready for Data upload",
    3: "Ready for Data upload",
    4: "Data upload in Progress",
    5: "Data upload Complete",
    6: "Gen3 Accepted",
}
