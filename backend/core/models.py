from django.db import models
from django.contrib.auth.models import User


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CPU(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    socket = models.CharField(max_length=32)
    cores = models.PositiveIntegerField()
    threads = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.manufacturer} {self.name}"


class GPU(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    vram_gb = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.manufacturer} {self.name} {self.vram_gb}GB"


class Build(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="builds")
    name = models.CharField(max_length=120, default="My build")
    cpu = models.ForeignKey(CPU, on_delete=models.PROTECT, null=True, blank=True)
    gpu = models.ForeignKey(GPU, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"
