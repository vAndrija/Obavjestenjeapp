import urllib.request

from background_task import background
from background_task import models
from bs4 import BeautifulSoup, Comment
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone


# Create your views here.
from .models import Korisnik, Stranica






def home(request):
    return render(request, "korisnik/home.html", {})




def adding(request, username):
    objekat = Korisnik.objects.get(username=username)
    try:
        staranica = objekat.stranica_set.get(link=request.POST['link'])
        return HttpResponseRedirect(reverse('korisnik:logged', args=(username,)))
    except:
        pass
    objekat.stranica_set.create(link=request.POST['link'])
    stranica = objekat.stranica_set.get(link=request.POST['link'])




    return HttpResponseRedirect(reverse('korisnik:logged', args=(username,)))


def delatingRedirecting(request, username):
    objekat = Korisnik.objects.get(username=username)
    stranice = objekat.stranica_set.all
    context = {
        'objekat': objekat,
        'stranice': stranice,
        'username': username,
    }
    return render(request, 'korisnik/delating.html', context)


def delatingLink(request, username):
    link = request.POST['stranica']
    objekat = Stranica.objects.get(link=link)
    objekat.delete()
    return HttpResponseRedirect(reverse('korisnik:logged', args=(username,)))


def help(request):
    try:
        username = request.POST['username']
        object = Korisnik.objects.get(username=username)
        if (object.password != request.POST['pwd']):
            return HttpResponseRedirect(reverse('korisnik:home'))
    except(KeyError, Korisnik.DoesNotExist):
        return HttpResponseRedirect(reverse('korisnik:home'))
    return HttpResponseRedirect(reverse('korisnik:logged', args=(object.username,)))


def logged(request, username):
    objekat = Korisnik.objects.get(username=username)
    try:
        print(request.META['HTTP_REFERER'])
    except:
        return HttpResponseRedirect(reverse('korisnik:home'))

    lista = objekat.obavjestenje_set.all()[0:5]
    return render(request, 'korisnik/index.html', {'username': username,
                                                   'objekat': objekat,
                                                   'obavjestenja': lista})


def register(request):
    return render(request, "korisnik/registrationa.html", {})


def helpRegister(request):
    try:
        obj = Korisnik.objects.get(username=request.POST['username'])
        print(obj.username)
        return HttpResponseRedirect(reverse('korisnik:register'))
    except:
        objekat = Korisnik.objects.create(firstName=request.POST['fname'],
                                          lastName=request.POST['lname'],
                                          username=request.POST['username'],
                                          password=request.POST['pwd'],
                                          email=request.POST['email'])
        objekat.save()
        return HttpResponseRedirect(reverse('korisnik:home'))
