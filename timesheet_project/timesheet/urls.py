from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    login_view,
    logout_view,
    register,
    add_attendance,
    attendance_list,
    timesheet_view,
    punch_in,
    punch_out,
    generate_daily_report,
    generate_monthly_report,
    generate_yearly_report,
    some_error_page,
)

urlpatterns = [
    # User authentication routes
    path('login/', login_view, name='login'),  # Login page
    path('register/', register, name='register'),  # User registration page

    # Attendance management routes
    path('add_attendance/', add_attendance, name='add_attendance'),  # Add attendance page
    path('logout/', logout_view, name='logout'),
    path('attendance_list/', attendance_list, name='attendance_list'),  # View attendance list
    path('timesheet/', timesheet_view, name='timesheet'),  # Main timesheet page

    # Punch in/out routes
    path('punch_in/<int:employee_id>/', punch_in, name='punch_in'),  # Punch in for an employee
    path('punch_out/<int:attendance_id>/', punch_out, name='punch_out'),  # Punch out for an employee

    # Report generation routes
    path('daily_report/', generate_daily_report, name='daily_report'),  # Daily report
    path('monthly_report/', generate_monthly_report, name='monthly_report'),  # Monthly report
    path('yearly_report/', generate_yearly_report, name='yearly_report'),  # Yearly report

    # Default landing page
    path('', login_view, name='home'),  # Redirect root URL to login view
    path('error/', some_error_page, name='some_error_page'),  # Error page
]
