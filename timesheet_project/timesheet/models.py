from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    punch_in = models.DateTimeField()
    punch_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    work_status = models.CharField(max_length=50, default='Working')
    comment = models.TextField(blank=True, null=True)

    @property
    def duration(self):
        """Calculate duration between punch_in and punch_out."""
        if self.punch_in and self.punch_out:
            return self.punch_out - self.punch_in
        return None

    @property
    def hours(self):
        """Get hours worked."""
        if self.punch_in and self.punch_out:
            return (self.punch_out - self.punch_in).seconds // 3600
        return 0

    @property
    def minutes(self):
        """Get minutes worked."""
        if self.punch_in and self.punch_out:
            return (self.punch_out - self.punch_in).seconds // 60 % 60
        return 0

    def __str__(self):
        return f"{self.employee.name} - {self.date}"
