from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from users.forms import UserCreateForm, UserLoginForm
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail

def users(request):
    return render_to_response('users/users.html', locals(), context_instance=RequestContext(request))

def signup(request):
    form_su = UserCreateForm(request.POST or None)
    if form_su.is_valid():
        save_user = form_su.save(commit=False)
        save_user.save()

        subject = "Point To Point Registration Complete!"
        from_email = 'PointToPoint@pointtopoint.webfactional.com'
        body = "Thanks for registering!\n\n"
        body += "You may now login to Point To Point and access your quest history and other various settings\n\n"
        body += "Gracias\n\n"
        body += "~The Point To Point Team"
        to_email = save_user.email
        send_mail(subject, body, from_email,[to_email], fail_silently=False)

        new_user = authenticate(username=request.POST['username'], password=request.POST['password1'])
        auth_login(request, new_user)
        return HttpResponseRedirect("/")
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
                return HttpResponseRedirect('/users/profile')
            else:
                return HttpResponse("Your Point2Point account is disabled")
        else:
            return HttpResponse("We could not find a user matching those credentials")
    else:
        return render_to_response('users/login.html', locals(), context_instance=RequestContext(request))

@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')
