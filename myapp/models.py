from django.db import models

# Create your models here.
class Product(models.Model):
    region = models.CharField(max_length=256, default='')
    state = models.CharField(max_length=256, default='')
    village = models.CharField(max_length=256, default='')
    zone = models.CharField(max_length=256, default='')
    price = models.IntegerField(default=0)
    area = models.IntegerField(default=0)
    contract = models.CharField(max_length=256, default='Sale')
    type = models.CharField(max_length=256, default='')
    source = models.CharField(max_length=256, default='')
    year = models.IntegerField(default=0)

    def __unicode__(self):
        return self.region, self.state, self.contract, self.area, self.price, self.year, self.zone

    class Meta:
        verbose_name_plural = "products"


class User(models.Model):
    user_id = models.CharField(max_length=256, default='')
    user_name = models.CharField(max_length=256, default='')
    user_user_name = models.CharField(max_length=256, default='')
    user_email = models.CharField(max_length=256, default='')
    user_phone = models.CharField(max_length=256, default='')
    user_pass =  models.CharField(max_length=256, default='')
