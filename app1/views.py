import json
import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

from .forms import MeetingForm, PersonForm, MeetingAttendeesForm, MeetingAttachmentForm, NotificationForm, ReminderSettingForm, PersonProfileForm, UserProfileForm, CustomPasswordChangeForm, DepartmentForm, MeetingAgendaItemForm
from .models import Meeting, Person, MeetingAttendee, MeetingAttachment, Notification, ReminderSetting, Department, MeetingAgendaItem, MeetingAgendaItemAssignee


INVALID_JSON_RESPONSE = {'ok': False, 'errors': {'_': ['无效的 JSON']}}
METHOD_NOT_ALLOWED_RESPONSE = {'ok': False, 'errors': {'_': ['不支持的请求方法']}}


def _render_home(request):
    return render(
        request,
        'meeting-system-index.html',
        {
            'person_count': Person.objects.count(),
            'meeting_count': Meeting.objects.count(),
        },
    )


def _parse_json_request(request):
    try:
        return json.loads(request.body.decode('utf-8')), None
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse(INVALID_JSON_RESPONSE, status=400)


def _method_not_allowed_json_response():
    return JsonResponse(METHOD_NOT_ALLOWED_RESPONSE, status=405)


def _save_form_json_response(form):
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


def _recalculate_attendee_count(meeting):
    meeting.attendee_count = meeting.attendees.count()
    meeting.save(update_fields=['attendee_count'])


def _handle_post_delete(request, obj, *, success_message, redirect_name, redirect_kwargs=None, invalid_method_message):
    if request.method != 'POST':
        messages.error(request, invalid_method_message)
        return redirect(redirect_name, **(redirect_kwargs or {}))
    obj.delete()
    messages.success(request, success_message)
    return redirect(redirect_name, **(redirect_kwargs or {}))


def _create_meeting_approval_notification(meeting, *, approved, opinion):
    organizer = meeting.organizer
    if not organizer or not organizer.user:
        return

    result_text = '已通过' if approved else '未通过'
    opinion_text = opinion.strip() if opinion and opinion.strip() else '无审批意见'
    Notification.objects.create(
        recipient=organizer.user,
        notification_type=Notification.TYPE_MEETING_UPDATE,
        title=f'会议审批结果：{result_text}',
        content=(
            f'会议主题：{meeting.title}\n'
            f'审批结果：{result_text}\n'
            f'审批意见：{opinion_text}'
        ),
        meeting=meeting,
    )


@login_required
def home(request):
    return _render_home(request)


@login_required
def meetings(request):
    Meeting.refresh_all_statuses()
    all_meetings = Meeting.objects.select_related('organizer').all()
    visible_meetings = all_meetings.exclude(status=Meeting.STATUS_DRAFT)
    qs = visible_meetings
    q = request.GET.get('q', '').strip()
    date_str = request.GET.get('date', '').strip()
    status = request.GET.get('status', '').strip()
    view_type = request.GET.get('view', 'all').strip()

    all_stats_source = visible_meetings
    mine_stats_source = Meeting.objects.none()

    try:
        current_person = request.user.person_profile
        mine_stats_source = all_meetings.filter(organizer=current_person)
    except Person.DoesNotExist:
        current_person = None

    if view_type == 'mine':
        qs = mine_stats_source

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(organizer__name__icontains=q))
    if date_str:
        d = parse_date(date_str)
        if d:
            qs = qs.filter(start_time__date=d)
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    meeting_list = paginator.get_page(page_number)
    organizers = [
        {'id': p.id, 'name': p.name}
        for p in Person.objects.order_by('name')
    ]
    if view_type == 'mine':
        meeting_stats = {
            'mine_total': mine_stats_source.count(),
            'mine_applied': mine_stats_source.exclude(status=Meeting.STATUS_DRAFT).count(),
            'mine_draft': mine_stats_source.filter(status=Meeting.STATUS_DRAFT).count(),
            'applied_pending': mine_stats_source.filter(status=Meeting.STATUS_PENDING).count(),
            'applied_unapproved': mine_stats_source.filter(status=Meeting.STATUS_REJECTED).count(),
            'applied_approved': mine_stats_source.filter(status__in=[Meeting.STATUS_APPROVED_PENDING, Meeting.STATUS_IN_PROGRESS, Meeting.STATUS_DONE]).count(),
            'applied_expired': mine_stats_source.filter(status=Meeting.STATUS_EXPIRED_CANCELLED).count(),
        }
    else:
        meeting_stats = {
            'total': all_stats_source.count(),
            'pending': all_stats_source.filter(status=Meeting.STATUS_PENDING).count(),
            'unapproved': all_stats_source.filter(status=Meeting.STATUS_REJECTED).count(),
            'approved': all_stats_source.filter(status__in=[Meeting.STATUS_APPROVED_PENDING, Meeting.STATUS_IN_PROGRESS, Meeting.STATUS_DONE]).count(),
            'expired': all_stats_source.filter(status=Meeting.STATUS_EXPIRED_CANCELLED).count(),
            'approved_pending': all_stats_source.filter(status=Meeting.STATUS_APPROVED_PENDING).count(),
            'in_progress': all_stats_source.filter(status=Meeting.STATUS_IN_PROGRESS).count(),
            'done': all_stats_source.filter(status=Meeting.STATUS_DONE).count(),
        }
    return render(
        request,
        'meeting-system-meetings.html',
        {
            'meeting_list': meeting_list,
            'organizers_json': json.dumps(organizers, ensure_ascii=False),
            'view_type': view_type,
            'current_person': current_person,
            'meeting_stats': meeting_stats,
        },
    )


