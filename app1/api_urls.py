from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import (
    AppTokenRefreshView,
    DashboardAPIView,
    DepartmentViewSet,
    LoginAPIView,
    MeetingViewSet,
    MeAPIView,
    NotificationsAPIView,
    PersonViewSet,
    ProfileAPIView,
    ProfilePasswordAPIView,
    RegisterAPIView,
    ReminderSettingsAPIView,
    SessionTokenAPIView,
    MeetingResponseAPIView,
)

router = DefaultRouter()
router.register('departments', DepartmentViewSet, basename='department')
router.register('people', PersonViewSet, basename='person')
router.register('meetings', MeetingViewSet, basename='meeting')

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('auth/refresh/', AppTokenRefreshView.as_view(), name='token-refresh'),
    path('auth/session-token/', SessionTokenAPIView.as_view(), name='api-session-token'),
    path('auth/me/', MeAPIView.as_view(), name='api-me'),
    path('dashboard/', DashboardAPIView.as_view(), name='api-dashboard'),
    path('profile/', ProfileAPIView.as_view(), name='api-profile'),
    path('profile/password/', ProfilePasswordAPIView.as_view(), name='api-profile-password'),
    path('reminder-settings/', ReminderSettingsAPIView.as_view(), name='api-reminder-settings'),
    path('notifications/', NotificationsAPIView.as_view(), name='api-notifications'),
    path('meetings/<int:meeting_id>/respond/', MeetingResponseAPIView.as_view(), name='api-meeting-respond'),
    path('', include(router.urls)),
]
