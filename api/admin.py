from django.contrib import admin

from .models import Task, managerProfile, employeeProfile
admin.site.register(Task)
admin.site.register(managerProfile)
admin.site.register(employeeProfile)

class MyTaskView(admin.ModelAdmin):
    list_display = ('id', 'title', 'assigned_to', 'status', 'deadline', 'created_at')
    search_fields = ('title', 'assigned_to__username', 'status')
    list_filter = ('status', 'created_at')