@login_required
def people(request):
    qs = Person.objects.select_related('department').all()
    q = request.GET.get('q', '').strip()
    department = request.GET.get('department', '').strip()
    role = request.GET.get('role', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(employee_no__icontains=q))
    if department:
        qs = qs.filter(department__name__icontains=department)
    if role:
        qs = qs.filter(role__icontains=role)

    people_stats_source = qs
    people_stats = {
        'total': people_stats_source.count(),
    }
    people_department_stats = list(
        people_stats_source.exclude(department__isnull=True)
        .values('department__name')
        .annotate(count=Count('id'))
        .order_by('-count', 'department__name')
    )
    people_unassigned_count = people_stats_source.filter(department__isnull=True).count()

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    person_list = paginator.get_page(page_number)
    department_choices = Department.objects.all().order_by('name')
    role_choices = (
        Person.objects.exclude(role='')
        .values_list('role', flat=True)
        .distinct()
        .order_by('role')
    )
    return render(
        request,
        'meeting-system-people.html',
        {
            'person_list': person_list,
            'department_choices': department_choices,
            'role_choices': role_choices,
            'people_stats': people_stats,
            'people_department_stats': people_department_stats,
            'people_unassigned_count': people_unassigned_count,
        },
    )


@login_required
def person_create(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '人员已添加。')
            return redirect('people')
    else:
        form = PersonForm()
    return render(request, 'person_create.html', {'form': form})


@login_required
def meeting_create(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '会议已创建。')
            return redirect('meetings')
    else:
        form = MeetingForm()
    return render(request, 'meeting_create.html', {'form': form})


@login_required
def person_edit(request, pk):
    person = get_object_or_404(Person, pk=pk)
    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, '人员信息已保存。')
            return redirect('people')
    else:
        form = PersonForm(instance=person)
    return render(
        request,
        'person_edit.html',
        {'form': form, 'person': person},
    )


def _build_meeting_attendees_context(meeting, attendees_form, request):
    all_attendees = meeting.attendees.select_related('person').all()
    paginator = Paginator(all_attendees, 10)
    page_number = request.GET.get('page')
    current_attendees_page = paginator.get_page(page_number)
    attendee_options = [
        {
            'id': person.id,
            'name': person.name,
            'department': person.department.name if person.department else '',
            'employee_no': person.employee_no or '',
            'search_text': ' '.join(filter(None, [person.name, person.department.name if person.department else '', person.employee_no or ''])).lower(),
        }
        for person in attendees_form.fields['attendees'].queryset.select_related('department')
    ]
    return {
        'meeting': meeting,
        'attendees_form': attendees_form,
        'attendee_options_json': json.dumps(attendee_options, ensure_ascii=False),
        'attendee_submit_url': request.path,
        'current_attendees': current_attendees_page,
        'paginator': paginator,
        'page_obj': current_attendees_page,
    }


