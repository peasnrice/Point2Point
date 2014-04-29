from django.conf import settings
from django.db import models

class NavBarItem(models.Model):
    # position runs left to right
    pos = models.IntegerField()
    text = models.CharField(max_length=32)
    url = models.CharField(max_length=128)

class IndexJumbotron(models.Model):
    title = models.CharField(max_length=512)
    text = models.CharField(max_length=1024)
    button_text = models.CharField(blank=True, null=True, max_length=32)
    bg_image = models.FileField(blank=True, null=True, upload_to='index')
    image = models.FileField(blank=True, null=True, upload_to='index')

class IndexInfoPiece(models.Model):
    pos = models.IntegerField()
    title = models.CharField(max_length=512)
    body = models.CharField(max_length=1024)
    button_text = models.CharField(blank=True, null=True, max_length=32)
    bg_image = models.FileField(blank=True, null=True, upload_to='index')
    image = models.FileField(blank=True, null=True, upload_to='index')

class Employee(models.Model):
    name = models.CharField(max_length=32)
    position = models.CharField(max_length=32)
    about = models.CharField(max_length=32)
    mug_shot = models.FileField(blank=True, null=True, upload_to='mug_shots')