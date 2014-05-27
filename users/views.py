from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from users.forms import UserCreateForm, UserLoginForm
from django.http import HttpResponseRedirect, HttpResponse

def users(request):
    return render_to_response('users/users.html', locals(), context_instance=RequestContext(request))

def signup(request):
    form_su = UserCreateForm(request.POST or None)
    if form_su.is_valid():
        save_user = form_su.save(commit=False)
        save_user.save()
        return render_to_response('home/index.html', locals(), context_instance=RequestContext(request))
    return render_to_response('users/signup.html', locals(), context_instance=RequestContext(request))

def login(request):
    form_l = UserLoginForm(request.POST or None)
    if form_l.is_valid():
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your Point2Point account is disabled")
        else:
            return HttpResponse("We could not find a user matching those credentials")
    else:
        return render_to_response('users/login.html', locals(), context_instance=RequestContext(request))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')
