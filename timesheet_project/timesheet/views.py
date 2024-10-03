from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Attendance, Employee
from .forms import AttendanceForm, UserRegistrationForm, UserLoginForm
import openpyxl
import datetime
from django.utils.timezone import make_naive

def logout_view(request):
    logout(request)
    return redirect('login')


def attendance_list(request):
    """Display the list of attendance records."""
    attendance_records = Attendance.objects.all()  # Retrieve all attendance records
    return render(request, 'timesheet/attendance_list.html', {'attendance_records': attendance_records})


def add_attendance(request):
    """Add attendance for the logged-in employee."""
    if request.method == 'POST':
        form = AttendanceForm(request.POST)  # Pass the POST data to the form
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.employee = Employee.objects.get(user=request.user)  # Assign the logged-in user's employee
            attendance.save()
            messages.success(request, 'Attendance added successfully!')
            return redirect('attendance_list')
        else:
            messages.error(request, 'Error adding attendance. Please check the form.')
    else:
        form = AttendanceForm()  # Initialize an empty form

    # Retrieve employees associated with the logged-in user
    employees = Employee.objects.filter(user=request.user)
    return render(request, 'attendance/add_attendance.html', {'form': form, 'employees': employees})


def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create the user instance but don't save yet
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()  # Save the user
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('add_attendance')
            else:
                messages.error(request, 'Invalid username or password.')
                print(f'Failed authentication for user: {username}')  # Debug output
        else:
            print(form.errors)  # Print form errors for debugging
    else:
        form = UserLoginForm()

    return render(request, 'timesheet/login.html', {'form': form})


def timesheet_view(request):
    """Display the timesheet for authenticated users."""
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated
    attendance_list = Attendance.objects.all().order_by('-date')  # Get all attendance records
    return render(request, 'timesheet/timesheet.html', {'attendance_list': attendance_list})


def punch_in(request, employee_id):
    """Punch in the employee and create an attendance record."""
    try:
        employee = Employee.objects.get(id=employee_id)
        Attendance.objects.create(employee=employee, punch_in=timezone.now())
        messages.success(request, f'{employee.name} punched in successfully.')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee does not exist.')
    return redirect('timesheet')


def punch_out(request, attendance_id):
    """Punch out the employee and update the attendance record."""
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        if attendance.punch_out is None:
            attendance.punch_out = timezone.now()
            attendance.duration = attendance.punch_out - attendance.punch_in  # Update the duration
            attendance.save()
            messages.success(request, f'{attendance.employee.name} punched out successfully.')
        else:
            messages.warning(request, 'This employee has already punched out.')
    except Attendance.DoesNotExist:
        messages.error(request, 'Attendance record does not exist.')
    return redirect('timesheet')


def generate_report(request, time_period='daily'):
    """Generate and download attendance report based on time period."""
    if time_period == 'daily':
        attendance_records = Attendance.objects.filter(date=datetime.date.today())
        filename = f'Daily_Attendance_{datetime.date.today()}.xlsx'
    elif time_period == 'monthly':
        current_month = timezone.now().month
        current_year = timezone.now().year
        attendance_records = Attendance.objects.filter(date__month=current_month, date__year=current_year)
        filename = f'Monthly_Attendance_{current_month}_{current_year}.xlsx'
    elif time_period == 'yearly':
        current_year = timezone.now().year
        attendance_records = Attendance.objects.filter(date__year=current_year)
        filename = f'Yearly_Attendance_{current_year}.xlsx'
    else:
        messages.error(request, 'Invalid time period specified.')
        return redirect('timesheet')

    # Prepare the response for downloading the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Attendance"
    
    # Define headers based on time period
    if time_period == 'daily':
        ws.append(['Name', 'Company', 'Punch In', 'Punch Out', 'Hours', 'Minutes', 'Duration'])
    else:
        ws.append(['Name', 'Company', 'Date', 'Punch In', 'Punch Out', 'Hours', 'Minutes', 'Duration'])

    for record in attendance_records:
        punch_in_naive = make_naive(record.punch_in) if record.punch_in else None
        punch_out_naive = make_naive(record.punch_out) if record.punch_out else None
        if time_period == 'daily':
            ws.append([record.employee.name, record.employee.company, punch_in_naive, punch_out_naive, record.hours, record.minutes, record.duration])
        else:
            ws.append([record.employee.name, record.employee.company, record.date, punch_in_naive, punch_out_naive, record.hours, record.minutes, record.duration])

    wb.save(response)  # Save the workbook to the response
    return response


# Utility functions for generating specific reports
def generate_daily_report(request):
    """Generate daily attendance report."""
    return generate_report(request, time_period='daily')


def generate_monthly_report(request):
    """Generate monthly attendance report."""
    return generate_report(request, time_period='monthly')


def generate_yearly_report(request):
    """Generate yearly attendance report."""
    return generate_report(request, time_period='yearly')


def some_error_page(request):
    """Render an error page."""
    return render(request, 'error_page.html')
