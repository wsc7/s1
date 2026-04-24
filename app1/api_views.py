from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import Department, Meeting, Person
from .serializers import (
    DepartmentSerializer,
    MeetingSerializer,
    PersonSerializer,
    UserSerializer,
)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response({'detail': '用户名和密码不能为空。'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request=request, username=username, password=password)
        if user is None:
            return Response({'detail': '用户名或密码错误。'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
            }
        )


class MeAPIView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all().order_by('name')

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        person_count = Person.objects.filter(department=instance).count()
        if person_count:
            return Response(
                {'detail': '该部门下仍有关联人员，不能删除。', 'person_count': person_count},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    queryset = Person.objects.select_related('department').all().order_by('name')

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        search = params.get('search', '').strip()
        department_id = params.get('department_id', '').strip()
        role = params.get('role', '').strip()

        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(employee_no__icontains=search))
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if role:
            queryset = queryset.filter(role__icontains=role)

        return queryset


class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.select_related('organizer', 'organizer__department').all().order_by('-start_time')

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        search = params.get('search', '').strip()
        status_value = params.get('status', '').strip()
        date_value = params.get('date', '').strip()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(location__icontains=search)
                | Q(description__icontains=search)
            )
        if status_value:
            queryset = queryset.filter(status=status_value)
        if date_value:
            queryset = queryset.filter(start_time__date=date_value)

        return queryset

    def list(self, request, *args, **kwargs):
        Meeting.refresh_all_statuses()
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.refresh_status()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        meeting = self.get_object()
        action_value = request.data.get('action')

        if action_value == 'approve':
            meeting.status = Meeting.STATUS_APPROVED_PENDING
        elif action_value == 'reject':
            meeting.status = Meeting.STATUS_REJECTED
        else:
            return Response({'detail': '无效的审批动作。'}, status=status.HTTP_400_BAD_REQUEST)

        meeting.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(meeting).data)


class AppTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
