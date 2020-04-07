from django.db import models
import time
import urllib.request
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
# Create your models here.

from bs4 import BeautifulSoup, Comment
from django.core.mail import send_mail
from django.utils import timezone
from projekat import settings
class Korisnik(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    firstName = models.CharField(max_length=20,default='')
    lastName = models.CharField(max_length = 20,default='')
    email = models.CharField(max_length = 30, default='@')


    def __str__(self):
        return "{}".format(self.username)


class Stranica(models.Model):
    link = models.CharField(max_length=200,default = '')
    korisnik = models.ForeignKey(Korisnik,on_delete=models.CASCADE)
    staroStanje = models.TextField(default='nista')
    def __str__(self):
        return "{}".format(self.link)

class Obavjestenje(models.Model):
    korisnik = models.ForeignKey(Korisnik, on_delete=models.CASCADE)
    naziv = models.CharField(max_length=100)
    sadrzaj = models.CharField(max_length=100)
    datum = models.DateTimeField('vrijeme promjene')
    def __str__(self):
        return "{}".format(self.naziv)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

try:
    # Instantiated scheduler

    scheduler = BackgroundScheduler()
    # Scheduler uses DjangoJobStore()
    scheduler.add_jobstore(DjangoJobStore(), "default")


    # 'cron' mode loop, Monday to Friday, 9:30:10 every day, id is the work ID as a tag
    # ('scheduler',"interval", seconds=1) # cycle with interval, execute once every second
    #@register_job(scheduler, 'interval',seconds=10)
    @scheduler.scheduled_job('interval',seconds=30)
    def test_job():
        print("Pocetka funckije")
        for object in Korisnik.objects.all():
            print("usao u korisnika")
            for stranica in object.stranica_set.all():
                print("usao u straniccu")
                try:
                    html = urllib.request.urlopen(stranica.link)
                except:
                     return
                soup = BeautifulSoup(html, 'html.parser')
                texts = soup.findAll(text=True)
                visible_texts = filter(tag_visible, texts)

                tekst = u" ".join(t.strip() for t in visible_texts)

                if (stranica.staroStanje == 'nista'):
                    stranica.staroStanje = tekst
                    stranica.save()

                elif (stranica.staroStanje != tekst):
                    object.obavjestenje_set.create(naziv="Doslo je do promjene na sajtu", sadrzaj=stranica.link,
                                                     datum=timezone.now())
                    subject = 'Desila se promjena na sajtu'
                    message = ' {} '.format(stranica.link)
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = ["{}".format(object.email), ]
                    send_mail(subject, message, email_from, recipient_list)
                    stranica.staroStanje = tekst
                    stranica.save()

    register_events(scheduler)
# Scheduler starts
    scheduler.start()
except Exception as e:
    print(e)


