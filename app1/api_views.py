from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .forms import CustomPasswordChangeForm

from .models import (
    Department,
    Meeting,
    MeetingAgendaItem,
    MeetingAgendaItemAssignee,
    MeetingAttachment,
    MeetingAttendee,
    Notification,
    Person,
    ReminderSetting,
)
from .serializers import (
    DepartmentSerializer,
    MeetingAgendaItemSerializer,
    MeetingAttachmentSerializer,
    MeetingAttendeeSerializer,
    MeetingSerializer,
    PersonSerializer,
    UserSerializer,
    format_datetime,
)


class OptionalPageSizePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        email = (request.data.get('email') or '').strip()
        password1 = (request.data.get('password1') or '').strip()
        password2 = (request.data.get('password2') or '').strip()
        name = (request.data.get('name') or '').strip()
        employee_no = (request.data.get('employee_no') or '').strip()
        department = (request.data.get('department') or '').strip()

        if not username or not password1 or not password2 or not name:
            return Response({'detail': '请填写所有必填字段'}, status=status.HTTP_400_BAD_REQUEST)
        if len(username) < 3:
            return Response({'detail': '用户名至少需要3个字符'}, status=status.HTTP_400_BAD_REQUEST)
        if not __import__('re').match(r'^[\w.@+-]+$', username):
            return Response({'detail': '用户名只能包含字母、数字和@/./+/-/_符号'}, status=status.HTTP_400_BAD_REQUEST)
        if len(password1) < 8:
            return Response({'detail': '密码至少需要8个字符'}, status=status.HTTP_400_BAD_REQUEST)
        if password1 != password2:
            return Response({'detail': '两次输入的密码不一致'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'detail': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            department_obj = Department.objects.filter(name=department).first() if department else None
            Person.objects.create(name=name, employee_no=employee_no, department=department_obj, user=user)
            ReminderSetting.objects.get_or_create(
                user=user,
                defaults={
                    'reminder_methods': [ReminderSetting.REMINDER_EMAIL, ReminderSetting.REMINDER_IN_APP],
                    'default_reminder_minutes': [15, 60],
                    'email_notifications': True,
                    'in_app_notifications': True,
                    'sms_notifications': False,
                },
            )
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'detail': f'注册成功！欢迎 {name}',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)
        except Exception as exc:
            if user and user.pk:
                user.delete()
            return Response({'detail': f'注册失败：{exc}'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response({'detail': '用户名和密码不能为空。'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request=request, username=username, password=password)
        if user is None:
            return Response({'detail': '用户名或密码错误。'}, status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
            }
        )


class SessionTokenAPIView(APIView):
    def get(self, request):
        refresh = RefreshToken.for_user(request.user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(request.user).data,
            }
        )


class MeAPIView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class DashboardAPIView(APIView):
    def get(self, request):
        return Response({
            'username': request.user.username or '用户',
            'current_date': timezone.localdate().strftime('%Y-%m-%d'),
            'person_count': Person.objects.count(),
            'meeting_count': Meeting.objects.count(),
        })


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    pagination_class = OptionalPageSizePagination
    queryset = Department.objects.all().order_by('name')

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', self.request.query_params.get('q', '')).strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return queryset

    @action(detail=False, methods=['get'])
    def options(self, request):
        departments = Department.objects.all().order_by('name')
        return Response({'departments': [{'id': department.id, 'name': department.name} for department in departments]})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        person_count = Person.objects.filter(department=instance).count()
        if person_count:
            return Response(
                {'detail': f'无法删除该部门，因为仍有 {person_count} 名人员属于此部门。', 'person_count': person_count},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    pagination_class = OptionalPageSizePagination
    queryset = Person.objects.select_related('department').all().order_by('name')

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        search = params.get('search', params.get('q', '')).strip()
        department_id = params.get('department_id', '').strip()
        department_name = params.get('department', '').strip()
        role = params.get('role', '').strip()

        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(employee_no__icontains=search))
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        elif department_name:
            queryset = queryset.filter(department__name=department_name)
        if role:
            queryset = queryset.filter(role__icontains=role)

        return queryset

    @action(detail=False, methods=['get'])
    def options(self, request):
        departments = Department.objects.all().order_by('name')
        roles = Person.objects.exclude(role='').order_by('role').values_list('role', flat=True).distinct()
        return Response({
            'departments': [{'id': department.id, 'name': department.name} for department in departments],
            'roles': list(roles),
        })


class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    pagination_class = OptionalPageSizePagination
    queryset = Meeting.objects.select_related('organizer', 'organizer__department').all().order_by('-start_time')

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        search = params.get('search', params.get('q', '')).strip()
        status_value = params.get('status', '').strip()
        date_value = params.get('date', '').strip()
        view_type = params.get('view', 'all').strip()

        if self.action == 'list':
            if view_type == 'mine':
                try:
                    queryset = queryset.filter(organizer=self.request.user.person_profile)
                except Person.DoesNotExist:
                    queryset = queryset.none()
            elif params.get('include_drafts') != '1':
                queryset = queryset.exclude(status=Meeting.STATUS_DRAFT)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(organizer__name__icontains=search)
            )
        if status_value:
            queryset = queryset.filter(status=status_value)
        if date_value:
            queryset = queryset.filter(start_time__date=date_value)

        return queryset

    def list(self, request, *args, **kwargs):
        Meeting.refresh_all_statuses()
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.refresh_status()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        meeting = serializer.save()
        if meeting.status == Meeting.STATUS_PENDING:
            self._create_apply_notifications(meeting)

    @action(detail=False, methods=['get'])
    def options(self, request):
        organizers = Person.objects.all().order_by('name')
        return Response({
            'organizers': [{'id': person.id, 'name': person.name} for person in organizers],
            'statuses': [{'value': value, 'label': label} for value, label in Meeting.STATUS_CHOICES],
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        Meeting.refresh_all_statuses()
        all_meetings = Meeting.objects.select_related('organizer').all()
        visible_meetings = all_meetings.exclude(status=Meeting.STATUS_DRAFT)
        view_type = request.query_params.get('view', 'all').strip()

        try:
            mine_stats_source = all_meetings.filter(organizer=request.user.person_profile)
        except Person.DoesNotExist:
            mine_stats_source = Meeting.objects.none()

        if view_type == 'mine':
            return Response({
                'mine_total': mine_stats_source.count(),
                'mine_applied': mine_stats_source.exclude(status=Meeting.STATUS_DRAFT).count(),
                'mine_draft': mine_stats_source.filter(status=Meeting.STATUS_DRAFT).count(),
                'applied_pending': mine_stats_source.filter(status=Meeting.STATUS_PENDING).count(),
                'applied_unapproved': mine_stats_source.filter(status=Meeting.STATUS_REJECTED).count(),
                'applied_approved': mine_stats_source.filter(status__in=[Meeting.STATUS_APPROVED_PENDING, Meeting.STATUS_IN_PROGRESS, Meeting.STATUS_DONE]).count(),
                'applied_expired': mine_stats_source.filter(status=Meeting.STATUS_EXPIRED_CANCELLED).count(),
            })

        return Response({
            'total': visible_meetings.count(),
            'pending': visible_meetings.filter(status=Meeting.STATUS_PENDING).count(),
            'unapproved': visible_meetings.filter(status=Meeting.STATUS_REJECTED).count(),
            'approved': visible_meetings.filter(status__in=[Meeting.STATUS_APPROVED_PENDING, Meeting.STATUS_IN_PROGRESS, Meeting.STATUS_DONE]).count(),
            'expired': visible_meetings.filter(status=Meeting.STATUS_EXPIRED_CANCELLED).count(),
            'approved_pending': visible_meetings.filter(status=Meeting.STATUS_APPROVED_PENDING).count(),
            'in_progress': visible_meetings.filter(status=Meeting.STATUS_IN_PROGRESS).count(),
            'done': visible_meetings.filter(status=Meeting.STATUS_DONE).count(),
        })

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        meeting = self.get_object()
        if meeting.status not in (Meeting.STATUS_DRAFT, Meeting.STATUS_REJECTED):
            return Response({'detail': '该会议当前状态不可提交申请。'}, status=status.HTTP_400_BAD_REQUEST)

        meeting.status = Meeting.STATUS_PENDING
        meeting.save(update_fields=['status', 'updated_at'])
        self._create_apply_notifications(meeting)
        return Response(self.get_serializer(meeting).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        meeting = self.get_object()
        action_value = request.data.get('action')
        opinion = (request.data.get('opinion') or '').strip()

        if meeting.status != Meeting.STATUS_PENDING:
            return Response({'detail': '该会议当前状态不可审批。'}, status=status.HTTP_400_BAD_REQUEST)

        if action_value == 'approve':
            meeting.status = Meeting.STATUS_APPROVED_PENDING
            result_text = '已通过'
        elif action_value == 'reject':
            meeting.status = Meeting.STATUS_REJECTED
            result_text = '未通过'
        else:
            return Response({'detail': '无效的审批操作。'}, status=status.HTTP_400_BAD_REQUEST)

        meeting.save(update_fields=['status', 'updated_at'])
        self._create_approval_notification(meeting, result_text, opinion)
        return Response(self.get_serializer(meeting).data)


    @action(detail=True, methods=['get', 'post'])
    def attendees(self, request, pk=None):
        meeting = self.get_object()
        if request.method == 'GET':
            attendees = meeting.attendees.select_related('person', 'person__department').all()
            return Response({
                'results': MeetingAttendeeSerializer(attendees, many=True).data,
                'count': attendees.count(),
            })

        person_ids = request.data.get('attendees') or request.data.get('person_ids') or []
        if not isinstance(person_ids, list):
            return Response({'detail': '请选择参与人。'}, status=status.HTTP_400_BAD_REQUEST)

        is_required = bool(request.data.get('is_required', True))
        added_people = []
        for person_id in person_ids:
            person = get_object_or_404(Person, pk=person_id)
            _, created = MeetingAttendee.objects.get_or_create(
                meeting=meeting,
                person=person,
                defaults={'is_required': is_required, 'added_by': request.user},
            )
            if created:
                added_people.append(person)

        meeting.attendee_count = meeting.attendees.count()
        meeting.save(update_fields=['attendee_count'])
        self._create_invitation_notifications(meeting, added_people)
        return Response({'added_count': len(added_people), 'attendee_count': meeting.attendee_count}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='attendees/batch')
    def attendees_batch(self, request, pk=None):
        meeting = self.get_object()
        action_value = request.data.get('action')
        attendee_ids = request.data.get('attendee_ids') or []
        attendees = MeetingAttendee.objects.filter(id__in=attendee_ids, meeting=meeting)

        if action_value == 'mark_required':
            attendees.update(is_required=True)
        elif action_value == 'mark_optional':
            attendees.update(is_required=False)
        elif action_value == 'batch_remove':
            attendees.delete()
            meeting.attendee_count = meeting.attendees.count()
            meeting.save(update_fields=['attendee_count'])
        else:
            return Response({'detail': '无效的批量操作。'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'ok': True, 'attendee_count': meeting.attendee_count})

    @action(detail=True, methods=['delete'], url_path='attendees/(?P<attendee_id>[^/.]+)')
    def attendee_delete(self, request, pk=None, attendee_id=None):
        meeting = self.get_object()
        attendee = get_object_or_404(MeetingAttendee, pk=attendee_id, meeting=meeting)
        attendee.delete()
        meeting.attendee_count = meeting.attendees.count()
        meeting.save(update_fields=['attendee_count'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get', 'post'])
    def attachments(self, request, pk=None):
        meeting = self.get_object()
        if request.method == 'GET':
            attachments = meeting.attachments.select_related('uploaded_by').all()
            return Response({
                'results': MeetingAttachmentSerializer(attachments, many=True).data,
                'count': attachments.count(),
            })

        serializer = MeetingAttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attachment = serializer.save(meeting=meeting, uploaded_by=request.user)
        return Response(MeetingAttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='attachments/(?P<attachment_id>[^/.]+)')
    def attachment_delete(self, request, pk=None, attachment_id=None):
        meeting = self.get_object()
        attachment = get_object_or_404(MeetingAttachment, pk=attachment_id, meeting=meeting)
        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get', 'post'], url_path='agenda-items')
    def agenda_items(self, request, pk=None):
        meeting = self.get_object()
        if request.method == 'GET':
            agenda_items = meeting.agenda_items.prefetch_related('assignees__person').all()
            return Response({
                'results': MeetingAgendaItemSerializer(agenda_items, many=True).data,
                'count': agenda_items.count(),
                'assignee_options': self._agenda_assignee_options(meeting),
                'statuses': [{'value': value, 'label': label} for value, label in MeetingAgendaItem.STATUS_CHOICES],
            })

        serializer = MeetingAgendaItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agenda_item = serializer.save(meeting=meeting)
        return Response(MeetingAgendaItemSerializer(agenda_item).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch', 'delete'], url_path='agenda-items/(?P<item_id>[^/.]+)')
    def agenda_item_detail(self, request, pk=None, item_id=None):
        meeting = self.get_object()
        agenda_item = get_object_or_404(MeetingAgendaItem, pk=item_id, meeting=meeting)

        if request.method == 'DELETE':
            agenda_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = MeetingAgendaItemSerializer(agenda_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        agenda_item = serializer.save()
        return Response(MeetingAgendaItemSerializer(agenda_item).data)

    @action(detail=True, methods=['patch'], url_path='agenda-assignments/(?P<assignment_id>[^/.]+)')
    def agenda_assignment_detail(self, request, pk=None, assignment_id=None):
        meeting = self.get_object()
        assignment = get_object_or_404(MeetingAgendaItemAssignee, pk=assignment_id, agenda_item__meeting=meeting)
        assignment.is_completed = bool(request.data.get('is_completed'))
        assignment.save(update_fields=['is_completed'])
        return Response({'ok': True})

    def _agenda_assignee_options(self, meeting):
        return [
            {
                'id': attendee.person.id,
                'name': attendee.person.name,
                'department': attendee.person.department.name if attendee.person.department else '',
            }
            for attendee in meeting.attendees.select_related('person', 'person__department').all()
        ]

    def _create_invitation_notifications(self, meeting, attendees):
        Notification.objects.bulk_create([
            Notification(
                recipient=person.user,
                notification_type=Notification.TYPE_MEETING_INVITATION,
                title=f'会议邀请：{meeting.title}',
                content=(
                    f'您被邀请参加以下会议：\n\n'
                    f'会议主题：{meeting.title}\n'
                    f'时间：{meeting.start_time.strftime("%Y-%m-%d %H:%M")} - {meeting.end_time.strftime("%Y-%m-%d %H:%M")}\n'
                    f'地点：{meeting.location}\n'
                    f'发起人：{meeting.organizer.name if meeting.organizer else "未指定"}\n\n'
                    f'请登录系统回复是否参加。'
                ),
                meeting=meeting,
            )
            for person in attendees
            if person.user
        ])

    def _create_apply_notifications(self, meeting):
        organizer_name = meeting.organizer.name if meeting.organizer else '未知'
        start_time_str = meeting.start_time.strftime('%Y-%m-%d %H:%M') if meeting.start_time else '未设置'
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
            for admin in User.objects.filter(is_staff=True)
        ])

    def _create_approval_notification(self,meeting, result_text, opinion):
        organizer = meeting.organizer
        if not organizer or not organizer.user:
            return

        opinion_text = opinion or '无审批意见'
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


class NotificationsAPIView(APIView):
    def get(self, request):
        notifications = request.user.notifications.select_related('meeting').all()
        return Response({
            'unread_count': notifications.filter(status=Notification.STATUS_UNREAD).count(),
            'results': [self._notification_data(notification) for notification in notifications],
        })

    def patch(self, request):
        notification = get_object_or_404(Notification, pk=request.data.get('notification_id'), recipient=request.user)
        action_value = request.data.get('action')
        if action_value == 'mark_read':
            notification.status = Notification.STATUS_READ
            notification.save(update_fields=['status'])
            return Response({'detail': '通知已标记为已读', 'notification': self._notification_data(notification)})
        if action_value == 'dismiss':
            notification.status = Notification.STATUS_DISMISSED
            notification.save(update_fields=['status'])
            return Response({'detail': '通知已忽略', 'notification': self._notification_data(notification)})
        return Response({'detail': '无效的通知操作。'}, status=status.HTTP_400_BAD_REQUEST)

    def _notification_data(self, notification):
        return {
            'id': notification.id,
            'notification_type': notification.notification_type,
            'notification_type_label': notification.get_notification_type_display(),
            'title': notification.title,
            'content': notification.content,
            'status': notification.status,
            'status_label': notification.get_status_display(),
            'created_at_display': format_datetime(notification.created_at),
            'meeting': notification.meeting_id,
            'meeting_title': notification.meeting.title if notification.meeting else '',
        }


class MeetingResponseAPIView(APIView):
    def post(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        attendee = get_object_or_404(MeetingAttendee, meeting=meeting, person__user=request.user)
        response_value = request.data.get('response')
        if response_value not in dict(MeetingAttendee.RESPONSE_CHOICES):
            return Response({'detail': '无效的回复'}, status=status.HTTP_400_BAD_REQUEST)

        attendee.response = response_value
        attendee.response_time = timezone.now()
        attendee.save(update_fields=['response', 'response_time'])
        response_text = dict(MeetingAttendee.RESPONSE_CHOICES)[response_value]
        return Response({'detail': f'您的回复已记录：{response_text}'})


class ReminderSettingsAPIView(APIView):
    def get(self, request):
        reminder_settings, _ = ReminderSetting.objects.get_or_create(user=request.user)
        return Response(self._data(reminder_settings))

    def patch(self, request):
        reminder_settings, _ = ReminderSetting.objects.get_or_create(user=request.user)
        reminder_settings.email_notifications = bool(request.data.get('email_notifications'))
        reminder_settings.in_app_notifications = bool(request.data.get('in_app_notifications'))
        reminder_settings.sms_notifications = bool(request.data.get('sms_notifications'))
        reminder_settings.quiet_hours_start = request.data.get('quiet_hours_start') or None
        reminder_settings.quiet_hours_end = request.data.get('quiet_hours_end') or None
        reminder_settings.save()
        return Response({**self._data(reminder_settings), 'detail': '提醒设置已保存'})

    def _data(self, reminder_settings):
        return {
            'email_notifications': reminder_settings.email_notifications,
            'in_app_notifications': reminder_settings.in_app_notifications,
            'sms_notifications': reminder_settings.sms_notifications,
            'quiet_hours_start': reminder_settings.quiet_hours_start.strftime('%H:%M') if reminder_settings.quiet_hours_start else '',
            'quiet_hours_end': reminder_settings.quiet_hours_end.strftime('%H:%M') if reminder_settings.quiet_hours_end else '',
        }


class ProfileAPIView(APIView):
    def get(self, request):
        person, _ = Person.objects.get_or_create(user=request.user, defaults={'name': request.user.username})
        reminder_settings, _ = ReminderSetting.objects.get_or_create(user=request.user)
        return Response({
            'user': self._user_data(request.user),
            'person': self._person_data(person),
            'reminder_settings': self._reminder_settings_data(reminder_settings),
            'departments': [
                {'id': department.id, 'name': department.name}
                for department in Department.objects.all().order_by('name')
            ],
        })

    def patch(self, request):
        section = request.data.get('section')
        if section == 'person':
            return self._update_person(request)
        if section == 'user':
            return self._update_user(request)
        return Response({'detail': '无效的个人中心操作。'}, status=status.HTTP_400_BAD_REQUEST)

    def _update_person(self, request):
        person, _ = Person.objects.get_or_create(user=request.user, defaults={'name': request.user.username})
        data = request.data
        name = (data.get('name') or '').strip()
        if not name:
            return Response({'name': ['姓名不能为空。']}, status=status.HTTP_400_BAD_REQUEST)

        department_id = data.get('department') or None
        department = None
        if department_id:
            department = get_object_or_404(Department, pk=department_id)

        person.name = name
        person.employee_no = (data.get('employee_no') or '').strip()
        person.department = department
        person.position = (data.get('position') or '').strip()
        person.role = (data.get('role') or '').strip()
        person.phone = (data.get('phone') or '').strip()
        person.save()
        return Response({'person': self._person_data(person), 'detail': '个人信息已更新'})

    def _update_user(self, request):
        request.user.email = (request.data.get('email') or '').strip()
        request.user.save(update_fields=['email'])
        return Response({'user': self._user_data(request.user), 'detail': '账户信息已更新'})

    def _user_data(self, user):
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_joined_display': format_datetime(user.date_joined),
            'last_login_display': format_datetime(user.last_login) or '从未登录',
        }

    def _person_data(self, person):
        return {
            'id': person.id,
            'name': person.name,
            'employee_no': person.employee_no,
            'department': person.department_id,
            'department_name': person.department.name if person.department else '',
            'position': person.position,
            'role': person.role,
            'phone': person.phone,
        }

    def _reminder_settings_data(self, reminder_settings):
        return {
            'email_notifications': reminder_settings.email_notifications,
            'in_app_notifications': reminder_settings.in_app_notifications,
            'sms_notifications': reminder_settings.sms_notifications,
            'quiet_hours_start': reminder_settings.quiet_hours_start.strftime('%H:%M') if reminder_settings.quiet_hours_start else '',
            'quiet_hours_end': reminder_settings.quiet_hours_end.strftime('%H:%M') if reminder_settings.quiet_hours_end else '',
        }


class ProfilePasswordAPIView(APIView):
    def post(self, request):
        form = CustomPasswordChangeForm(user=request.user, data={
            'old_password': request.data.get('old_password', ''),
            'new_password1': request.data.get('new_password1', ''),
            'new_password2': request.data.get('new_password2', ''),
        })
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        form.save()
        update_session_auth_hash(request, form.user)
        return Response({'detail': '密码已成功修改'})


class AppTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
