# Generated by Django 3.2.9 on 2021-11-16 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="bucket_created_dt",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Bucket Created Date"
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="data_accepted_dt",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Gen3 Accepted Date"
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="data_uploaded_completed_dt",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Data Uploaded Completed Date"
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="data_uploaded_started_dt",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Data Uploaded Started Date"
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="ticket_approved_dt",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Intake Form Approved Date"
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="ticket_rejected_dt",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Intake Form Rejected Date"
            ),
        ),
        migrations.AlterField(
            model_name="ticket",
            name="dataset_description",
            field=models.CharField(
                blank=True,
                help_text="Describe the dataset you are uploading",
                max_length=2500,
                verbose_name="Dataset Description",
            ),
        ),
    ]
