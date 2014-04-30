from django.db import models
import random
import string

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class PromoCode(models.Model):
    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = id_generator()
        super(PromoCode, self).save(*args, **kwargs)
    promo_type = models.CharField(max_length=32, blank=True, null=True)
    code = models.CharField(max_length=16, blank=True, null=True)
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    valid = models.BooleanField(default=True)
    def __unicode__(self):
        return "phone: " + str(self.phone_number) + " - Code: " + self.code

