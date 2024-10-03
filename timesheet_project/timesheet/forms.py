from django import forms
from django.contrib.auth.models import User
from .models import Attendance, Employee

# Attendance Form
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'punch_in', 'punch_out', 'comment']  # Include comment field
        widgets = {
            'punch_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'punch_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter any comments here...'}),  # Optional placeholder
        }

    def __init__(self, *args, **kwargs):
        # Get the logged-in user from the view and pass it to the form
        logged_in_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter the employee field to show only employees linked to the logged-in user
        if logged_in_user:
            self.fields['employee'].queryset = Employee.objects.filter(user=logged_in_user)

# User Registration Form
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password_confirmation = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirmation']  # Include confirmation in fields

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data  # Return cleaned data for further processing

# User Login Form
class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
