from django.contrib import admin
# Register your models here.
from .models import Korisnik,Stranica,Obavjestenje

admin.site.register(Korisnik)
admin.site.register(Stranica)
admin.site.register(Obavjestenje)
