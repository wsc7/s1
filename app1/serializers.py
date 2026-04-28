from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Department,
    Meeting,
    MeetingAgendaItem,
    MeetingAgendaItemAssignee,
    MeetingAttachment,
    MeetingAttendee,
    Person,
)


def format_datetime(value):
    return value.strftime('%Y-%m-%d %H:%M') if value else ''


class DepartmentSerializer(serializers.ModelSerializer):
    created_at_display = serializers.SerializerMethodField()
    updated_at_display = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'created_at_display', 'updated_at_display']

    def get_created_at_display(self, obj):
        return format_datetime(obj.created_at)

    def get_updated_at_display(self, obj):
        return format_datetime(obj.updated_at)


class PersonSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Person
        fields = [
            'id',
            'name',
            'employee_no',
            'department',
            'department_name',
            'position',
            'role',
            'phone',
            'created_at',
        ]


class MeetingSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.name', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    status_badge_class = serializers.CharField(read_only=True)
    start_time_display = serializers.SerializerMethodField()
    end_time_display = serializers.SerializerMethodField()
    attachment_count = serializers.IntegerField(source='attachments.count', read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id',
            'title',
            'organizer',
            'organizer_name',
            'start_time',
            'end_time',
            'start_time_display',
            'end_time_display',
            'location',
            'attendee_count',
            'status',
            'status_label',
            'status_badge_class',
            'description',
            'attachment_count',
            'created_at',
            'updated_at',
        ]

    def get_start_time_display(self, obj):
        return format_datetime(obj.start_time)

    def get_end_time_display(self, obj):
        return format_datetime(obj.end_time)

    def validate(self, attrs):
        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': '结束时间必须晚于开始时间。'})

        return attrs


class MeetingAttendeeSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.name', read_only=True)
    person_employee_no = serializers.CharField(source='person.employee_no', read_only=True)
    department_name = serializers.CharField(source='person.department.name', read_only=True, default='')
    response_label = serializers.CharField(source='get_response_display', read_only=True)

    class Meta:
        model = MeetingAttendee
        fields = [
            'id',
            'person',
            'person_name',
            'person_employee_no',
            'department_name',
            'response',
            'response_label',
            'is_required',
            'added_at',
        ]


class MeetingAttachmentSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(read_only=True)
    file_url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True, default='-')
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = MeetingAttachment
        fields = ['id', 'filename', 'file', 'file_url', 'uploaded_by_name', 'created_at', 'created_at_display']
        read_only_fields = ['filename', 'file_url', 'uploaded_by_name', 'created_at', 'created_at_display']

    def get_file_url(self, obj):
        return obj.file.url if obj.file else ''

    def get_created_at_display(self, obj):
        return format_datetime(obj.created_at)


class MeetingAgendaItemAssigneeSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.name', read_only=True)

    class Meta:
        model = MeetingAgendaItemAssignee
        fields = ['id', 'person', 'person_name', 'is_completed']


class MeetingAgendaItemSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    start_time_display = serializers.SerializerMethodField()
    end_time_display = serializers.SerializerMethodField()
    assignees = MeetingAgendaItemAssigneeSerializer(many=True, read_only=True)
    assignee_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = MeetingAgendaItem
        fields = [
            'id',
            'title',
            'start_time',
            'end_time',
            'start_time_display',
            'end_time_display',
            'status',
            'status_label',
            'assignees',
            'assignee_ids',
        ]

    def get_start_time_display(self, obj):
        return format_datetime(obj.start_time)

    def get_end_time_display(self, obj):
        return format_datetime(obj.end_time)

    def validate(self, attrs):
        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        if start_time and end_time and end_time < start_time:
            raise serializers.ValidationError({'end_time': '结束时间不能早于开始时间'})
        return attrs

    def save(self, **kwargs):
        assignee_ids = self.validated_data.pop('assignee_ids', None)
        agenda_item = super().save(**kwargs)
        if assignee_ids is not None:
            existing = {assignment.person_id: assignment for assignment in agenda_item.assignees.all()}
            selected_ids = set(assignee_ids)
            agenda_item.assignees.exclude(person_id__in=selected_ids).delete()
            for person_id in selected_ids:
                if person_id not in existing:
                    MeetingAgendaItemAssignee.objects.create(agenda_item=agenda_item, person_id=person_id)
        return agenda_item


class UserSerializer(serializers.ModelSerializer):
    person_id = serializers.IntegerField(source='person_profile.id', read_only=True)
    name = serializers.CharField(source='person_profile.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'person_id', 'name']
