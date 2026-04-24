from django.db import migrations
from django.utils import timezone


def migrate_meeting_statuses(apps, schema_editor):
    Meeting = apps.get_model('app1', 'Meeting')
    now = timezone.now()

    for meeting in Meeting.objects.all():
        if meeting.status == 'approved':
            if now >= meeting.end_time:
                meeting.status = 'done'
            elif now >= meeting.start_time:
                meeting.status = 'in_progress'
            else:
                meeting.status = 'approved_pending'
        elif meeting.status == 'cancelled':
            meeting.status = 'expired_cancelled'
        elif meeting.status == 'pending' and now >= meeting.start_time:
            meeting.status = 'expired_cancelled'
        meeting.save(update_fields=['status'])


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0008_alter_meeting_status'),
    ]

    operations = [
        migrations.RunPython(migrate_meeting_statuses, migrations.RunPython.noop),
    ]
