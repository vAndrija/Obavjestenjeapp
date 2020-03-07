from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.urls import reverse
# Create your views here.
from .models import Korisnik,Stranica,Obavjestenje
def home(request):
    return render(request,"korisnik/home.html",{})


def adding(request,username):
    objekat=Korisnik.objects.get(username=username)
    objekat.stranica_set.create(link = request.POST['link'])

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
