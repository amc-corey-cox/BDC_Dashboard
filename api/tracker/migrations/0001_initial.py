# Generated by Django 3.2.9 on 2021-11-16 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ticket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, verbose_name="Email")),
                (
                    "name",
                    models.CharField(
                        help_text="Name of primary contact",
                        max_length=100,
                        verbose_name="Name",
                    ),
                ),
                (
                    "organization",
                    models.CharField(
                        help_text="Name of requesting organization",
                        max_length=250,
                        verbose_name="Organization",
                    ),
                ),
                (
                    "study_name",
                    models.CharField(
                        blank=True,
                        help_text="Name of Study or Dataset (if applicable)",
                        max_length=250,
                        verbose_name="Study Name",
                    ),
                ),
                (
                    "dataset_description",
                    models.CharField(
                        blank=True,
                        help_text="Describe the dataset you are uploading",
                        max_length=1000,
                        verbose_name="Dataset Description",
                    ),
                ),
                (
                    "is_test_data",
                    models.BooleanField(
                        blank=True,
                        help_text="Check this box if this is test data: ",
                        verbose_name="Is Test Data",
                    ),
                ),
                (
                    "google_email",
                    models.EmailField(
                        blank=True,
                        help_text="If you're uploading to Google please provide your google email for access",
                        max_length=254,
                        verbose_name="Google Email",
                    ),
                ),
                (
                    "aws_iam",
                    models.CharField(
                        blank=True,
                        help_text="If you're uploading to Amazon please provide your AWS IAM",
                        max_length=100,
                        verbose_name="AWS IAM",
                    ),
                ),
                (
                    "data_size",
                    models.CharField(
                        blank=True,
                        help_text="Please provide an estimated size of your data set(s)",
                        max_length=100,
                        verbose_name="Data Size",
                    ),
                ),
                ("study_id", models.CharField(max_length=100, verbose_name="Study ID")),
                (
                    "consent_code",
                    models.CharField(max_length=100, verbose_name="Consent Code"),
                ),
                (
                    "created_dt",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created Date"
                    ),
                ),
            ],
        ),
    ]
