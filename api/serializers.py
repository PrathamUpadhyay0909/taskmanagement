from rest_framework import serializers
from .models import managerProfile, employeeProfile, Task
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=[('manager', 'Manager'), ('employee', 'Employee')], write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(**validated_data)
        if role == 'manager':
            managerProfile.objects.create(user=user)
        else:
            employeeProfile.objects.create(user=user)
        return user

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        raise serializers.ValidationError("Invalid username or password")
    
class managerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = managerProfile
        fields = ['user_id','user', 'department']

class employeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = employeeProfile
        fields = ['user_id','user', 'position']

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']

