from django.contrib import admin

from .models import Meeting, Person, Department, MeetingAgendaItem, MeetingAgendaItemAssignee


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


@admin.register(MeetingAgendaItem)
class MeetingAgendaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting', 'start_time', 'end_time', 'status')
    list_filter = ('status',)
    search_fields = ('title', 'meeting__title')
    raw_id_fields = ('meeting',)


@admin.register(MeetingAgendaItemAssignee)
class MeetingAgendaItemAssigneeAdmin(admin.ModelAdmin):
    list_display = ('agenda_item', 'person', 'is_completed')
    list_filter = ('is_completed',)
    search_fields = ('agenda_item__title', 'person__name')
    raw_id_fields = ('agenda_item', 'person')
