from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import Task
from .serializers import (
    RegisterSerializer, LoginSerializer, TaskListSerializer,
    TaskCreateUpdateSerializer, EmployeeTaskStatusSerializer,
)
from .permissions import IsManager, IsEmployee


def standard_response(message=None, data=None, status_code=200, status_bool=True):
    response_data = {
        "status": status_bool,
        "message": message,
        "data": data if status_bool else None
    }
    return Response(response_data, status=status_code)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if s.is_valid():
            user = s.save()
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
            return standard_response(
                message="User registered successfully.",
                data=user_data,
                status_code=status.HTTP_201_CREATED,
                status_bool=True
            )
        error_message = next(iter(s.errors.values()))[0] if s.errors else "Registration failed."
        return standard_response(
            message=str(error_message),
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            status_bool=False
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        if s.is_valid():
            return standard_response(
                message="Login successful.",
                data=s.validated_data,
                status_code=status.HTTP_200_OK,
                status_bool=True
            )
        error_message = next(iter(s.errors.values()))[0] if s.errors else "Invalid username or password."
        return standard_response(
            message=str(error_message),
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            status_bool=False
        )


class ManagerTaskListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsManager]

    def get(self, request):
        qs = Task.objects.filter(created_by=request.user)
        serialized = TaskListSerializer(qs, many=True).data
        return standard_response(
            message="Tasks fetched successfully.",
            data=serialized,
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        s = TaskCreateUpdateSerializer(data=request.data)
        if s.is_valid():
            # Extract validated data first
            validated_data = s.validated_data
            assigned_users = validated_data.pop("assigned_to", [])

            # Create task manually
            task = Task.objects.create(created_by=request.user, **validated_data)

            # Assign multiple employees to the M2M field
            task.assigned_to.set(assigned_users)
            task.save()

            serialized = TaskListSerializer(task).data
            return standard_response(
                message="Task created successfully.",
                data=serialized,
                status_code=status.HTTP_201_CREATED
            )

        error_message = next(iter(s.errors.values()))[0] if s.errors else "Task creation failed."
        return standard_response(
            message=str(error_message),
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            status_bool=False
        )


class ManagerTaskDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsManager]

    def get_object(self, request, pk):
        return get_object_or_404(Task, pk=pk, created_by=request.user)

    def get(self, request, pk):
        task = self.get_object(request, pk)
        serialized = TaskListSerializer(task).data
        return standard_response(
            message="Task details retrieved successfully.",
            data=serialized,
            status_code=status.HTTP_200_OK
        )

    def put(self, request, pk):
        task = self.get_object(request, pk)
        s = TaskCreateUpdateSerializer(task, data=request.data, partial=True)
        if s.is_valid():
            task = s.save()
            serialized = TaskListSerializer(task).data
            return standard_response(
                message="Task updated successfully.",
                data=serialized,
                status_code=status.HTTP_200_OK
            )
        error_message = next(iter(s.errors.values()))[0] if s.errors else "Task update failed."
        return standard_response(
            message=str(error_message),
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            status_bool=False
        )

    def delete(self, request, pk):
        task = self.get_object(request, pk)
        task.delete()
        return standard_response(
            message="Task deleted successfully.",
            data=None,
            status_code=status.HTTP_204_NO_CONTENT
        )


class EmployeeMyTasksView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsEmployee]

    def get(self, request):
        qs = Task.objects.filter(assigned_to=request.user)
        serialized = TaskListSerializer(qs, many=True).data
        return standard_response(
            message="My tasks fetched successfully.",
            data=serialized,
            status_code=status.HTTP_200_OK
        )


class EmployeeTaskStatusUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsEmployee]

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
        s = EmployeeTaskStatusSerializer(task, data=request.data, partial=True)
        if s.is_valid():
            task = s.save()
            serialized = TaskListSerializer(task).data
            return standard_response(
                message="Task status updated successfully.",
                data=serialized,
                status_code=status.HTTP_200_OK
            )
        error_message = next(iter(s.errors.values()))[0] if s.errors else "Status update failed."
        return standard_response(
            message=str(error_message),
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            status_bool=False
        )
