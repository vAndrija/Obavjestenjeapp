from django.db import models
import time
import urllib.request
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
# Create your models here.
from django_apscheduler.models import DjangoJob
from bs4 import BeautifulSoup, Comment
from django.core.mail import send_mail
from django.utils import timezone
from projekat import settings
from datetime import datetime, timedelta

def default_start_time():
    now = datetime.now()
    start = now.replace(year=2000)
    return start


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
    posljedniMejl = models.DateTimeField(default=default_start_time)
    def __str__(self):
        return "{}".format(self.link)

class Obavjestenje(models.Model):
    korisnik = models.ForeignKey(Korisnik, on_delete=models.CASCADE)
    naziv = models.CharField(max_length=100)
    sadrzaj = models.CharField(max_length=100)
    datum = models.DateTimeField(null=True)
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

    if(len(DjangoJob.objects.all())==0):
        # 'cron' mode loop, Monday to Friday, 9:30:10 every day, id is the work ID as a tag
        # ('scheduler',"interval", seconds=1) # cycle with interval, execute once every second
        #@register_job(scheduler, 'interval',seconds=10)
        @scheduler.scheduled_job('interval',minutes=1)
        def test_job():
            for object in Korisnik.objects.all():
                for stranica in object.stranica_set.all():
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
                        if(stranica.posljedniMejl.year!=2000):

                            brojsekundi = timezone.now()-stranica.posljedniMejl
                            brojminuta  = brojsekundi.total_seconds()/60
                            if(brojminuta<=20):
                                return
                        else :

                            print("Ovo nema obavjestenja jos")
                            pass
                        object.obavjestenje_set.create(naziv="Doslo je do promjene na sajtu", sadrzaj=stranica.link,
                                                         datum=timezone.now())
                        subject = 'Desila se promjena na sajtu'
                        message = ' {} '.format(stranica.link)
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = ["{}".format(object.email), ]
                        send_mail(subject, message, email_from, recipient_list)
                        stranica.staroStanje = tekst
                        stranica.posljedniMejl=timezone.now()
                        stranica.save()

        register_events(scheduler)
    # Scheduler starts
        scheduler.start()
except Exception as e:
    print(e)


