from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    competitions = models.ManyToManyField("quests.Competition", blank=True, null=True)
    likes_cheese = models.BooleanField(default=True)
    favourite_hamster_name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.user.username

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
