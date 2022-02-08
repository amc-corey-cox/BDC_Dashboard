# Generated by Django 4.0.2 on 2022-02-03 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_remove_ticket_last_updated_dt_ticket_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='bucket_created_by',
            field=models.EmailField(default='', max_length=254, verbose_name='Bucket created by'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='data_accepted_by',
            field=models.EmailField(default='', max_length=254, verbose_name='Data accepted by'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='data_upload_completed_by',
            field=models.EmailField(default='', max_length=254, verbose_name='Data upload completed by'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='data_upload_started_by',
            field=models.EmailField(default='', max_length=254, verbose_name='Data upload started by'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='ticket_approved_by',
            field=models.EmailField(default='', max_length=254, verbose_name='Ticket approved by'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='ticket_rejected_by',
            field=models.EmailField(default='', max_length=254, verbose_name='Ticket rejected by'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]