"""
URL configuration for s1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from app1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('app1.api_urls')),
    path('', views.spa_shell, name='home'),
    path('login/', views.spa_shell, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.spa_shell, name='register'),
    path('meetings/', views.spa_shell, name='meetings'),
    path('people/', views.spa_shell, name='people'),
    path('departments/', views.spa_shell, name='departments'),
    path('meetings/add/', views.spa_shell, name='meeting_create'),
    path('meetings/<int:pk>/', views.spa_shell, name='meeting_detail'),
    path('meetings/<int:pk>/info/', views.spa_shell, name='meeting_info'),
    path('meetings/<int:pk>/edit/', views.spa_shell, name='meeting_edit'),
    path('meetings/<int:pk>/attachments/', views.spa_shell, name='meeting_attachments'),
    path('meetings/<int:pk>/agenda/', views.spa_shell, name='meeting_agenda'),
    path('meetings/<int:pk>/delete/', views.spa_shell, name='meeting_delete'),
    path('meetings/<int:pk>/apply/', views.spa_shell, name='meeting_apply'),
    path('meetings/<int:meeting_id>/agenda/items/<int:item_id>/delete/', views.spa_shell, name='meeting_agenda_item_delete'),
    path('people/add/', views.spa_shell, name='person_create'),
    path('people/<int:pk>/edit/', views.spa_shell, name='person_edit'),
    path('people/<int:pk>/delete/', views.spa_shell, name='person_delete'),
    path('departments/add/', views.spa_shell, name='department_create'),
    path('departments/<int:pk>/edit/', views.spa_shell, name='department_edit'),
    path('departments/<int:pk>/delete/', views.spa_shell, name='department_delete'),
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
    path('meetings/<int:meeting_id>/attendees/', views.spa_shell, name='meeting_attendees'),
    path('meetings/<int:meeting_id>/attendees/<int:attendee_id>/remove/', views.spa_shell, name='remove_attendee'),
    path('meetings/<int:meeting_id>/attachments/<int:attachment_id>/remove/', views.spa_shell, name='remove_attachment'),
    path('meetings/<int:meeting_id>/respond/', views.spa_shell, name='respond_to_meeting'),
    path('notifications/', views.spa_shell, name='notifications'),
    path('reminder-settings/', views.spa_shell, name='reminder_settings'),
    path('profile/', views.spa_shell, name='profile'),
    path('send-reminders/', views.send_meeting_reminders, name='send_meeting_reminders'),
    path('test-csrf/', views.test_csrf, name='test_csrf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
