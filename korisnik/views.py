from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
import urllib.request
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


@background(schedule=10)
def obavjestenje(link,username):
    html = urllib.request.urlopen(link)
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
        print(tekst)
        print("Inicijalo stanje")
    elif (stranica.staroStanje != tekst):
        korisnik.obavjestenje_set.create(naziv="Doslo je do promjene na sajtu",sadrzaj=link,datum=timezone.now())
        subject = 'Desila se promjena na sajtu'
        message = ' {} '.format(link)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['andrijavojnovicpa@gmail.com', ]
        send_mail(subject, message, email_from, recipient_list)
        print("prosao")


def home(request):
    return render(request,"korisnik/home.html",{})


def adding(request,username):
    objekat=Korisnik.objects.get(username=username)
    objekat.stranica_set.create(link = request.POST['link'])
    obavjestenje(request.POST['link'],username, schedule=5,repeat=10)

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



    return render(request,'korisnik/logovan.html',{'username':username,
                                                   'objekat':objekat})

def register(request):
    return render(request,"korisnik/registration.html",{})

def helpRegister(request):
    objekat = Korisnik.objects.create(firstName =request.POST['fname'],
                        lastName = request.POST['lname'],
                        username =request.POST['username'],
                        password = request.POST['pwd'],
                        email = request.POST['email'])
    objekat.save()
    return HttpResponseRedirect(reverse('korisnik:home'))
