from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import (
    AppTokenRefreshView,
    DepartmentViewSet,
    LoginAPIView,
    MeetingViewSet,
    MeAPIView,
    PersonViewSet,
)

router = DefaultRouter()
router.register('departments', DepartmentViewSet, basename='department')
router.register('people', PersonViewSet, basename='person')
router.register('meetings', MeetingViewSet, basename='meeting')

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/refresh/', AppTokenRefreshView.as_view(), name='token-refresh'),
    path('auth/me/', MeAPIView.as_view(), name='api-me'),
    path('', include(router.urls)),
]
