from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from datetime import timedelta

from .models import Meeting, MeetingAttendee, Notification, ReminderSetting


@ensure_csrf_cookie
def spa_shell(request, *args, **kwargs):
    return render(request, 'spa.html')


def send_meeting_reminders(request):
    if request.method == 'POST':
        meeting_id = request.POST.get('meeting_id')
        meeting = get_object_or_404(Meeting, pk=meeting_id)

        attendees = MeetingAttendee.objects.filter(
            meeting=meeting,
            response=MeetingAttendee.RESPONSE_ACCEPTED
        ).select_related('person__user')

        sent_count = 0
        for attendee in attendees:
            if hasattr(attendee.person, 'user'):
                Notification.objects.create(
                    recipient=attendee.person.user,
                    notification_type=Notification.TYPE_MEETING_REMINDER,
                    title=f'会议提醒：{meeting.title}',
                    content=f'您有一个即将开始的会议：{meeting.title}\n时间：{meeting.start_time}\n地点：{meeting.location}',
                    meeting=meeting
                )
                sent_count += 1

        messages.success(request, f'已向 {sent_count} 名参会人员发送会议提醒')
        return redirect('meetings')

    return redirect('meetings')


def send_meeting_invitations(meeting, attendees):
    notifications_sent = 0
    for person in attendees:
        try:
            if person.user:
                Notification.objects.create(
                    recipient=person.user,
                    notification_type=Notification.TYPE_MEETING_INVITATION,
                    title=f'会议邀请：{meeting.title}',
                    content=f'您被邀请参加以下会议：\n\n会议主题：{meeting.title}\n时间：{meeting.start_time} - {meeting.end_time}\n地点：{meeting.location}\n发起人：{meeting.organizer.name if meeting.organizer else "未指定"}\n\n请登录系统回复是否参加。',
                    meeting=meeting
                )
                notifications_sent += 1
        except Exception as e:
            print(f"Error creating notification for person {person.id} ({person.name}): {e}")
            continue

    return notifications_sent


def check_and_send_reminders():
    now = timezone.now()

    upcoming_meetings = Meeting.objects.filter(
        status=Meeting.STATUS_APPROVED_PENDING,
        start_time__gt=now,
        start_time__lte=now + timedelta(hours=2)
    )

    for meeting in upcoming_meetings:
        attendees = MeetingAttendee.objects.filter(
            meeting=meeting,
            response=MeetingAttendee.RESPONSE_ACCEPTED
        ).select_related('person__user')

        for attendee in attendees:
            if hasattr(attendee.person, 'user'):
                existing_reminder = Notification.objects.filter(
                    recipient=attendee.person.user,
                    meeting=meeting,
                    notification_type=Notification.TYPE_MEETING_REMINDER,
                    created_at__gte=now - timedelta(hours=1)
                ).exists()

                if not existing_reminder:
                    Notification.objects.create(
                        recipient=attendee.person.user,
                        notification_type=Notification.TYPE_MEETING_REMINDER,
                        title=f'会议即将开始：{meeting.title}',
                        content=f'提醒：您有一个会议即将开始\n\n会议主题：{meeting.title}\n开始时间：{meeting.start_time}\n地点：{meeting.location}',
                        meeting=meeting,
                        sent_time=now
                    )


def create_user_reminder_settings(user):
    ReminderSetting.objects.get_or_create(
        user=user,
        defaults={
            'reminder_methods': [ReminderSetting.REMINDER_EMAIL, ReminderSetting.REMINDER_IN_APP],
            'default_reminder_minutes': [15, 60],
            'email_notifications': True,
            'in_app_notifications': True,
            'sms_notifications': False,
        }
    )


def logout_view(request):
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('login')
