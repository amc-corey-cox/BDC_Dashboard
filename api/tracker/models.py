import logging

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator, \
    MaxLengthValidator, validate_ipv4_address
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from simple_history.models import HistoricalRecords
from allauth.account.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .validators import NegateValidator

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
    3: "Awaiting Data Custodian Upload Start",
    4: "Awaiting Data Custodian Upload Complete",
    5: "Awaiting Gen3 Acceptance",
    6: "Gen3 Accepted",
}

DATA_UNIT_CHOICES = (
    ("mb", "MB"),
    ("gb", "GB"),
    ("tb", "TB"),
    ("pb", "PB"),
)

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
    "dbGaP Consent Group Code format invalid",
)
DATA_SIZE_VALIDATOR = RegexValidator(
    r"^[0-9]{1,5}(.[0-9]{1,5})?\s?(MB|GB|TB|PB)$",
    "Data Size format invalid. Please add a unit of measurement (MB, GB, TB, PB)",
)

logger = logging.getLogger("django")

class Ticket(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Name",
        help_text="Name of primary contact",
        default="",
    )
    email = models.EmailField(verbose_name="Email", default="")
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
    study_id = models.CharField(
        max_length=100,
        verbose_name="Study ID",
        help_text="Please refer to Data Custodian Instructions for more information",
        default="",
        validators=[STUDY_ID_VALIDATOR],
    )
    consent_code = models.CharField(
        max_length=100,
        verbose_name="dbGaP Consent Group Code",
        help_text="Please refer to Data Custodian Instructions for more information",
        default="",
        validators=[CONSENT_CODE_VALIDATOR],
    )
    data_size = models.CharField(
        max_length=100,
        verbose_name="Data Size",
        help_text="Please provide an estimated size of your data set(s) (ex. 100 GB)",
        default="",
        validators=[DATA_SIZE_VALIDATOR],
    )

    dataset_description = models.CharField(
        max_length=2500,
        verbose_name="Dataset Description",
        help_text="Describe the dataset you are uploading",
        blank=True,
        default="",
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
        help_text="If you're uploading to Amazon, please provide your AWS IAM ARN (ex: arn:aws:iam::123456789012:user/username)",
        blank=True,
        default="",
        validators=[AWS_IAM_VALIDATOR],
    )
    is_test_data = models.BooleanField(
        verbose_name="Is Test Data",
        help_text="Check this box if this is test data",
        blank=True,
        default=False,
    )

    ticket_review_comment = models.CharField(
        max_length=1000,
        verbose_name="Ticket Review Comment",
        help_text="Please provide a comment for approval or rejection",
        blank=True,
        default="",
    )

    # time date fields
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

    # append name to log
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    ticket_approved_by = models.EmailField(
        verbose_name="Ticket approved by", default=""
    )
    ticket_rejected_by = models.EmailField(
        verbose_name="Ticket rejected by", default=""
    )
    bucket_created_by = models.EmailField(verbose_name="Bucket created by", default="")
    data_uploaded_started_by = models.EmailField(
        verbose_name="Data upload started by", default=""
    )
    data_uploaded_completed_by = models.EmailField(
        verbose_name="Data upload completed by", default=""
    )
    data_accepted_by = models.EmailField(verbose_name="Data accepted by", default="")

    # Bucket Names
    data_bucket_name = models.CharField(
        max_length=250,
        verbose_name="Data Bucket Name",
        help_text="Name of Cloud Data Bucket",
        blank=True,
        default="",
        validators=[
            MinLengthValidator(
                3,
                "Bucket name must have at least 3 characters"
            ),
            MaxLengthValidator(
                63,
                "Bucket can be no more than 63 characters"
            ),
            RegexValidator(
                r'^[a-z.0-9-]*$',
                "Bucket name can only contain lower case letters, decimals,"
                + " numbers, and hyphens"
            ),
            RegexValidator(
                r'^[a-z0-9].*[a-z0-9]$',
                " Bucket name must begin and end in a letter or number"
            ),
            RegexValidator(
                r'^xn--',
                "Bucket name cannot begin with 'xn--'",
                inverse_match=True,
            ),
            RegexValidator(
                r'-s3alias$',
                "Bucket name cannot end with '-s3alias'",
                inverse_match=True,
            ),
            RegexValidator(
                r'\.\.',
                "Bucket name cannot contain two or more consecutive periods",
                inverse_match=True,
            ),
            NegateValidator(
                validate_ipv4_address,
                "Bucket name cannot be an ip address"
            ),
        ],
    )

    # Ticket Jira ID
    jira_id = models.CharField(
        max_length=100,
        verbose_name="Associated Jira Ticket ID",
        help_text="Associated Jira Ticket ID",
        blank=True,
        default="",
    )

    # django-simple-history
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse("tracker:ticket-update", kwargs={"pk": self.pk})

    def get_fields(self):
        return [
            (field.verbose_name, field.value_from_object(self))
            for field in self.__class__._meta.fields
        ]

    def default_data_bucket_name(self):
        return (
            'nhlbi-bdc-{ticket.study_id}-{ticket.consent_code}'
            .format(ticket=self)
        )

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


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_data):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        now = timezone.now()
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_data
        )
        user.set_password(password)
        user.save(using=self._db)
        logger.info("Created user " + email)
        return user

    def create_user(self, email, password, **extra_data):
        return self._create_user(email, password, False, False, **extra_data)

    def create_superuser(self, email, password, **extra_data):
        user = self._create_user(email, password, True, True, **extra_data)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="Email", unique=True)
    name = models.CharField(max_length=100, verbose_name="Name")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "users/%i" % self.pk
        
    def get_short_name(self):
        return self.name
        

@receiver(user_logged_in)
def login_logger(request, user, **kwargs):
    logger.info("User {} logged in with {}".format(user.email, request))
@receiver(user_logged_out)
def login_logger(request, user, **kwargs):
    logger.info("User {} logged out.".format(user.email))


