import traceback
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from api.models import Task
from api.serializers import (
    RegisterSerializer, LoginSerializer, TaskListSerializer,
    TaskCreateUpdateSerializer, EmployeeTaskStatusSerializer,
)
from api.permissions import IsManager, IsEmployee
from api.tasks import send_error_email_to_admin


def standard_response(message=None, data=None, status_code=200, status_bool=True):
    response_data = {
        "status": status_bool,
        "message": message,
        "data": data if status_bool else None,
    }
    return Response(response_data, status=status_code)

class BaseAPIView(APIView):
    def handle_request(self, request, func):
        try:
            return func()
        except Exception as exc:
            traceback_details = traceback.format_exc()
            exception_type = type(exc).__name__
            exception_message = str(exc)
            url = request.build_absolute_uri()
            user = (
                request.user.username
                if hasattr(request, "user") and request.user.is_authenticated
                else "Anonymous"
            )

            print(f"\n API Error at {url}")
            print(f"User: {user}")
            print(f"Exception: {exception_type} - {exception_message}")
            print(traceback_details)

            send_error_email_to_admin.delay(
                url, user, exception_type, exception_message, traceback_details
            )

            return JsonResponse(
                {
                    "status": False,
                    "message": "Internal Server Error - Admin has been notified.",
                    "data": None,
                },
                status=500,
            )

    def notify_admin_error(self, request, exception_message, exception_type="ValidationError"):
        url = request.build_absolute_uri()
        user = (
            request.user.username
            if hasattr(request, "user") and request.user.is_authenticated
            else "Anonymous"
        )
        traceback_details = "No traceback (manual validation error)"
        send_error_email_to_admin.delay(url, user, exception_type, exception_message, traceback_details)

class RegisterView(BaseAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return self.handle_request(request, lambda: self._process_registration(request))

    def _process_registration(self, request):
        s = RegisterSerializer(data=request.data)
        if s.is_valid():
            user = s.save()
            data = {"id": user.id, "username": user.username, "email": user.email}
            return standard_response("User registered successfully.", data, status.HTTP_201_CREATED)

        error_message = next(iter(s.errors.values()))[0] if s.errors else "Registration failed."
        self.notify_admin_error(request, error_message)
        return standard_response(error_message, None, status.HTTP_400_BAD_REQUEST, False)

class LoginView(BaseAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return self.handle_request(request, lambda: self._process_login(request))

    def _process_login(self, request):
        s = LoginSerializer(data=request.data)
        if s.is_valid():
            return standard_response("Login successful.", s.validated_data, status.HTTP_200_OK)

        error_message = next(iter(s.errors.values()))[0] if s.errors else "Invalid username or password."
        self.notify_admin_error(request, error_message, "AuthenticationError")
        return standard_response(error_message, None, status.HTTP_400_BAD_REQUEST, False)

class ManagerTaskListCreateView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsManager]

    def get(self, request):
        return self.handle_request(request, lambda: self._get_tasks(request))

    def post(self, request):
        return self.handle_request(request, lambda: self._create_task(request))

    def _get_tasks(self, request):
        qs = Task.objects.filter(created_by=request.user)
        serialized = TaskListSerializer(qs, many=True).data
        return standard_response("Tasks fetched successfully.", serialized, status.HTTP_200_OK)

    def _create_task(self, request):
        s = TaskCreateUpdateSerializer(data=request.data)
        if s.is_valid():
            validated_data = s.validated_data
            assigned_users = validated_data.pop("assigned_to", [])
            task = Task.objects.create(created_by=request.user, **validated_data)
            task.assigned_to.set(assigned_users)
            serialized = TaskListSerializer(task).data
            return standard_response("Task created successfully.", serialized, status.HTTP_201_CREATED)

        error_message = next(iter(s.errors.values()))[0] if s.errors else "Task creation failed."
        self.notify_admin_error(request, error_message)
        return standard_response(error_message, None, status.HTTP_400_BAD_REQUEST, False)

class ManagerTaskDetailView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsManager]

    def get(self, request, pk):
        return self.handle_request(request, lambda: self._get_task(request, pk))

    def put(self, request, pk):
        return self.handle_request(request, lambda: self._update_task(request, pk))

    def delete(self, request, pk):
        return self.handle_request(request, lambda: self._delete_task(request, pk))

    def _get_task(self, request, pk):
        task = get_object_or_404(Task, pk=pk, created_by=request.user)
        serialized = TaskListSerializer(task).data
        return standard_response("Task details retrieved successfully.", serialized, status.HTTP_200_OK)

    def _update_task(self, request, pk):
        task = get_object_or_404(Task, pk=pk, created_by=request.user)
        s = TaskCreateUpdateSerializer(task, data=request.data, partial=True)
        if s.is_valid():
            task = s.save()
            serialized = TaskListSerializer(task).data
            return standard_response("Task updated successfully.", serialized, status.HTTP_200_OK)

        error_message = next(iter(s.errors.values()))[0] if s.errors else "Task update failed."
        self.notify_admin_error(request, error_message)
        return standard_response(error_message, None, status.HTTP_400_BAD_REQUEST, False)

    def _delete_task(self, request, pk):
        task = get_object_or_404(Task, pk=pk, created_by=request.user)
        task.delete()
        return standard_response("Task deleted successfully.", None, status.HTTP_204_NO_CONTENT)

class EmployeeMyTasksView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsEmployee]

    def get(self, request):
        return self.handle_request(request, lambda: self._get_my_tasks(request))

    def _get_my_tasks(self, request):
        qs = Task.objects.filter(assigned_to=request.user)
        serialized = TaskListSerializer(qs, many=True).data
        return standard_response("My tasks fetched successfully.", serialized, status.HTTP_200_OK)

class EmployeeTaskStatusUpdateView(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsEmployee]

    def put(self, request, pk):
        return self.handle_request(request, lambda: self._update_status(request, pk))

    def _update_status(self, request, pk):
        task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
        s = EmployeeTaskStatusSerializer(task, data=request.data, partial=True)
        if s.is_valid():
            task = s.save()
            serialized = TaskListSerializer(task).data
            return standard_response("Task status updated successfully.", serialized, status.HTTP_200_OK)

        error_message = next(iter(s.errors.values()))[0] if s.errors else "Status update failed."
        self.notify_admin_error(request, error_message)
        return standard_response(error_message, None, status.HTTP_400_BAD_REQUEST, False)

class TestErrorView(BaseAPIView):
    def get(self, request):
        return self.handle_request(request, lambda: self._test_error(request))

    def _test_error(self, request):
        raise ValueError("This is a test error for admin email alert.")
