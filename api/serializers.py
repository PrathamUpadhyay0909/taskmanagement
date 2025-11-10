from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Task, ManagerProfile, EmployeeProfile, STATUS_CHOICES

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=[('manager', 'Manager'), ('employee', 'Employee')], write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def create(self, validated_data):
        role = validated_data.pop("role")
        user = User.objects.create_user(**validated_data)
        if role == "manager":
            ManagerProfile.objects.create(user=user)
        else:
            EmployeeProfile.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserBasicSerializer(user).data
            }
        raise serializers.ValidationError("Invalid username or password")

class TaskListSerializer(serializers.ModelSerializer):
    assigned_to = UserBasicSerializer(many=True, read_only=True)
    created_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = Task
        fields = "__all__"

class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True
    )

    class Meta:
        model = Task
        fields = ["title", "description", "assigned_to", "deadline", "status", "remark"]

    def validate_assigned_to(self, users):
        for user in users:
            if not hasattr(user, "employee_profile"):
                raise serializers.ValidationError(f"User {user.username} must be an Employee.")
        return users

    def validate_status(self, value):
        valid = [c[0] for c in STATUS_CHOICES]
        if value not in valid:
            raise serializers.ValidationError("Invalid status.")
        return value

class EmployeeTaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["status", "remark"]

class TaskSerializer(serializers.ModelSerializer):
    deadline = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",   
        input_formats=["%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S"]
    )

    class Meta:
        model = Task
        fields = "__all__"

