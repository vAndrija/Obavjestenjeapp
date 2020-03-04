from django.db import models

# Create your models here.
class Korisnik(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    firstName = models.CharField(max_length=20,default='')
    lastName = models.CharField(max_length = 20,default='')
    email = models.CharField(max_length = 30, default='@')


    def __str__(self):
        return "{}".format(self.username)