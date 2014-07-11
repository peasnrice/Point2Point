from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    game_instances = models.ManyToManyField("quests.GameInstance", blank=True, null=True)
    email_alerts = models.BooleanField(default=False)
    phone_number_verified = models.BooleanField(default=False)
    def __unicode__(self):
        return self.user.username

class ProfilePhoneNumber(models.Model):
	user_profile = models.ForeignKey('UserProfile')
	phone_number = models.CharField(max_length=15)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
