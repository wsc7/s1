from datetime import datetime

from django.db import migrations
from django.utils import timezone


def seed(apps, schema_editor):
    Person = apps.get_model('app1', 'Person')
    Meeting = apps.get_model('app1', 'Meeting')
    tz = timezone.get_current_timezone()

    p1 = Person.objects.create(
        name='张三',
        employee_no='0001',
        department='办公室',
        position='主任',
        role='系统管理员',
        phone='13800000001',
    )
    p2 = Person.objects.create(
        name='李四',
        employee_no='0002',
        department='信息中心',
        position='工程师',
        role='会议管理员',
        phone='13800000002',
    )
    p3 = Person.objects.create(
        name='王五',
        employee_no='0003',
        department='人事处',
        position='科员',
        role='普通用户',
        phone='13800000003',
    )

    Meeting.objects.create(
        title='2026 年度工作计划部署会议',
        organizer=p1,
        start_time=timezone.make_aware(datetime(2026, 3, 20, 9, 0), tz),
        end_time=timezone.make_aware(datetime(2026, 3, 20, 11, 0), tz),
        location='第一会议室',
        attendee_count=25,
        status='pending',
    )
    Meeting.objects.create(
        title='部门月度例会',
        organizer=p2,
        start_time=timezone.make_aware(datetime(2026, 3, 10, 14, 30), tz),
        end_time=timezone.make_aware(datetime(2026, 3, 10, 16, 0), tz),
        location='线上会议',
        attendee_count=12,
        status='done',
    )
    Meeting.objects.create(
        title='项目启动评审会',
        organizer=p3,
        start_time=timezone.make_aware(datetime(2026, 3, 25, 15, 0), tz),
        end_time=timezone.make_aware(datetime(2026, 3, 25, 17, 0), tz),
        location='第二会议室',
        attendee_count=18,
        status='approved',
    )


def unseed(apps, schema_editor):
    Person = apps.get_model('app1', 'Person')
    Meeting = apps.get_model('app1', 'Meeting')
    Meeting.objects.all().delete()
    Person.objects.filter(employee_no__in=['0001', '0002', '0003']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
