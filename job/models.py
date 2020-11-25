from ckeditor.fields import RichTextField
from django.db import models
from user.models import User


class JobModel(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Any', 'Any'),
    ]

    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Intern', 'Intern'),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES, null=True, blank=True)
    vacancy = models.CharField(max_length=255, null=True, blank=True)
    responsibilities = RichTextField(null=True, blank=True)
    requirements = RichTextField(null=True, blank=True)
    salary = models.CharField(max_length=255, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES, null=True, blank=True)
    job_desc = models.CharField(max_length=255, null=True, blank=True)
    additional_note = RichTextField(null=True, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.name + " posted " + self.job_title


class AppliedJobModel(models.Model):
    applicant = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    job = models.ForeignKey(JobModel, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.applicant.name + " applied to " + self.job.job_title
