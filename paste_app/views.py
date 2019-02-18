import hashlib

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.functions import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.template import loader, Context
from django.urls import reverse

from paste_app.forms import UserForm, UserProfileInfoForm
from paste_app.models import Paste


def main(request):
    prev=request.POST.get('paste','')
    if prev:
        text=prev.encode()
        id=hashlib.md5(text).hexdigest()

        try:
            print("przed paste")
            Paste.objects.get(content=prev,url=id)
            print("po pascie")
        except:
            deleteAfterRead=True if request.POST.get('deleteCheckbox') else False
            if request.user.is_authenticated:
                author=request.user.id
                p=Paste(content=prev,url=id,author=request.user,delete_after_read=deleteAfterRead)
            else:
                p = Paste(content=prev, url=id,delete_after_read=deleteAfterRead)
            p.save()
            print("dodano do bazy")

        prev= 'http://%s/p/%s' % (request.get_host(),id)


    c={
        'previous' : prev
    }

    return render(request,'index.html',c)

def paste(request,url):
    url=request.META.get('PATH_INFO','')[3:]
    #url=get_object_or_404(Paste, id=nr)

    try:
        p=Paste.objects.get(url=url)
    except:
        t=loader.get_template('index.html')
        c={
            'error': "Plik '%s' nie istnieje." % url
        }
        return render(request,'index.html',c)

    toDelete=True if p.delete_after_read and p.delete_timestamp is None else False
    deleted=False if p.delete_timestamp is None else True
    if request.method == "POST":
        p.delete_timestamp=datetime.datetime.now()
        print("w poscie")
    toDelete=True if p.delete_after_read and p.delete_timestamp is None else False
    c={
        'delete_date':p.delete_timestamp,
        'now_date':datetime.datetime.now(),
        'toDelete':toDelete,
        'deleted':deleted,
        'text':p.content,
        'url':p.url
    }
    if request.method == "POST":
        p.content="deleted"
        print("usuniete")
    p.save()
    return render(request,'paste.html',c)
    #return HttpResponse(p.content)

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

@login_required
def moje(request):
    #if request.method=="POST":
    id=request.user.id
    query=Paste.objects.filter(author_id=id)
    c={}
    if not query:
        c={
            'error':'Nie masz żadnych tekstów do wyświetlenia'
        }
    else:
        c={
            'query':query
        }
    return render(request,'my_pastes.html',c)


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            registered = True
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request,'registration.html',
                          {'user_form':user_form,
                           'profile_form':profile_form,
                           'registered':registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'login.html', {})
    else:
        return render(request, 'login.html', {})


#def index(request):
#    return render(request,'index.html')
def delete(request):
    #if (request.GET.get('submit')):
    url = request.POST.get('submit', '')
    Paste.objects.filter(url=url).delete()
    return moje(request)
