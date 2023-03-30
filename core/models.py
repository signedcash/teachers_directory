import os
from django.db import models


class Subject(models.Model):
    """
    Subject model
    """
    name = models.CharField("Subject Name", max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"



class Teacher(models.Model):
    """
    School teacher model.
    """
    first_name = models.CharField("First Name", max_length=100)
    last_name = models.CharField("Last Name", max_length=100)
    profile_picture = models.ImageField("Profile Picture", upload_to='profile_pictures/', blank=True, null=True)
    email_address = models.EmailField("Email Address", unique=True)
    phone_number = models.CharField("Phone Number", max_length=20)
    room_number = models.CharField("Room Number", max_length=10)
    subjects_taught = models.ManyToManyField(
            Subject,
            related_name="teachers",
            verbose_name="Subjects Taught",
            blank=True,
        )


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        ordering = ['last_name', 'first_name']


