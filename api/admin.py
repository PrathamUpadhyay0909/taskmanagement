from django.contrib import admin
from .models import Task, ManagerProfile, EmployeeProfile

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "assigned_to", "created_by", "status", "deadline", "reminder_sent", "created_at")
    list_filter = ("status", "reminder_sent")
    search_fields = ("title", "description", "assigned_to__username", "created_by__username")

admin.site.register(ManagerProfile)
admin.site.register(EmployeeProfile)
