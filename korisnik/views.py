from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
import urllib.request
from background_task import models
from background_task import background
from bs4 import BeautifulSoup,Comment
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.
from .models import Korisnik,Stranica,Obavjestenje


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def provjera_postojanja(link, username):

    for task in models.Task.objects.all():
        text = "{}".format(task.task_params)
        odvojeni = text.split(",")
        stranica = odvojeni[0].split('"')
        korisnik = odvojeni[1].split('"')
        if(username==korisnik[1] and link==stranica[1]):
            try:
                vlasnik = Korisnik.objects.get(username =korisnik[1])
                try:
                    nadjenaStranica = vlasnik.stranica_set.get(link=stranica[1])
                except:
                    print("Treba da se izbrise")
                    task.delete()
                    return False
            except:
                return False


    return True

@background(schedule=20)
def obavjestenje(link,username):
    povratna = provjera_postojanja(link,username)
    if(not povratna):
        return
    print("Nit je prosla sa {}".format(link))
    try:
        html = urllib.request.urlopen(link)
    except:
        return
    soup = BeautifulSoup(html, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    korisnik = Korisnik.objects.get(username=username)
    tekst=u" ".join(t.strip() for t in visible_texts)
    try:
        stranica = korisnik.stranica_set.get(link=link)
    except:
        return
    if (stranica.staroStanje == 'nista'):
        stranica.staroStanje =tekst
        stranica.save()

    elif (stranica.staroStanje != tekst):
        korisnik.obavjestenje_set.create(naziv="Doslo je do promjene na sajtu",sadrzaj=link,datum=timezone.now())
        subject = 'Desila se promjena na sajtu'
        message = ' {} '.format(link)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ["{}".format(korisnik.email), ]
        send_mail(subject, message, email_from, recipient_list)
        stranica.staroStanje=tekst
        stranica.save()



def home(request):
    return render(request,"korisnik/home.html",{})


def adding(request,username):
    objekat=Korisnik.objects.get(username=username)
    try:
        staranica = objekat.stranica_set.get(link=request.POST['link'])
        return HttpResponseRedirect(reverse('korisnik:logged', args=(username,)))
    except:
        pass
    objekat.stranica_set.create(link = request.POST['link'])
    obavjestenje(request.POST['link'],username,repeat=40)

    return HttpResponseRedirect(reverse('korisnik:logged',args=(username,)))


def delatingRedirecting(request,username):
    objekat = Korisnik.objects.get(username=username)
    stranice = objekat.stranica_set.all
    context = {
        'objekat': objekat,
        'stranice': stranice,
        'username' : username,
    }
    return render(request,'korisnik/delating.html',context)

def delatingLink(request,username):
    link = request.POST['stranica']
    objekat = Stranica.objects.get(link=link)
    objekat.delete()
    return HttpResponseRedirect(reverse('korisnik:logged',args=(username,)))


def help(request):
    try:
        username = request.POST['username']
        object = Korisnik.objects.get(username=username)
        if(object.password!=request.POST['pwd']):
            return HttpResponseRedirect(reverse('korisnik:home'))
    except(KeyError, Korisnik.DoesNotExist):
        return HttpResponseRedirect(reverse('korisnik:home'))
    return HttpResponseRedirect(reverse('korisnik:logged',args=(object.username,)))


def logged(request,username):
    objekat = Korisnik.objects.get(username =username)
    try:
        print(request.META['HTTP_REFERER'])
    except:
        return HttpResponseRedirect(reverse('korisnik:home'))


    lista  = objekat.obavjestenje_set.all()[0:5]
    return render(request,'korisnik/index.html',{'username':username,
                                                   'objekat':objekat,
                                                 'obavjestenja': lista})

def register(request):
    return render(request,"korisnik/registrationa.html",{})

def helpRegister(request):
    try:
        obj = Korisnik.objects.get(username = request.POST['username'])
        print(obj.username)
        return HttpResponseRedirect(reverse('korisnik:register'))
    except:
        objekat = Korisnik.objects.create(firstName =request.POST['fname'],
                            lastName = request.POST['lname'],
                            username =request.POST['username'],
                            password = request.POST['pwd'],
                            email = request.POST['email'])
        objekat.save()
        return HttpResponseRedirect(reverse('korisnik:home'))
