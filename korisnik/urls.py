from django.urls import path

from . import views

app_name="korisnik"

urlpatterns = [
    path('',views.home,name='home'),
    path('logged/<str:username>/',views.logged,name= 'logged'),
    path('register/',views.register,name='register'),
    path('redirecting/',views.help,name = 'help'),
    path('logged/<str:username>/adding',views.adding, name= 'adding'),
    path('redirecting./',views.helpRegister,name='helpRegister'),
]