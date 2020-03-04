from django.contrib import admin
# Register your models here.
from .models import Korisnik,Stranica

admin.site.register(Korisnik)
admin.site.register(Stranica)