@login_required
def meeting_detail(request, pk):
    return redirect('meeting_info', pk=pk)


@login_required
def meeting_info(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    meeting.refresh_status()
    meeting_form = MeetingForm(instance=meeting)

    if request.method == 'POST':
        meeting_form = MeetingForm(request.POST, instance=meeting)
        if meeting_form.is_valid():
            meeting_form.save()
            messages.success(request, '会议信息已保存。')
            return redirect('meeting_info', pk=meeting.id)

    return render(
        request,
        'meeting_edit.html',
        {
            'meeting': meeting,
            'meeting_form': meeting_form,
        },
    )


@login_required
def meeting_edit(request, pk):
    return redirect('meeting_detail', pk=pk)


@login_required
def meeting_attachments(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    meeting.refresh_status()
    attachment_form = MeetingAttachmentForm()

    if request.method == 'POST':
        attachment_form = MeetingAttachmentForm(request.POST, request.FILES)
        if attachment_form.is_valid():
            attachment = attachment_form.save(commit=False)
            attachment.meeting = meeting
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(request, '附件已上传。')
            return redirect('meeting_attachments', pk=meeting.id)

    attachments = meeting.attachments.select_related('uploaded_by').all()
    return render(
        request,
        'meeting_attachments.html',
        {
            'meeting': meeting,
            'attachment_form': attachment_form,
            'attachments': attachments,
        },
    )


@login_required
def meeting_agenda(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    meeting.refresh_status()
    agenda_form = MeetingAgendaItemForm(meeting=meeting)

    if request.method == 'POST' and request.POST.get('action') == 'toggle_completion':
        assignment = get_object_or_404(
            MeetingAgendaItemAssignee.objects.select_related('agenda_item__meeting'),
            pk=request.POST.get('assignment_id'),
            agenda_item__meeting=meeting,
        )
        assignment.is_completed = request.POST.get('is_completed') == '1'
        assignment.save(update_fields=['is_completed'])
        return redirect('meeting_agenda', pk=meeting.id)

    if request.method == 'POST':
        agenda_form = MeetingAgendaItemForm(request.POST, meeting=meeting)
        if agenda_form.is_valid():
            agenda_item = agenda_form.save(commit=False)
            agenda_item.meeting = meeting
            agenda_item.save()

            assignees = agenda_form.cleaned_data['assignees']
            MeetingAgendaItemAssignee.objects.bulk_create([
                MeetingAgendaItemAssignee(
                    agenda_item=agenda_item,
                    person=person,
                    is_completed=False,
                )
                for person in assignees
            ])
            messages.success(request, '会议事项已添加。')
            return redirect('meeting_agenda', pk=meeting.id)

    agenda_items = list(
        meeting.agenda_items.prefetch_related('assignees__person').all()
    )

    return render(
        request,
        'meeting_agenda.html',
        {
            'meeting': meeting,
            'agenda_form': agenda_form,
            'agenda_items': agenda_items,
        },
    )


@login_required
def meeting_attendees(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    meeting.refresh_status()
    attendees_form = MeetingAttendeesForm(meeting=meeting)
    action = request.POST.get('action', '')

    if request.method == 'POST' and action in ['mark_required', 'mark_optional', 'batch_remove']:
        attendee_ids_str = request.POST.get('attendee_ids', '')
        if not attendee_ids_str:
            messages.error(request, '未选择参与人')
            return redirect('meeting_attendees', meeting_id=meeting.id)

        try:
            attendee_ids = [int(id) for id in attendee_ids_str.split(',') if id.strip()]
        except ValueError:
            messages.error(request, '无效的参与人ID')
            return redirect('meeting_attendees', meeting_id=meeting.id)

        attendees = MeetingAttendee.objects.filter(id__in=attendee_ids, meeting=meeting)

        if not attendees.exists():
            messages.error(request, '未找到指定的参与人')
            return redirect('meeting_attendees', meeting_id=meeting.id)

        if action == 'mark_required':
            updated_count = attendees.update(is_required=True)
            messages.success(request, f'已将 {updated_count} 名参与人设为必须参加')
        elif action == 'mark_optional':
            updated_count = attendees.update(is_required=False)
            messages.success(request, f'已将 {updated_count} 名参与人设为可选')
        elif action == 'batch_remove':
            removed_count = attendees.count()
            attendees.delete()
            _recalculate_attendee_count(meeting)
            messages.success(request, f'已批量移除 {removed_count} 名参与人')

        return redirect('meeting_attendees', meeting_id=meeting.id)

    if request.method == 'POST':
        attendees_form = MeetingAttendeesForm(request.POST, meeting=meeting)
        if attendees_form.is_valid():
            attendees = attendees_form.cleaned_data['attendees']
            is_required = attendees_form.cleaned_data['is_required']

            added_count = 0
            added_people = []
            for person in attendees:
                if not MeetingAttendee.objects.filter(meeting=meeting, person=person).exists():
                    MeetingAttendee.objects.create(
                        meeting=meeting,
                        person=person,
                        is_required=is_required,
                        added_by=request.user
                    )
                    added_count += 1
                    added_people.append(person)

            if added_count > 0:
                notifications_sent = send_meeting_invitations(meeting, added_people)
                _recalculate_attendee_count(meeting)

                if notifications_sent == added_count:
                    messages.success(request, f'成功添加 {added_count} 名参与人，并已发送会议邀请')
                elif notifications_sent > 0:
                    messages.success(request, f'成功添加 {added_count} 名参与人，其中 {notifications_sent} 人已发送会议邀请（{added_count - notifications_sent} 人无用户账户）')
                else:
                    messages.success(request, f'成功添加 {added_count} 名参与人（无用户账户，未发送应用内通知）')
            else:
                messages.info(request, '没有新增参与人')

            return redirect('meeting_attendees', meeting_id=meeting.id)

    return render(
        request,
        'meeting_attendees.html',
        _build_meeting_attendees_context(meeting, attendees_form, request),
    )


@login_required
def person_delete(request, pk):
    person = get_object_or_404(Person, pk=pk)
    return _handle_post_delete(
        request,
        person,
        success_message=f'已删除人员：{person.name}',
        redirect_name='people',
        invalid_method_message='请通过页面上的删除按钮操作。',
    )


@login_required
def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return _handle_post_delete(
        request,
        meeting,
        success_message=f'已删除会议：{meeting.title}',
        redirect_name='meetings',
        invalid_method_message='请通过页面上的删除按钮操作。',
    )


@login_required
def meeting_apply(request, pk):
    """将草稿/未通过会议提交申请（状态改为待审批）"""
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method != 'POST':
        messages.error(request, '请通过页面上的申请按钮操作。')
        return redirect('meetings', )
    if meeting.status not in (Meeting.STATUS_DRAFT, Meeting.STATUS_REJECTED):
        messages.error(request, '该会议当前状态不可提交申请。')
        return redirect('meetings')
    meeting.status = Meeting.STATUS_PENDING
    meeting.save(update_fields=['status', 'updated_at'])

    # 通知所有管理员（is_staff=True）有新会议待审批
    organizer_name = meeting.organizer.name if meeting.organizer else '未知'
    start_time_str = meeting.start_time.strftime('%Y-%m-%d %H:%M') if meeting.start_time else '未设置'
    admin_users = User.objects.filter(is_staff=True)
    Notification.objects.bulk_create([
        Notification(
            recipient=admin,
            notification_type=Notification.TYPE_MEETING_UPDATE,
            title=f'新会议待审批：{meeting.title}',
            content=(
                f'会议主题：{meeting.title}\n'
                f'发起人：{organizer_name}\n'
                f'开始时间：{start_time_str}\n'
                f'请登录系统进行审批。'
            ),
            meeting=meeting,
        )
        for admin in admin_users
    ])

    messages.success(request, f'会议「{meeting.title}」已提交申请，等待审批。')
    return redirect(f'{request.META.get("HTTP_REFERER", "/meetings/")}' if 'view=mine' in request.META.get('HTTP_REFERER', '') else '/meetings/?view=mine')


@login_required
def meeting_agenda_item_delete(request, meeting_id, item_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    agenda_item = get_object_or_404(MeetingAgendaItem, pk=item_id, meeting=meeting)
    return _handle_post_delete(
        request,
        agenda_item,
        success_message=f'已删除事项：{agenda_item.title}',
        redirect_name='meeting_agenda',
        redirect_kwargs={'pk': meeting.id},
        invalid_method_message='请通过页面上的删除按钮操作。',
    )


def api_meeting_agenda_item_detail(request, meeting_id, item_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    agenda_item = get_object_or_404(
        MeetingAgendaItem.objects.prefetch_related('assignees__person'),
        pk=item_id,
        meeting=meeting,
    )
    return JsonResponse({
        'id': agenda_item.id,
        'title': agenda_item.title,
        'start_time': agenda_item.start_time.strftime('%Y-%m-%dT%H:%M'),
        'end_time': agenda_item.end_time.strftime('%Y-%m-%dT%H:%M'),
        'status': agenda_item.status,
        'assignee_ids': list(agenda_item.assignees.values_list('person_id', flat=True)),
        'assignee_options': [
            {
                'id': attendee.person.id,
                'name': attendee.person.name,
                'department': attendee.person.department.name if attendee.person.department else '',
            }
            for attendee in meeting.attendees.select_related('person__department').all()
        ],
    })


def api_meeting_agenda_item_update(request, meeting_id, item_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    agenda_item = get_object_or_404(MeetingAgendaItem, pk=item_id, meeting=meeting)

    if request.method not in ['PUT', 'PATCH', 'POST']:
        return _method_not_allowed_json_response()

    data, error_response = _parse_json_request(request)
    if error_response:
        return error_response

    form = MeetingAgendaItemForm(data, instance=agenda_item, meeting=meeting)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    agenda_item = form.save()
    assignees = form.cleaned_data['assignees']
    assignee_map = {
        assignment.person_id: assignment
        for assignment in agenda_item.assignees.all()
    }
    selected_ids = {person.id for person in assignees}

    agenda_item.assignees.exclude(person_id__in=selected_ids).delete()

    for person in assignees:
        if person.id not in assignee_map:
            MeetingAgendaItemAssignee.objects.create(
                agenda_item=agenda_item,
                person=person,
                is_completed=False,
            )

    return JsonResponse({'ok': True})


@require_POST
def api_person_create(request):
    data, error_response = _parse_json_request(request)
    if error_response:
        return error_response
    return _save_form_json_response(PersonForm(data))


@require_POST
def api_meeting_create(request):
    data, error_response = _parse_json_request(request)
    if error_response:
        return error_response
    if isinstance(data, dict) and data.get('organizer') in ('', None):
        data = {**data, 'organizer': ''}
    return _save_form_json_response(MeetingForm(data))


@login_required
def api_meeting_approve(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method != 'POST':
        return _method_not_allowed_json_response()

    data, error_response = _parse_json_request(request)
    if error_response:
        return error_response

    if not isinstance(data, dict):
        return JsonResponse(INVALID_JSON_RESPONSE, status=400)

    meeting.refresh_status()
    if meeting.status != Meeting.STATUS_PENDING:
        return JsonResponse({'ok': False, 'errors': {'_': ['该会议当前状态不可审批']}}, status=400)

    action = (data.get('action') or '').strip()
    opinion = (data.get('opinion') or '').strip()
    if action not in ['approve', 'reject']:
        return JsonResponse({'ok': False, 'errors': {'action': ['无效的审批操作']}}, status=400)

    approved = action == 'approve'
    meeting.status = Meeting.STATUS_APPROVED_PENDING if approved else Meeting.STATUS_REJECTED
    meeting.save(update_fields=['status', 'updated_at'])
    _create_meeting_approval_notification(meeting, approved=approved, opinion=opinion)
    return JsonResponse({'ok': True})


def api_person_detail(request, pk):
    """Get person details for editing"""
    person = get_object_or_404(Person, pk=pk)
    return JsonResponse({
        'id': person.id,
        'name': person.name,
        'employee_no': person.employee_no,
        'department_id': person.department.id if person.department else None,
        'department_name': person.department.name if person.department else '',
        'position': person.position,
        'role': person.role,
        'phone': person.phone,
    })


def api_department_list(request):
    """Get list of departments for dropdown"""
    departments = Department.objects.all().order_by('name')
    department_list = [
        {'id': dept.id, 'name': dept.name}
        for dept in departments
    ]
    return JsonResponse({'departments': department_list})


def api_person_update(request, pk):
    """Update person details - supports both PUT and POST with ID"""
    person = get_object_or_404(Person, pk=pk)

    if request.method not in ['PUT', 'PATCH', 'POST']:
        return _method_not_allowed_json_response()

    data, error_response = _parse_json_request(request)
    if error_response:
        return error_response

    return _save_form_json_response(PersonForm(data, instance=person))


def api_check_auth(request):
    """Check if user is authenticated"""
    if request.user.is_authenticated:
        return JsonResponse({
            'is_authenticated': True,
            'username': request.user.username
        })
    else:
        return JsonResponse({
            'is_authenticated': False,
            'username': None
        })


@login_required
def remove_attendee(request, meeting_id, attendee_id):
    """移除会议参与人"""
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    attendee = get_object_or_404(MeetingAttendee, pk=attendee_id, meeting=meeting)

    if request.method == 'POST':
        person_name = attendee.person.name
        attendee.delete()
        _recalculate_attendee_count(meeting)
        messages.success(request, f'已从会议中移除 {person_name}')
        return redirect('meeting_attendees', meeting_id=meeting.id)

    return render(request, 'remove_attendee.html', {
        'meeting': meeting,
        'attendee': attendee,
    })


@login_required
def remove_attachment(request, meeting_id, attachment_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    attachment = get_object_or_404(MeetingAttachment, pk=attachment_id, meeting=meeting)
    return _handle_post_delete(
        request,
        attachment,
        success_message=f'已删除附件：{attachment.filename}',
        redirect_name='meeting_attachments',
        redirect_kwargs={'pk': meeting.id},
        invalid_method_message='请通过页面上的删除按钮操作。',
    )


@login_required
def respond_to_meeting(request, meeting_id):
    """参与人回复会议邀请"""
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    attendee = get_object_or_404(MeetingAttendee, meeting=meeting, person__user=request.user)

    if request.method == 'POST':
        response = request.POST.get('response')
        if response in dict(MeetingAttendee.RESPONSE_CHOICES):
            attendee.response = response
            attendee.response_time = timezone.now()
            attendee.save()

            response_text = dict(MeetingAttendee.RESPONSE_CHOICES)[response]
            messages.success(request, f'您的回复已记录：{response_text}')
        else:
            messages.error(request, '无效的回复')

        return redirect('notifications')

    return render(request, 'respond_to_meeting.html', {
        'meeting': meeting,
        'attendee': attendee,
    })


@login_required
def notifications(request):
    """用户通知中心"""
    user_notifications = request.user.notifications.all()

    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        action = request.POST.get('action')

        if notification_id and action:
            notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)

            if action == 'mark_read':
                notification.status = Notification.STATUS_READ
                notification.save()
                messages.success(request, '通知已标记为已读')
            elif action == 'dismiss':
                notification.status = Notification.STATUS_DISMISSED
                notification.save()
                messages.success(request, '通知已忽略')

        return redirect('notifications')

    # 统计未读通知数量
    unread_count = user_notifications.filter(status=Notification.STATUS_UNREAD).count()

    return render(request, 'notifications.html', {
        'notifications': user_notifications,
        'unread_count': unread_count,
    })


@login_required
def reminder_settings(request):
    """用户提醒设置"""
    try:
        settings = request.user.reminder_settings
    except ReminderSetting.DoesNotExist:
        settings = ReminderSetting.objects.create(user=request.user)

    if request.method == 'POST':
        form = ReminderSettingForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, '提醒设置已保存')
            return redirect('reminder_settings')
    else:
        form = ReminderSettingForm(instance=settings)

    return render(request, 'reminder_settings.html', {
        'form': form,
        'settings': settings,
    })


@login_required
def send_meeting_reminders(request):
    """手动发送会议提醒"""
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
                # 创建提醒通知
                notification = Notification.objects.create(
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


# ===== 辅助函数 =====

def send_meeting_invitations(meeting, attendees):
    """发送会议邀请通知
    返回成功发送的通知数量
    """
    notifications_sent = 0
    for person in attendees:
        try:
            # 检查人员是否关联了用户账户
            if person.user:
                # 创建会议邀请通知
                Notification.objects.create(
                    recipient=person.user,
                    notification_type=Notification.TYPE_MEETING_INVITATION,
                    title=f'会议邀请：{meeting.title}',
                    content=f'您被邀请参加以下会议：\n\n会议主题：{meeting.title}\n时间：{meeting.start_time} - {meeting.end_time}\n地点：{meeting.location}\n发起人：{meeting.organizer.name if meeting.organizer else "未指定"}\n\n请登录系统回复是否参加。',
                    meeting=meeting
                )
                notifications_sent += 1
        except Exception as e:
            # 记录错误但继续处理其他人员
            print(f"Error creating notification for person {person.id} ({person.name}): {e}")
            continue

    return notifications_sent


def check_and_send_reminders():
    """检查并发送会议提醒（可设置为定时任务）"""
    now = timezone.now()

    # 查找需要发送提醒的会议
    upcoming_meetings = Meeting.objects.filter(
        status=Meeting.STATUS_APPROVED_PENDING,
        start_time__gt=now,
        start_time__lte=now + timedelta(hours=2)  # 2小时内开始的会议
    )

    for meeting in upcoming_meetings:
        attendees = MeetingAttendee.objects.filter(
            meeting=meeting,
            response=MeetingAttendee.RESPONSE_ACCEPTED
        ).select_related('person__user')

        for attendee in attendees:
            if hasattr(attendee.person, 'user'):
                # 检查是否已经发送过提醒
                existing_reminder = Notification.objects.filter(
                    recipient=attendee.person.user,
                    meeting=meeting,
                    notification_type=Notification.TYPE_MEETING_REMINDER,
                    created_at__gte=now - timedelta(hours=1)  # 1小时内已发送过
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
    """为用户创建默认提醒设置"""
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


def login_view(request):
    """Login view"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # Debug: Print POST data
        print(f"Login POST data: {dict(request.POST)}")

        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, '请输入用户名和密码')
        else:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'欢迎回来，{user.username}！')
                return redirect('home')
            else:
                messages.error(request, '用户名或密码错误')

    return render(request, 'login.html')


def register_view(request):
    """注册视图"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        name = request.POST.get('name', '').strip()
        employee_no = request.POST.get('employee_no', '').strip()
        department = request.POST.get('department', '').strip()

        # 验证必填字段
        if not username or not password1 or not password2 or not name:
            messages.error(request, '请填写所有必填字段')
        elif len(username) < 3:
            messages.error(request, '用户名至少需要3个字符')
        elif not re.match(r'^[\w.@+-]+$', username):
            messages.error(request, '用户名只能包含字母、数字和@/./+/-/_符号')
        elif len(password1) < 8:
            messages.error(request, '密码至少需要8个字符')
        elif password1 != password2:
            messages.error(request, '两次输入的密码不一致')
        elif User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
        else:
            # 创建用户
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email if email else '',
                    password=password1
                )

                # 创建人员记录
                # 处理部门：如果提供了部门名称，查找对应的Department对象
                dept_obj = None
                if department:
                    try:
                        dept_obj = Department.objects.get(name=department)
                    except Department.DoesNotExist:
                        # 部门不存在，可以设置为空或创建（根据需求）
                        # 这里设置为空，因为只有管理员可以创建部门
                        pass

                person = Person.objects.create(
                    name=name,
                    employee_no=employee_no,
                    department=dept_obj,
                    user=user
                )

                # 创建提醒设置
                create_user_reminder_settings(user)

                # 自动登录用户
                login(request, user)
                messages.success(request, f'注册成功！欢迎 {name}')
                return redirect('home')

            except Exception as e:
                messages.error(request, f'注册失败：{str(e)}')
                # 如果用户创建成功但人员创建失败，删除用户
                if 'user' in locals() and user.pk:
                    user.delete()

    return render(request, 'register.html')


def test_csrf(request):
    """Test CSRF functionality"""
    return render(request, 'test_csrf.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('login')


@login_required
def profile_view(request):
    """个人中心页面，包含个人信息、账户信息和密码修改"""
    user = request.user

    # 获取关联的Person对象，如果不存在则创建
    try:
        person = user.person_profile
    except Person.DoesNotExist:
        # 如果Person不存在，创建一个空的Person对象关联到用户
        person = Person.objects.create(user=user, name=user.username)

    # 获取提醒设置
    try:
        reminder_settings = user.reminder_settings
    except ReminderSetting.DoesNotExist:
        reminder_settings = ReminderSetting.objects.create(user=user)

    # 初始化表单
    person_form = PersonProfileForm(instance=person, prefix='person')
    user_form = UserProfileForm(instance=user, prefix='user')
    password_form = CustomPasswordChangeForm(user=user, prefix='password')

    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')

        if form_type == 'profile_person':
            # 处理个人信息表单
            person_form = PersonProfileForm(request.POST, instance=person, prefix='person')
            if person_form.is_valid():
                person_form.save()
                messages.success(request, '个人信息已更新')
                return redirect('profile')
            else:
                messages.error(request, '请修正个人信息表单中的错误')

        elif form_type == 'profile_user':
            # 处理账户信息表单（邮箱）
            user_form = UserProfileForm(request.POST, instance=user, prefix='user')
            if user_form.is_valid():
                user_form.save()
                messages.success(request, '账户信息已更新')
                return redirect('profile')
            else:
                messages.error(request, '请修正账户信息表单中的错误')

        elif form_type == 'password':
            # 处理密码修改表单
            password_form = CustomPasswordChangeForm(user=user, data=request.POST, prefix='password')
            if password_form.is_valid():
                password_form.save()
                # 重要：更新会话认证哈希，保持用户登录状态
                update_session_auth_hash(request, password_form.user)
                messages.success(request, '密码已成功修改')
                return redirect('profile')
            else:
                messages.error(request, '请修正密码修改表单中的错误')

    # 渲染模板
    context = {
        'person': person,
        'user': user,
        'reminder_settings': reminder_settings,
        'person_form': person_form,
        'user_form': user_form,
        'password_form': password_form,
    }

    return render(request, 'profile.html', context)


@login_required
def departments(request):
    """部门列表"""
    qs = Department.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    department_stats = {
        'total': qs.count(),
    }

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    department_list = paginator.get_page(page_number)

    return render(
        request,
        'meeting-system-departments.html',
        {
            'department_list': department_list,
            'department_stats': department_stats,
        },
    )


@login_required
def department_create(request):
    """创建部门"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '部门已添加。')
            return redirect('departments')
    else:
        form = DepartmentForm()

    return render(request, 'department_create.html', {'form': form})


@login_required
def department_edit(request, pk):
    """编辑部门"""
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, '部门信息已更新。')
            return redirect('departments')
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'department_edit.html', {'form': form, 'department': department})


@login_required
def department_delete(request, pk):
    """删除部门"""
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        # 检查是否有人员关联此部门
        person_count = Person.objects.filter(department=department).count()
        if person_count > 0:
            messages.error(request, f'无法删除该部门，因为仍有 {person_count} 名人员属于此部门。')
            return redirect('departments')

        department.delete()
        messages.success(request, '部门已删除。')
        return redirect('departments')

    return render(request, 'department_delete.html', {'department': department})


# ====== 部门管理 API ======
def api_department_create(request):
    """创建新部门"""
    data, error_response = _parse_json_request(request)
    if error_response:
        return error_response
    return _save_form_json_response(DepartmentForm(data))


def api_department_detail(request, pk):
    """获取部门详情"""
    department = get_object_or_404(Department, pk=pk)
    return JsonResponse({
        'id': department.id,
        'name': department.name,
        'description': department.description or '',
    })


def api_department_update(request, pk):
    """更新部门信息"""
    department = get_object_or_404(Department, pk=pk)
    data, error_response = _parse_json_request(request)
    if error_response:
        return error_response
    return _save_form_json_response(DepartmentForm(data, instance=department))


@require_POST
def api_department_delete(request, pk):
    """删除部门（API版）"""
    department = get_object_or_404(Department, pk=pk)
    # 检查是否有人员关联此部门
    person_count = Person.objects.filter(department=department).count()
    if person_count > 0:
        return JsonResponse({
            'ok': False,
            'errors': {'_': [f'无法删除该部门，因为仍有 {person_count} 名人员属于此部门。']}
        }, status=400)
    department.delete()
    return JsonResponse({'ok': True})
