from django.db import models
from django.contrib.auth.models import User


class Pilot(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    year_of_birth = models.IntegerField()
    total_hours = models.IntegerField()
    role = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Ballon(models.Model):
    type = models.CharField(max_length=255)
    manufacturer_name = models.CharField(max_length=255)
    max_passengers = models.IntegerField()

    def __str__(self):
        return f"{self.type} - {self.manufacturer_name}"


class Airways(models.Model):
    name = models.CharField(max_length=255)
    year_founded = models.IntegerField()
    coverage_EU = models.BooleanField()

    def __str__(self):
        return self.name


class AirwaysPilot(models.Model):
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    airways = models.ForeignKey(Airways, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pilot} - {self.airways}"


class Flight(models.Model):
    code = models.CharField(max_length=255)
    takeoff_airport = models.CharField(max_length=255)
    landing_airport = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="flights/", null=True, blank=True)
    ballon = models.ForeignKey(Ballon, on_delete=models.CASCADE)
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE)
    airways = models.ForeignKey(Airways, on_delete=models.CASCADE)

    def __str__(self):
        return self.code
