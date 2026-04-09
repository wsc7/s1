"""
URL configuration for s1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from app1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('meetings/', views.meetings, name='meetings'),
    path('meetings/add/', views.meeting_create, name='meeting_create'),
    path('meetings/<int:pk>/', views.meeting_detail, name='meeting_detail'),
    path('meetings/<int:pk>/info/', views.meeting_info, name='meeting_info'),
    path('meetings/<int:pk>/edit/', views.meeting_edit, name='meeting_edit'),
    path('meetings/<int:pk>/attachments/', views.meeting_attachments, name='meeting_attachments'),
    path('meetings/<int:pk>/agenda/', views.meeting_agenda, name='meeting_agenda'),
    path('meetings/<int:pk>/delete/', views.meeting_delete, name='meeting_delete'),
    path('meetings/<int:meeting_id>/agenda/items/<int:item_id>/delete/', views.meeting_agenda_item_delete, name='meeting_agenda_item_delete'),
    path('people/', views.people, name='people'),
    path('people/add/', views.person_create, name='person_create'),
    path('people/<int:pk>/edit/', views.person_edit, name='person_edit'),
    path('people/<int:pk>/delete/', views.person_delete, name='person_delete'),
    # 部门管理
    path('departments/', views.departments, name='departments'),
    path('departments/add/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    path('api/people/create/', views.api_person_create, name='api_person_create'),
    path('api/people/<int:pk>/', views.api_person_detail, name='api_person_detail'),
    path('api/people/<int:pk>/update/', views.api_person_update, name='api_person_update'),
    path('api/meetings/create/', views.api_meeting_create, name='api_meeting_create'),
    path('api/meetings/<int:pk>/approve/', views.api_meeting_approve, name='api_meeting_approve'),
    path('api/meetings/<int:meeting_id>/agenda-items/<int:item_id>/', views.api_meeting_agenda_item_detail, name='api_meeting_agenda_item_detail'),
    path('api/meetings/<int:meeting_id>/agenda-items/<int:item_id>/update/', views.api_meeting_agenda_item_update, name='api_meeting_agenda_item_update'),
    path('api/check-auth/', views.api_check_auth, name='api_check_auth'),
    path('api/departments/', views.api_department_list, name='api_department_list'),
    path('api/departments/create/', views.api_department_create, name='api_department_create'),
    path('api/departments/<int:pk>/', views.api_department_detail, name='api_department_detail'),
    path('api/departments/<int:pk>/update/', views.api_department_update, name='api_department_update'),
    path('api/departments/<int:pk>/delete/', views.api_department_delete, name='api_department_delete'),
    # 会议参与人管理
    path('meetings/<int:meeting_id>/attendees/', views.meeting_attendees, name='meeting_attendees'),
    path('meetings/<int:meeting_id>/attendees/<int:attendee_id>/remove/', views.remove_attendee, name='remove_attendee'),
    path('meetings/<int:meeting_id>/attachments/<int:attachment_id>/remove/', views.remove_attachment, name='remove_attachment'),
    path('meetings/<int:meeting_id>/respond/', views.respond_to_meeting, name='respond_to_meeting'),
    # 通知与提醒
    path('notifications/', views.notifications, name='notifications'),
    path('reminder-settings/', views.reminder_settings, name='reminder_settings'),
    path('profile/', views.profile_view, name='profile'),
    path('send-reminders/', views.send_meeting_reminders, name='send_meeting_reminders'),
    path('test-csrf/', views.test_csrf, name='test_csrf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
