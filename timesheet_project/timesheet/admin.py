from django.contrib import admin
from .models import Employee, Attendance

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0  # Number of empty forms to display

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company')
    inlines = [AttendanceInline]

class AttendanceAdmin(admin.ModelAdmin):
    # Updated list_display to include work_status and comment
    list_display = ('employee', 'punch_in', 'punch_out', 'date', 'duration', 'work_status', 'comment')
    
    # Allow filtering by work_status and date/employee as before
    list_filter = ('date', 'employee', 'work_status')
    
    # Make duration and other fields searchable/read-only
    search_fields = ('employee__name',)
    readonly_fields = ('duration',)

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Attendance, AttendanceAdmin)
