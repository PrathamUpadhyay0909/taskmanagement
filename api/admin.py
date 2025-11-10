from django.contrib import admin
from .models import Task, ManagerProfile, EmployeeProfile


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'get_assigned_users',
        'status', 'deadline', 'created_by', 'created_at'
    )
    list_filter = ('status', 'deadline')
    search_fields = ('title', 'description', 'created_by__username')

    def get_assigned_users(self, obj):
        return ", ".join([f"{user.id} - {user.username}" for user in obj.assigned_to.all()])
    get_assigned_users.short_description = "Assigned To (ID - Username)"


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_id', 'name', 'get_username', 'department')  
    search_fields = ('name', 'user__username', 'department')

    def get_user_id(self, obj):
        return obj.user.id
    get_user_id.short_description = "User ID"

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_id', 'name', 'get_username', 'position')  
    search_fields = ('name', 'user__username', 'position')

    def get_user_id(self, obj):
        return obj.user.id
    get_user_id.short_description = "User ID"

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"
