from django.contrib import admin

from .models import Meeting, Person, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_no', 'department', 'position', 'role', 'phone', 'created_at')
    search_fields = ('name', 'employee_no', 'department')


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'location', 'organizer', 'attendee_count', 'status')
    list_filter = ('status',)
    search_fields = ('title', 'location')
    raw_id_fields = ('organizer',)
