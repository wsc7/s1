from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Meeting, Person, MeetingAttendee, MeetingAttachment, Notification, ReminderSetting, Department


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'employee_no', 'department', 'position', 'role', 'phone']
        labels = {
            'name': '姓名',
            'employee_no': '工号',
            'department': '部门',
            'position': '职务',
            'role': '角色',
            'phone': '联系方式',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'employee_no': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置部门字段的查询集，按名称排序
        self.fields['department'].queryset = Department.objects.all().order_by('name')
        self.fields['department'].empty_label = '— 请选择部门 —'


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'title',
            'organizer',
            'start_time',
            'end_time',
            'location',
            'attendee_count',
            'status',
            'description',
        ]
        labels = {
            'title': '会议主题',
            'organizer': '发起人',
            'start_time': '开始时间',
            'end_time': '结束时间',
            'location': '地点',
            'attendee_count': '参会人数',
            'status': '状态',
            'description': '说明',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'organizer': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'end_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'attendee_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fmts = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
        self.fields['start_time'].input_formats = fmts
        self.fields['end_time'].input_formats = fmts
        self.fields['organizer'].queryset = Person.objects.all().order_by('name')
        self.fields['organizer'].empty_label = '— 未指定 —'


class MeetingAttendeeForm(forms.ModelForm):
    """会议参与人表单"""

    class Meta:
        model = MeetingAttendee
        fields = ['person', 'is_required']
        labels = {
            'person': '参与人',
            'is_required': '必须参加',
        }
        widgets = {
            'person': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        meeting = kwargs.pop('meeting', None)
        super().__init__(*args, **kwargs)
        if meeting:
            # 排除已经是会议组织者的人员
            self.fields['person'].queryset = Person.objects.exclude(
                id=meeting.organizer.id if meeting.organizer else -1
            )


class MeetingAttendeesForm(forms.Form):
    """批量添加会议参与人表单"""

    attendees = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='选择参与人'
    )
    is_required = forms.BooleanField(
        initial=True,
        required=False,
        label='必须参加',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        meeting = kwargs.pop('meeting', None)
        super().__init__(*args, **kwargs)
        if meeting:
            # 只排除会议组织者（如果存在）
            organizer_id = meeting.organizer.id if meeting.organizer else -1
            # 构建查询集：只排除组织者，按部门和姓名排序
            self.fields['attendees'].queryset = Person.objects.exclude(
                id=organizer_id
            ).order_by('department', 'name')


class MeetingAttachmentForm(forms.ModelForm):
    class Meta:
        model = MeetingAttachment
        fields = ['file']
        labels = {
            'file': '附件文件',
        }
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class NotificationForm(forms.ModelForm):
    """通知表单"""

    class Meta:
        model = Notification
        fields = ['recipient', 'notification_type', 'title', 'content', 'scheduled_time']
        labels = {
            'recipient': '接收人',
            'notification_type': '通知类型',
            'title': '标题',
            'content': '内容',
            'scheduled_time': '计划发送时间',
        }
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'notification_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'scheduled_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fmts = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
        self.fields['scheduled_time'].input_formats = fmts


class ReminderSettingForm(forms.ModelForm):
    """提醒设置表单"""

    class Meta:
        model = ReminderSetting
        fields = [
            'email_notifications',
            'in_app_notifications',
            'sms_notifications',
            'quiet_hours_start',
            'quiet_hours_end'
        ]
        labels = {
            'email_notifications': '邮件通知',
            'in_app_notifications': '应用内通知',
            'sms_notifications': '短信通知',
            'quiet_hours_start': '免打扰开始时间',
            'quiet_hours_end': '免打扰结束时间',
        }
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'in_app_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quiet_hours_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'quiet_hours_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class PersonProfileForm(forms.ModelForm):
    """个人资料编辑表单"""
    class Meta:
        model = Person
        fields = ['name', 'employee_no', 'department', 'position', 'role', 'phone']
        labels = {
            'name': '姓名',
            'employee_no': '工号',
            'department': '部门',
            'position': '职务',
            'role': '角色',
            'phone': '联系方式',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'employee_no': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置部门字段的查询集，按名称排序
        self.fields['department'].queryset = Department.objects.all().order_by('name')
        self.fields['department'].empty_label = '— 请选择部门 —'


class UserProfileForm(forms.ModelForm):
    """用户账户信息编辑表单（仅邮箱）"""
    class Meta:
        model = User
        fields = ['email']
        labels = {
            'email': '邮箱地址',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """自定义密码修改表单，添加Bootstrap样式"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为所有字段添加Bootstrap样式
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs.update({'class': 'form-control'})
            if field_name == 'old_password':
                field.label = '当前密码'
            elif field_name == 'new_password1':
                field.label = '新密码'
                field.help_text = '密码至少需要8个字符，不能全是数字'
            elif field_name == 'new_password2':
                field.label = '确认新密码'


class DepartmentForm(forms.ModelForm):
    """部门表单"""

    class Meta:
        model = Department
        fields = ['name', 'description']
        labels = {
            'name': '部门名称',
            'description': '描述',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
