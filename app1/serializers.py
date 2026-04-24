from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Department, Meeting, Person


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


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

    class Meta:
        model = Meeting
        fields = [
            'id',
            'title',
            'organizer',
            'organizer_name',
            'start_time',
            'end_time',
            'location',
            'attendee_count',
            'status',
            'status_label',
            'status_badge_class',
            'description',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': '结束时间必须晚于开始时间。'})

        return attrs


class UserSerializer(serializers.ModelSerializer):
    person_id = serializers.IntegerField(source='person_profile.id', read_only=True)
    name = serializers.CharField(source='person_profile.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'person_id', 'name']
