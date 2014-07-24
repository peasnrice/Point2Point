from django.db import models

# Create your models here.

class transaction(models.Model):
	completed = models.BooleanField(default=False)
	