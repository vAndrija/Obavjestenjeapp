from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.urls import reverse
# Create your views here.
from .models import Korisnik
def home(request):
    return render(request,"korisnik/home.html",{})



def adding(request,username):
    objekat=Korisnik.objects.get(username=username)
    objekat.stranica_set.create(link = request.POST['link'])
    return HttpResponseRedirect(reverse('korisnik:logged',args=(username,)))

def help(request):
    try:
        username = request.POST['username']
        object = Korisnik.objects.get(username=username)
        if(object.password!=request.POST['pwd']):
            return HttpResponseRedirect(reverse('korisnik:home'))
    except(KeyError, Korisnik.DoesNotExist):
        return HttpResponseRedirect(reverse('korisnik:home'))
    print("andrija")
    return HttpResponseRedirect(reverse('korisnik:logged',args=(object.username,)))

def logged(request,username):
    objekat = Korisnik.objects.get(username =username)
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
