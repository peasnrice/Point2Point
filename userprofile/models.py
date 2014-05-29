from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    game_instances = models.ManyToManyField("quests.GameInstance", blank=True, null=True)
    email_alerts = models.BooleanField(default=False)
    def __unicode__(self):
        return self.user.username

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
