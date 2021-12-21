from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator

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


STATUS_TYPES = {
    0: "Data Intake Form Rejected",
    1: "Awaiting NHLBI Review",
    2: "Awaiting NHLBI Cloud Bucket Creation",
    3: "Awaiting Custodian Upload Start",
    4: "Awaiting Custodian Upload Complete",
    5: "Awaiting Gen3 Acceptance",
    6: "Gen3 Accepted",
}


AWS_IAM_VALIDATOR = RegexValidator(
    r"^arn:aws:iam::[0-9]{12}:user/[a-zA-Z0-9-_]{1,64}$",
    "AWS IAM format invalid. Please use the following format: arn:aws:iam::123456789012:user/username",
)
GOOGLE_EMAIL_VALIDATOR = RegexValidator()
STUDY_ID_AND_CONSENT_CODE_REGEX = r"^[a-z0-9][a-z0-9.]{0,59}[a-z0-9]$"
STUDY_ID_VALIDATOR = RegexValidator(
    STUDY_ID_AND_CONSENT_CODE_REGEX,
    "Study ID format invalid",
)
CONSENT_CODE_VALIDATOR = RegexValidator(
    STUDY_ID_AND_CONSENT_CODE_REGEX,
    "Consent Code format invalid",
)


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
        help_text="Name of Study or Dataset",
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
        help_text="If you're uploading to Google, please provide your google email for access",
        blank=True,
        default="",
    )
    aws_iam = models.CharField(
        max_length=100,
        verbose_name="AWS IAM",
        help_text="If you're uploading to Amazon, please provide your AWS IAM (ex: arn:aws:iam::123456789012:user/username)",
        blank=True,
        default="",
        validators=[AWS_IAM_VALIDATOR],
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
        help_text="Please refer to Data Custodian Instructions for more information",
        default="",
        validators=[STUDY_ID_VALIDATOR],
    )
    consent_code = models.CharField(
        max_length=100,
        verbose_name="Consent Code",
        help_text="Please refer to Data Custodian Instructions for more information",
        default="",
        validators=[CONSENT_CODE_VALIDATOR],
    )

    ticket_review_comment = models.CharField(
        max_length=1000,
        verbose_name="Ticket Review Comment",
        help_text="Please provide a comment for approval or rejection",
        blank=True,
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

    # ideally this is used to track ticket updates
    last_updated_dt = models.DateTimeField(
        verbose_name="Last Updated Date", auto_now=True
    )

    def get_absolute_url(self):
        return reverse("tracker:ticket-update", kwargs={"pk": self.pk})

    def get_fields(self):
        return [
            (field.verbose_name, field.value_from_object(self))
            for field in self.__class__._meta.fields
        ]

    # get the ticket status based on the date time history
    @property
    def get_ticket_status(self):
        if self.ticket_rejected_dt:
            return (self.ticket_rejected_dt, STATUS_TYPES[0], "danger")
        elif self.data_accepted_dt:
            return (self.data_accepted_dt, STATUS_TYPES[6], "success")
        elif self.data_uploaded_completed_dt:
            return (self.data_uploaded_completed_dt, STATUS_TYPES[5], "secondary")
        elif self.data_uploaded_started_dt:
            return (self.data_uploaded_started_dt, STATUS_TYPES[4], "dark")
        elif self.bucket_created_dt:
            return (self.bucket_created_dt, STATUS_TYPES[3], "dark")
        elif self.ticket_approved_dt:
            return (self.ticket_approved_dt, STATUS_TYPES[2], "warning")
        else:
            return (self.created_dt, STATUS_TYPES[1], "primary")
