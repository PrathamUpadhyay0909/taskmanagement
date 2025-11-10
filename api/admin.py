from django.contrib import admin
from .models import Task, ManagerProfile, EmployeeProfile

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_assigned_users', 'status', 'deadline', 'created_by', 'created_at')
    list_filter = ('status', 'deadline')
    search_fields = ('title', 'description', 'created_by__username')

    def get_assigned_users(self, obj):
        return ", ".join([user.username for user in obj.assigned_to.all()])
    get_assigned_users.short_description = "Assigned To"


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position')
