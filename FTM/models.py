from django.db import models
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User,related_name='profile', on_delete=models.CASCADE, null=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    bio = models.TextField(blank=True)
    techstack = models.CharField(max_length=100)
    certificates = models.CharField(max_length=200)
    portfolio = models.URLField(max_length=200)

    def __str__(self):
        return str(self.user)


class WorkExp(models.Model):
    user = models.ForeignKey(Profile, related_name='exp', on_delete=models.CASCADE, null=True)
    company_name = models.CharField(max_length=50)
    manager_name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    work_experience = models.TextField(blank=False)

    def __str__(self):
        return str(self.user)


class Reviews(models.Model):
    user = models.ForeignKey(Profile,related_name='review', on_delete=models.CASCADE, null=True)
    comments = models.TextField(blank=False)
    ratings = models.IntegerField(default=0)
    endorsements = models.CharField(max_length=100)


