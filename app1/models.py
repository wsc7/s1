
from pathlib import Path

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Department(models.Model):
    """部门"""

    name = models.CharField('部门名称', max_length=100, unique=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = '部门'
        verbose_name_plural = '部门'

    def __str__(self):
        return self.name


class Person(models.Model):
    """人员（与人员管理页字段对应）"""

    name = models.CharField('姓名', max_length=100)
    employee_no = models.CharField('工号', max_length=50, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='部门')
    position = models.CharField('职务', max_length=100, blank=True)
    role = models.CharField('角色', max_length=100, blank=True)
    phone = models.CharField('联系方式', max_length=50, blank=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='person_profile',
        verbose_name='关联用户',
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = '人员'
        verbose_name_plural = '人员'

    def __str__(self):
        if self.department:
            return f"{self.name} ({self.department.name})"
        return self.name


class Meeting(models.Model):
    """会议（与会议管理页字段对应）"""

    STATUS_PENDING = 'pending'
    STATUS_APPROVED_PENDING = 'approved_pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'
    STATUS_EXPIRED_CANCELLED = 'expired_cancelled'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, '待审批'),
        (STATUS_APPROVED_PENDING, '审批通过未开始'),
        (STATUS_IN_PROGRESS, '进行中'),
        (STATUS_DONE, '已结束'),
        (STATUS_EXPIRED_CANCELLED, '未审批过期已取消'),
        (STATUS_REJECTED, '审批未通过'),
    ]

    title = models.CharField('会议主题', max_length=200)
    organizer = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_meetings',
        verbose_name='发起人',
    )
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    location = models.CharField('地点', max_length=200, blank=True)
    attendee_count = models.PositiveIntegerField('参会人数', default=0)
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    description = models.TextField('说明', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name = '会议'
        verbose_name_plural = '会议'

    def __str__(self):
        return self.title

    @property
    def status_badge_class(self):
        return {
            self.STATUS_PENDING: 'warning',
            self.STATUS_APPROVED_PENDING: 'primary',
            self.STATUS_IN_PROGRESS: 'info',
            self.STATUS_DONE: 'success',
            self.STATUS_EXPIRED_CANCELLED: 'default',
            self.STATUS_REJECTED: 'danger',
        }.get(self.status, 'default')

    def refresh_status(self, now=None):
        now = now or timezone.now()
        next_status = self.status

        if self.status == self.STATUS_PENDING and now >= self.start_time:
            next_status = self.STATUS_EXPIRED_CANCELLED
        elif self.status == self.STATUS_APPROVED_PENDING:
            if now >= self.end_time:
                next_status = self.STATUS_DONE
            elif now >= self.start_time:
                next_status = self.STATUS_IN_PROGRESS
        elif self.status == self.STATUS_IN_PROGRESS and now >= self.end_time:
            next_status = self.STATUS_DONE

        if next_status != self.status:
            self.status = next_status
            self.save(update_fields=['status', 'updated_at'])

        return self.status

    @classmethod
    def refresh_all_statuses(cls, now=None):
        now = now or timezone.now()
        meetings = list(cls.objects.filter(status__in=[
            cls.STATUS_PENDING,
            cls.STATUS_APPROVED_PENDING,
            cls.STATUS_IN_PROGRESS,
        ]))
        for meeting in meetings:
            meeting.refresh_status(now=now)


class MeetingAttendee(models.Model):
    """会议参与人"""

    RESPONSE_PENDING = 'pending'
    RESPONSE_ACCEPTED = 'accepted'
    RESPONSE_DECLINED = 'declined'
    RESPONSE_CHOICES = [
        (RESPONSE_PENDING, '待回复'),
        (RESPONSE_ACCEPTED, '已接受'),
        (RESPONSE_DECLINED, '已拒绝'),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='attendees',
        verbose_name='会议',
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='meeting_attendances',
        verbose_name='参与人',
    )
    response = models.CharField(
        '回复状态',
        max_length=20,
        choices=RESPONSE_CHOICES,
        default=RESPONSE_PENDING,
    )
    response_time = models.DateTimeField('回复时间', null=True, blank=True)
    is_required = models.BooleanField('必须参加', default=True)
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='添加人',
    )
    added_at = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        unique_together = ['meeting', 'person']
        ordering = ['-added_at']
        verbose_name = '会议参与人'
        verbose_name_plural = '会议参与人'

    def __str__(self):
        return f"{self.person.name} - {self.meeting.title}"


