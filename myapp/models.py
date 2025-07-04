from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# ✅ PDF file validation function
def validate_pdf(file):
    if not file.name.lower().endswith('.pdf'):
        raise ValidationError("Only PDF files are allowed.")

# ✅ College model
class College(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.department}"  # clearer representation

# ✅ Student model (linked with User)
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"  # more informative

# ✅ Resume model (linked with Student)
class Resume(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='secure_resumes/', validators=[validate_pdf])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username}'s Resume uploaded on {self.uploaded_at.strftime('%Y-%m-%d')}"