class MeetingAttachment(models.Model):
    """会议附件"""

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='会议',
    )
    file = models.FileField('附件', upload_to='meeting_attachments/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='上传人',
    )
    created_at = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '会议附件'
        verbose_name_plural = '会议附件'

    @property
    def filename(self):
        return Path(self.file.name).name

    def __str__(self):
        return self.filename


class MeetingAgendaItem(models.Model):
    """会议事项"""

    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_FINISHED = 'finished'
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, '未开始'),
        (STATUS_IN_PROGRESS, '进行中'),
        (STATUS_FINISHED, '已结束'),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='agenda_items',
        verbose_name='会议',
    )
    title = models.CharField('事项', max_length=200)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STARTED,
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['start_time', 'id']
        verbose_name = '会议事项'
        verbose_name_plural = '会议事项'

    def __str__(self):
        return self.title


class MeetingAgendaItemAssignee(models.Model):
    """会议事项完成人员"""

    agenda_item = models.ForeignKey(
        MeetingAgendaItem,
        on_delete=models.CASCADE,
        related_name='assignees',
        verbose_name='会议事项',
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='agenda_item_assignments',
        verbose_name='人员',
    )
    is_completed = models.BooleanField('是否完成', default=False)

    class Meta:
        unique_together = ['agenda_item', 'person']
        ordering = ['person__name']
        verbose_name = '会议事项人员'
        verbose_name_plural = '会议事项人员'

    def __str__(self):
        return f"{self.agenda_item.title} - {self.person.name}"


class Notification(models.Model):
    """通知消息"""

    TYPE_MEETING_INVITATION = 'invitation'
    TYPE_MEETING_REMINDER = 'reminder'
    TYPE_MEETING_UPDATE = 'update'
    TYPE_MEETING_CANCELLATION = 'cancellation'
    TYPE_CHOICES = [
        (TYPE_MEETING_INVITATION, '会议邀请'),
        (TYPE_MEETING_REMINDER, '会议提醒'),
        (TYPE_MEETING_UPDATE, '会议更新'),
        (TYPE_MEETING_CANCELLATION, '会议取消'),
    ]

    STATUS_UNREAD = 'unread'
    STATUS_READ = 'read'
    STATUS_DISMISSED = 'dismissed'
    STATUS_CHOICES = [
        (STATUS_UNREAD, '未读'),
        (STATUS_READ, '已读'),
        (STATUS_DISMISSED, '已忽略'),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收人',
    )
    notification_type = models.CharField(
        '通知类型',
        max_length=30,
        choices=TYPE_CHOICES,
    )
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='相关会议',
    )
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_UNREAD,
    )
    scheduled_time = models.DateTimeField('计划发送时间', null=True, blank=True)
    sent_time = models.DateTimeField('实际发送时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '通知'
        verbose_name_plural = '通知'

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.recipient.username}"


class ReminderSetting(models.Model):
    """提醒设置"""

    REMINDER_EMAIL = 'email'
    REMINDER_IN_APP = 'in_app'
    REMINDER_SMS = 'sms'
    REMINDER_CHOICES = [
        (REMINDER_EMAIL, '邮件'),
        (REMINDER_IN_APP, '应用内'),
        (REMINDER_SMS, '短信'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='reminder_settings',
        verbose_name='用户',
    )
    reminder_methods = models.JSONField('提醒方式', default=list)
    default_reminder_minutes = models.JSONField('默认提前时间(分钟)', default=list)
    email_notifications = models.BooleanField('邮件通知', default=True)
    in_app_notifications = models.BooleanField('应用内通知', default=True)
    sms_notifications = models.BooleanField('短信通知', default=False)
    quiet_hours_start = models.TimeField('免打扰开始时间', null=True, blank=True)
    quiet_hours_end = models.TimeField('免打扰结束时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '提醒设置'
        verbose_name_plural = '提醒设置'

    def __str__(self):
        return f"{self.user.username}的提醒设置"
